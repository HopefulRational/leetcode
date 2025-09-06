# Simple Food Delivery App
## Features Required
- User side
  - Browse restaurants, menus
  - Place order (select food, quantity) (here, quantity not handled)
  - Track order (status updates)
- Restaurant side
  - Accept/reject order
  - Update status: Preparing -> Ready -> OutForDelivery -> Delivered
- Delivery side
  - Assign delivery partner by location and availability (strategy)
  - Track delivry partner (mock location updates)
- System side
  - Manage restaurants, menus, orders, delivery agents
  - Notifications (Observer)
  - Payments (Strategy; COD, Online)

## Design Patterns Used
- State -> Order lifecycle states & transitions
- Strategy -> Delivery assignment policy; Payment method (COD/Online)
- Observer -> Notifications on order status changes
- Repository/Service (structural) -> Catalog, OrderService, DeliveryService
- Facade/Orchestrator -> `FoodDeliveryApp` coordinates everything
- Singleton (lightweight) -> `IdGennerator` for IDs 

## Design Highlights
- **Orchestrator** (`FoodDeliveryApp`) provides a clean API: browse, place, accept/reject, update status, assign delivery, track
- **Strict state machine** (`OrderStateMachine`) prevents illegal transitions
- **Pluggable strategies** for payment and delivery assignment
- **Observers** decouple notifications from core flow
- **Repositories/services** isolate data management and domain logic
- **Extensibility**
  - **More states**: `DriverArrivedAtRestaurant`, `PickupFailed` etc.
  - **Richer payments**: refunds, partial captures, retries, 3-DS flows
  - **Invetory & prep times**: per-menu stock, SLA-based assignment
  - **Geo & ETA**: switch to haversine, incorporate live traffic, batching
  - **Persistence**: replace in-memory repos with DB+caching (Redis)
  - **Messaging**: event bus (Kafka) for notifications/analytics
  - **Access control**: roles (User/Restaurant/Agent/Admin), auth tokens
  - 
## Implmentation
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <memory>
#include <functional>
#include <optional>
#include <algorithm>
#include <cassert>
#include <cmath>

using namespace std;

// ---------------- Utilities ----------------
struct Location { int x{0}, y{0}; };
static int dist(const Location& a, const Location& b){
    int dx=a.x-b.x, dy=a.y-b.y; return abs(dx)+abs(dy);
}
struct IdGenerator {
    static string next(const string& prefix) {
        static unordered_map<string,int> ctr;
        return prefix + "-" + to_string(++ctr[prefix]);
    }
};

// ---------------- Notifications (Observer) ----------------
class Observer {
public: virtual ~Observer()=default; virtual void update(const string& msg)=0; };

class ConsoleNotifier : public Observer {
public: void update(const string& msg) override { cout << "[Notify] " << msg << "\n"; }
};

class NotifierBus {
    vector<Observer*> subs;
public:
    void subscribe(Observer* o){ subs.push_back(o); }
    void publish(const string& msg){ for(auto* s: subs) s->update(msg); }
};

// ---------------- Catalog: Restaurant/Menu ----------------
struct MenuItem {
    string id, name; double price;
};
struct Restaurant {
    string id, name; Location loc;
    vector<MenuItem> menu;
    bool acceptsOrders{true};
};

class CatalogRepo {
    unordered_map<string, Restaurant> restaurants;
public:
    string addRestaurant(const string& name, Location loc, vector<MenuItem> menu) {
        string id = IdGenerator::next("R");
        restaurants[id] = Restaurant{id, name, loc, move(menu), true};
        return id;
    }
    optional<Restaurant> get(const string& id) const {
        auto it = restaurants.find(id); if(it==restaurants.end()) return nullopt; return it->second;
    }
    Restaurant* getPtr(const string& id) {
        auto it = restaurants.find(id); if(it==restaurants.end()) return nullptr; return &it->second;
    }
    vector<Restaurant> listAll() const {
        vector<Restaurant> v; v.reserve(restaurants.size());
        for (auto& kv: restaurants) v.push_back(kv.second);
        sort(v.begin(), v.end(), [](auto& a, auto& b){ return a.name < b.name; });
        return v;
    }
};

struct OrderItem { string menuItemId; string name; int qty; double unitPrice; };

// ---------------- Payment (Strategy) ----------------
class PaymentStrategy {
public:
    virtual ~PaymentStrategy()=default;
    virtual bool pay(double amount, const string& orderId)=0;
    virtual string name() const =0;
};
class CODPayment : public PaymentStrategy {
public:
    bool pay(double, const string&) override { return true; }
    string name() const override { return "CashOnDelivery"; }
};
class OnlinePayment : public PaymentStrategy {
public:
    bool pay(double, const string&) override { /* mock gateway */ return true; }
    string name() const override { return "Online"; }
};

// ---------------- Delivery Agents & Assignment (Strategy) ----------------
struct DeliveryAgent {
    string id, name; Location loc; bool available{true}; string currentOrderId;
};

class AssignmentStrategy {
public: virtual ~AssignmentStrategy()=default;
    virtual string chooseAgent(const vector<DeliveryAgent>& agents, const Location& from) = 0;
};

class NearestAvailableStrategy : public AssignmentStrategy {
public:
    string chooseAgent(const vector<DeliveryAgent>& agents, const Location& from) override {
        int best = 1e9; string agentId;
        for (auto& a: agents) if(a.available) {
            int d = dist(a.loc, from);
            if (d < best) { best = d; agentId = a.id; }
        }
        return agentId;
    }
};

class DeliveryRepo {
    unordered_map<string, DeliveryAgent> agents;
public:
    string addAgent(const string& name, Location loc){
        string id = IdGenerator::next("D");
        agents[id] = DeliveryAgent{id, name, loc, true, ""};
        return id;
    }
    DeliveryAgent* getPtr(const string& id){
        auto it=agents.find(id); if(it==agents.end()) return nullptr; return &it->second;
    }
    vector<DeliveryAgent> list() const {
        vector<DeliveryAgent> v; v.reserve(agents.size());
        for (auto& kv: agents) v.push_back(kv.second); return v;
    }
    bool assign(const string& agentId, const string& orderId){
        auto* a = const_cast<DeliveryAgent*>(static_cast<DeliveryRepo*>(this)->getPtr(agentId));
        if(!a || !a->available) return false;
        a->available=false; a->currentOrderId=orderId; return true;
    }
    void complete(const string& agentId, Location newLoc){
        auto* a = getPtr(agentId); if(!a) return; a->available=true; a->currentOrderId.clear(); a->loc=newLoc;
    }
};

// ---------------- Order + State Pattern ----------------
enum class OrderStateKind { Created, Accepted, Preparing, Ready, OutForDelivery, Delivered, Rejected, Cancelled };

struct Order {
    string id, userId, restaurantId;
    vector<OrderItem> items;
    double amount{0};
    OrderStateKind state{OrderStateKind::Created};
    optional<string> deliveryAgentId;
    Location pickup, dropoff;
};

static string stateName(OrderStateKind s){
    switch(s){
        case OrderStateKind::Created: return "Created";
        case OrderStateKind::Accepted: return "Accepted";
        case OrderStateKind::Preparing: return "Preparing";
        case OrderStateKind::Ready: return "Ready";
        case OrderStateKind::OutForDelivery: return "OutForDelivery";
        case OrderStateKind::Delivered: return "Delivered";
        case OrderStateKind::Rejected: return "Rejected";
        case OrderStateKind::Cancelled: return "Cancelled";
    }
    return "?";
}

class OrderRepo {
    unordered_map<string, Order> orders;
public:
    string createOrder(Order o){ string id=IdGenerator::next("O"); o.id=id; orders[id]=move(o); return id; }
    Order* getPtr(const string& id){ auto it=orders.find(id); if(it==orders.end()) return nullptr; return &it->second; }
    vector<Order> listUser(const string& uid) const {
        vector<Order> v; for(auto& kv: orders) if(kv.second.userId==uid) v.push_back(kv.second);
        sort(v.begin(), v.end(), [](auto& a, auto& b){ return a.id<b.id; }); return v;
    }
};

// State guard/transition helper
class OrderStateMachine {
public:
    static bool canTransition(OrderStateKind from, OrderStateKind to){
        switch(from){
            case OrderStateKind::Created: return (to==OrderStateKind::Accepted || to==OrderStateKind::Rejected || to==OrderStateKind::Cancelled);
            case OrderStateKind::Accepted: return (to==OrderStateKind::Preparing || to==OrderStateKind::Cancelled);
            case OrderStateKind::Preparing: return (to==OrderStateKind::Ready);
            case OrderStateKind::Ready: return (to==OrderStateKind::OutForDelivery);
            case OrderStateKind::OutForDelivery: return (to==OrderStateKind::Delivered);
            case OrderStateKind::Delivered: return false;
            case OrderStateKind::Rejected: return false;
            case OrderStateKind::Cancelled: return false;
        }
        return false;
    }
};

// ---------------- Facade / Orchestrator ----------------
class FoodDeliveryApp {
    CatalogRepo catalog;
    OrderRepo orders;
    DeliveryRepo delivery;
    unique_ptr<AssignmentStrategy> assigner;
    NotifierBus notifier;

public:
    FoodDeliveryApp() {
        assigner = make_unique<NearestAvailableStrategy>();
    }

    void addObserver(Observer* obs){ notifier.subscribe(obs); }

    // --- Restaurant & Agents management
    string addRestaurant(const string& name, Location loc, vector<MenuItem> menu){
        return catalog.addRestaurant(name, loc, move(menu));
    }
    string addAgent(const string& name, Location loc){
        return delivery.addAgent(name, loc);
    }

    vector<Restaurant> listRestaurants(){ return catalog.listAll(); }

    // --- User flow: place order
    string placeOrder(const string& userId, const string& restaurantId, const vector<pair<string,int>>& itemReqs, Location userLoc, PaymentStrategy& payment){
        auto ropt = catalog.get(restaurantId);
        if(!ropt || !ropt->acceptsOrders) throw runtime_error("Restaurant not available");
        const auto& r = *ropt;

        Order o;
        o.userId = userId; o.restaurantId = restaurantId; o.pickup = r.loc; o.dropoff = userLoc;

        // build items & price
        unordered_map<string, MenuItem> byId;
        for (auto& mi: r.menu) byId[mi.id]=mi;
        for (auto& req: itemReqs){
            auto it = byId.find(req.first);
            if(it==byId.end()) throw runtime_error("Menu item not found: " + req.first);
            o.items.push_back(OrderItem{it->second.id, it->second.name, req.second, it->second.price});
            o.amount += it->second.price * req.second;
        }

        // take payment (preauth for online / mark COD)
        if(!payment.pay(o.amount, "NA")) throw runtime_error("Payment failed");
        auto oid = orders.createOrder(move(o));
        auto* po = orders.getPtr(oid);
        notifier.publish("Order " + oid + " placed by user " + userId + " at " + r.name + " via " + payment.name() + ", amount " + to_string(po->amount));
        return oid;
    }

    // --- Restaurant actions
    void acceptOrder(const string& orderId){
        auto* o=orders.getPtr(orderId); if(!o) throw runtime_error("order not found");
        transition(*o, OrderStateKind::Accepted);
        notifier.publish("Order " + orderId + " accepted by restaurant");
    }
    void rejectOrder(const string& orderId){
        auto* o=orders.getPtr(orderId); if(!o) throw runtime_error("order not found");
        transition(*o, OrderStateKind::Rejected);
        notifier.publish("Order " + orderId + " rejected by restaurant");
    }
    void updatePreparing(const string& orderId){
        moveTo(orderId, OrderStateKind::Preparing);
    }
    void updateReady(const string& orderId){
        moveTo(orderId, OrderStateKind::Ready);
    }

    // --- Delivery assignment & tracking
    bool assignDelivery(const string& orderId){
        auto* o=orders.getPtr(orderId); if(!o) throw runtime_error("order not found");
        if(o->state != OrderStateKind::Ready) throw runtime_error("order must be Ready to assign");
        auto agents = delivery.list();
        string agentId = assigner->chooseAgent(agents, o->pickup);
        if(agentId.empty()) { notifier.publish("No delivery agent available for order " + orderId); return false; }
        if(!delivery.assign(agentId, orderId)) return false;
        o->deliveryAgentId = agentId;
        transition(*o, OrderStateKind::OutForDelivery);
        notifier.publish("Order " + orderId + " assigned to agent " + agentId);
        return true;
    }
    void markDelivered(const string& orderId){
        auto* o=orders.getPtr(orderId); if(!o) throw runtime_error("order not found");
        if(o->state != OrderStateKind::OutForDelivery) throw runtime_error("not out for delivery");
        transition(*o, OrderStateKind::Delivered);
        // agent becomes free at dropoff
        if(o->deliveryAgentId) delivery.complete(*o->deliveryAgentId, o->dropoff);
        notifier.publish("Order " + orderId + " delivered");
    }

    // --- Querying
    vector<Order> listUserOrders(const string& userId){ return orders.listUser(userId); }
    optional<Order> getOrder(const string& orderId) {
        auto* o=orders.getPtr(orderId); if(!o) return nullopt; return *o;
    }

private:
    void moveTo(const string& orderId, OrderStateKind to){
        auto* o=orders.getPtr(orderId); if(!o) throw runtime_error("order not found");
        transition(*o, to);
        notifier.publish("Order " + orderId + " " + stateName(to));
    }
    static void transition(Order& o, OrderStateKind to){
        if(!OrderStateMachine::canTransition(o.state, to))
            throw runtime_error("illegal order transition " + stateName(o.state) + " -> " + stateName(to));
        o.state = to;
    }
};

// ---------------- Demo ----------------
int main(){
    ConsoleNotifier notifier;
    FoodDeliveryApp app;
    app.addObserver(&notifier);

    // Seed restaurants
    string r1 = app.addRestaurant("SpiceHub", {5,5}, {
        {"M1","Paneer Tikka", 180},
        {"M2","Veg Biryani", 220},
        {"M3","Butter Naan", 40},
    });
    string r2 = app.addRestaurant("BurgerBarn", {1,8}, {
        {"B1","Veg Burger", 120},
        {"B2","Fries", 80},
    });

    // Seed agents
    string d1 = app.addAgent("Ravi", {4,6});
    string d2 = app.addAgent("Meera", {0,9});

    // Browse
    cout << "\n-- Restaurants --\n";
    for (auto& r : app.listRestaurants()){
        cout << r.id << " " << r.name << " at ("<<r.loc.x<<","<<r.loc.y<<") menu:";
        for (auto& m: r.menu) cout << " ["<<m.id<<":"<<m.name<<" ₹"<<m.price<<"]";
        cout << "\n";
    }

    // Place order (user U-1 at location 6,6; pay Online)
    OnlinePayment online;
    string orderId = app.placeOrder("U-1", r1, {{"M1",2}, {"M3",4}}, {6,6}, online);

    // Restaurant flow
    app.acceptOrder(orderId);
    app.updatePreparing(orderId);
    app.updateReady(orderId);

    // Delivery flow
    bool assigned = app.assignDelivery(orderId);
    if(assigned){
        // ... time passes ...
        app.markDelivered(orderId);
    }

    // Track orders
    cout << "\n-- User Orders --\n";
    for (auto& o : app.listUserOrders("U-1")){
        cout << o.id << " amount="<<o.amount<<" state="<<stateName(o.state);
        if(o.deliveryAgentId) cout << " agent="<<*o.deliveryAgentId;
        cout << "\n";
    }
    return 0;
}
```

#### Output
```

-- Restaurants --
R-2 BurgerBarn at (1,8) menu: [B1:Veg Burger Γé╣120] [B2:Fries Γé╣80]
R-1 SpiceHub at (5,5) menu: [M1:Paneer Tikka Γé╣180] [M2:Veg Biryani Γé╣220] [M3:Butter Naan Γé╣40]
[Notify] Order O-1 placed by user U-1 at SpiceHub via Online, amount 520.000000
[Notify] Order O-1 accepted by restaurant
[Notify] Order O-1 Preparing
[Notify] Order O-1 Ready
[Notify] Order O-1 assigned to agent D-1
[Notify] Order O-1 delivered

-- User Orders --
O-1 amount=520 state=Delivered agent=D-1
```
