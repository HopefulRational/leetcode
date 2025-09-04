# Parking Lot Application
## 1. Features Required
- Multiple floors; each floor has multiple parking spots of types: MotorCycle, Car, Truck/Bus, EV
- Spot allocation strategy (e.g., nearest-avalable; pluggable)
- Entry/Exit gates issue and close tickets
- Pricing strategy(hourly/slab based; pluggable)
- Payment (Card/UPI/cash) via strategy; idempotent ticket closing
- Real-time avalability per floor/overall (display board/queries)
- Thread safety for concurrent entry/exit
- Extensibility for new vihicle/spot types or policies

## 2. Design Patterns Used
- Singleton -> `ParkingLot` (shared state)
- Strategy -> `ISpotSelectionStrategy`, `IPricingStrategy`, `IPaymentStrategy`
- Factory -> `ParkingSpotFactory` (create typed spots), optional `VehicleFactory`
- Observer (lightweight) -> `IDisplayObserver` to publish avalability changes
- Facade -> Optional `Gate` to coordinate ticketing with strategies and repositories
- Repository -> In-memory stores for spots and tickets (Clean separation)
- Command/Template (optional) -> For payment flow; we'll keep PAyment Strategy

## 3. Design Highlights
- **Thread Safety**: `shared_mutex` guards the shared `spots` vector; read-heavy operations use shared locks; writes (park/unpark) use unique locks.
- **Race protection**: after strategy selects a spot under shared-lock, we re-check occupancy under exclusive lock.
- **Strategies are pluggable**: `NearestSpotStrategy` can be swapped with `BestFitSpotStrategy`, or swap `HourlyTieredPricing` with slabs/peak pricing. Basically, allocation, pricing and payments are strategy interfaces - easy to extend without changing core logic.
- **Observer**: `ConsoleDisplay` prints updates per change. In production, observers can push to dashboards.
- **Repositories**: `TicketRepository` centralizes persistence; easy to replace with DB-backed impl.

## Solution
```cpp
#include <string>
#include <cmath>
#include <chrono>
#include <optional>
#include <unordered_map>
#include <mutex>
#include <vector>
#include <iostream>
#include <memory>
#include <shared_mutex>
#include <algorithm>
#include <map>

using namespace std;

// ----------- Basic Types -----------
enum class EVehicleType {MotorCycle, Car, Truck, EV };
enum class ESpotType { MotorCycle, Compact, Large, EV };
enum class EPaymentMode { Cash, Card, UPI };
enum class ETicketState { Open, Closed };

// Vehicle {plate, type}
struct Vehicle {
    string plate;
    EVehicleType type;
};

struct Money {
    long long cents{0};
    static Money from_rupees(double r) { return Money{ (long long) llround(r * 100) }; }
    double to_rupees() const { return cents / 100.0; }
    Money& operator+=(const Money &o) { cents += o.cents; return *this; }
    friend Money operator+(Money a, const Money &b) { a+=b; return a; }
};

// ----------- Time Utils -----------
using Clock = chrono::steady_clock;
using TimePoint = Clock::time_point;

static string now_str() {
    auto t = chrono::system_clock::to_time_t(chrono::system_clock::now());
    string s = ctime(&t); if(!s.empty() && s.back() == '\n') s.pop_back();
    return s;
}

// Ids
using ParkingSpotId = int;
using VehiclePlate = string;
using TicketId = string;
using TxnId = string;

// ----------- Parking Spot -----------
struct ParkingSpot {
    ParkingSpotId id;
    int floor;
    ESpotType type;
    bool occupied{false};
    VehiclePlate currentPlate;
};

struct Ticket {
    TicketId ticketId;
    VehiclePlate vehiclePlate;
    EVehicleType vehicleType;
    ParkingSpotId id;
    int floor;
    TimePoint entryTime;
    optional<TimePoint> exitTime;
    ETicketState state{ETicketState::Open};
    Money amount; // final
};

// ----------- Repositories -----------
class TicketRepository {
    unordered_map<TicketId, Ticket> store;
    mutable mutex m;
public:
    string create(Ticket t) {
        lock_guard<mutex> lk(m);
        store[t.ticketId] = move(t);
        return store[t.ticketId].ticketId;
    }
    optional<Ticket> get(const TicketId &id) const {
        lock_guard<mutex> lk(m);
        auto it = store.find(id);
        if(it == store.end()) return nullopt;
        return it->second;
    }
    bool update(const Ticket &t) {
        lock_guard<mutex> lk(m);
        auto it = store.find(t.ticketId);
        if(it == store.end()) return false;
        it->second = t;
        return true;
    }
};

// ----------- Strategies -----------
// Pricing
struct IPricingStrategy {
    virtual ~IPricingStrategy() = default;
    virtual Money compute(EVehicleType type, chrono::minutes dur) const = 0;
};

class HourlyTieredPricing : public IPricingStrategy {
    // simple: per-hour by vehicle type (ceiling to next hour)
    unordered_map<EVehicleType, Money> perHour;
public:
    HourlyTieredPricing() {
        perHour[EVehicleType::MotorCycle] = Money::from_rupees(20);
        perHour[EVehicleType::Car]        = Money::from_rupees(50);
        perHour[EVehicleType::Truck]      = Money::from_rupees(100);
        perHour[EVehicleType::EV]         = Money::from_rupees(60);
    }
    Money compute(EVehicleType vtype, chrono::minutes dur) const override {
        auto hours = (long long)ceil(dur.count() / 60.0);
        if(hours <= 0) hours = 1;
        auto it = perHour.find(vtype);
        Money base = (it != perHour.end()) ? it->second : Money::from_rupees(50);
        Money total{ base.cents * hours };
        return total;
    }
};

// Spot selection (nearest-available by floor order, then spot id)
struct ISpotSelectionStrategy {
    virtual ~ISpotSelectionStrategy() = default;
    virtual optional<ParkingSpotId> selectSpot(const vector<ParkingSpot> &spots, 
                                        EVehicleType vtype,
                                        const vector<int> &floorOrder) = 0;
};

static bool canFit(EVehicleType vtype, ESpotType stype) {
    // basic fit rules
    switch(vtype) {
        case EVehicleType::MotorCycle:  return stype == ESpotType::MotorCycle || stype == ESpotType::Compact || stype == ESpotType::Large;
        case EVehicleType::Car:         return stype == ESpotType::Compact || stype == ESpotType::Large || stype == ESpotType::EV; 
        case EVehicleType::Truck:       return stype == ESpotType::Large;
        case EVehicleType::EV:          return stype == ESpotType::EV || stype == ESpotType::Large;
    }
    return false;
}

class NearestSpotStrategy : public ISpotSelectionStrategy {
public:
    optional<ParkingSpotId> selectSpot(const vector<ParkingSpot> &spots, 
                                EVehicleType vtype,
                                const vector<int> &floorOrder) override {
        for(int f : floorOrder) {
            ParkingSpotId bestId = -1;
            for(auto &s : spots) {
                if(s.floor != f) continue;
                if(!s.occupied && canFit(vtype, s.type)) {
                    if(bestId == -1 || s.id < bestId) bestId = s.id;
                }
            }
            if(bestId != -1) return bestId;
        }
        return nullopt;
    }
};

// Payments {ticketId, mode, amount, success, txnId}
struct PaymentReceipt {
    TicketId ticketId;
    EPaymentMode mode;
    Money amount;
    bool success{false};
    TxnId txnId;
};

struct IPaymentStrategy {
    virtual ~IPaymentStrategy() = default;
    virtual PaymentReceipt pay(const TicketId& ticketId, Money amount, EPaymentMode mode) = 0;
};

class SimplePayment : public IPaymentStrategy {
public:
    PaymentReceipt pay(const TicketId &ticketId, Money amount, EPaymentMode mode) {
        // pretend success for demo; idempotency token could be added here
        PaymentReceipt r;
        r.ticketId = ticketId;
        r.success = true;
        r.txnId = "TXN-" + ticketId + "-" + to_string(rand()%100000);
        return r;
    }
};

// ----------- Observer for Display -----------
struct IDisplayObserver {
    virtual ~IDisplayObserver() = default;
    virtual void onAvailabilityChanged(int floor, ESpotType type, int freeCount) = 0;
};

class ConsoleDisplay : public IDisplayObserver {
public:
    void onAvailabilityChanged(int floor, ESpotType type, int freeCount) {
        auto st = [](ESpotType t){
            switch(t){
                case ESpotType::MotorCycle: return "MotorCycle";
                case ESpotType::Compact:    return "Compact";
                case ESpotType::Large:      return "Large";
                case ESpotType::EV:         return "EV";
            } return "?";
        };
        cout << "[" << now_str() << "] Floor " << floor
             << " | " << st(type) << " free: " << freeCount << "\n";
    }
};

// ----------- Parking Lot -----------
class ParkingLot {
    // core state
    vector<ParkingSpot> spots;                        // all spots
    unordered_map<ParkingSpotId, int> spotIndexById; // spotId -> index in spots
    vector<int> floors;                              // floor order for selection
    vector<IDisplayObserver*> observers;

    unique_ptr<ISpotSelectionStrategy> spotStrategy;
    unique_ptr<IPricingStrategy> pricing;
    unique_ptr<IPaymentStrategy> payment;

    TicketRepository tickets;

    mutable shared_mutex spotsMutex; // allow concurrent reads

    ParkingLot() = default;
public:
    ParkingLot(const ParkingLot &) = delete;
    ParkingLot& operator=(const ParkingLot&) = delete;

    static ParkingLot& getInstance() {
        static ParkingLot instance;
        return instance;
    }

    // configuration
    void configure(unique_ptr<ISpotSelectionStrategy> s,
                   unique_ptr<IPricingStrategy> p,
                   unique_ptr<IPaymentStrategy> pay) {
        spotStrategy = std::move(s);
        pricing      = std::move(p);
        payment      = std::move(pay);
    }

    void addFloor(int floorNo) {
        floors.push_back(floorNo);
        sort(floors.begin(), floors.end());
    }

    ParkingSpotId addSpot(int floor, ESpotType type) {
        static int nextId = 1;
        ParkingSpot s{  .id = nextId++, 
                        .floor = floor, 
                        .type = type, 
                        .occupied = false, 
                        .currentPlate = ""
                    };
        int idx = (int)spots.size();
        spots.push_back(s);
        spotIndexById[s.id] = idx;
        notify(floor, type);
        return s.id;
    }

    // Observer Management
    void addObserver(IDisplayObserver* obs) {
        observers.push_back(obs);
    }

    void notify(int floor, ESpotType type) {
        int freeCount = 0;
        for(auto &s: spots) if(s.floor == floor && !s.occupied && s.type == type) freeCount++;
        for(auto &ob: observers) ob->onAvailabilityChanged(floor, type, freeCount);
    }

    // Entry flow
    optional<TicketId> parkVehicle(const Vehicle &v) {
        /*
            1. select spot using read lock and spotStrategy
            2. update spot using write lock
            3. create ticket
            4. notify observers        
        */
        if(!spotStrategy) return nullopt;
        shared_lock<shared_mutex> rlock(spotsMutex);
        optional<ParkingSpotId> spotId = spotStrategy->selectSpot(spots, v.type, floors);
        rlock.unlock();

        if(!spotId) return nullopt;

        // lock for write to occupy
        unique_lock<shared_mutex> wlock(spotsMutex);
        int idx = spotIndexById[*spotId];
        auto &s = spots[idx];
        if(s.occupied) return nullopt; // race safeguard
        s.occupied = true; s.currentPlate = v.plate;
        wlock.unlock();

        // create ticket
        Ticket t;
        t.ticketId = "T-" + to_string(*spotId) + "-" + to_string(chrono::duration_cast<chrono::milliseconds>(Clock::now().time_since_epoch()).count());
        t.vehiclePlate = v.plate;
        t.vehicleType = v.type;
        t.id = *spotId;
        t.floor = spots[idx].floor;
        t.entryTime = Clock::now();
        tickets.create(t);

        // notify observers
        notify(t.floor, spots[idx].type);
        return t.ticketId;
    }

    // Exit flow
    optional<PaymentReceipt> unparkAndPay(const TicketId &ticketId, EPaymentMode mode) {
        /*
            1. non-existing ticket; already paid - return synthetic receipt
            2. compute duration and amount
            3. payment
            4. free spot
            5. update ticket
            6. notify
        */
        auto tOpt = tickets.get(ticketId);
        if(!tOpt) return nullopt;
        auto t = *tOpt;
        if(t.state == ETicketState::Closed) {
            // already paid; return a synthetic receipt
            PaymentReceipt r{ticketId, mode, t.amount, true, "ALREADY-CLOSED"};
            return r;
        }

        // compute duration and amount
        auto end = Clock::now();
        auto dur = chrono::duration_cast<chrono::minutes>(end - t.entryTime);
        Money amount = pricing ? pricing->compute(t.vehicleType, dur) : Money::from_rupees(50);

        // payment
        auto receipt = payment ? payment->pay(t.ticketId, amount, mode) 
                               : PaymentReceipt{t.ticketId, mode, false, ""};
        if(!receipt.success) return nullopt;

        // free spot
        {
            unique_lock<shared_mutex> wlock(spotsMutex);
            int idx = spotIndexById[t.id];
            auto &s = spots[idx];
            s.occupied = false; s.currentPlate.clear();
        }

        // update ticket
        t.amount = amount;
        t.exitTime = end;
        t.state = ETicketState::Closed;
        tickets.update(t);

        // notify
        notify(t.floor, spots[spotIndexById[t.id]].type);
        return receipt;
    }

    // Queries
    map<ESpotType, int> freeSpotsByFloor(int floor) const {
        map<ESpotType, int> m;
        shared_lock<shared_mutex> rlock(spotsMutex);
        for(auto &s: spots) if(s.floor == floor && !s.occupied) m[s.type]++;
        return m;
    }

    int totalFree() const {
        int cnt = 0;
        shared_lock<shared_mutex> rlock(spotsMutex);
        for(auto &s : spots) if(!s.occupied) cnt++;
        return cnt;
    }
};

// ----------- Demo Main -----------
int main()
 {
    // Build ParkingLot
    auto &lot = ParkingLot::getInstance();
    lot.configure(make_unique<NearestSpotStrategy>(),
                  make_unique<HourlyTieredPricing>(),
                  make_unique<SimplePayment>());
    
    lot.addFloor(0); lot.addFloor(1);

    // Add spots
    for(int i=0; i<5; ++i) lot.addSpot(0, ESpotType::Compact);
    for(int i=0; i<2; ++i) lot.addSpot(0, ESpotType::EV);
    for(int i=0; i<2; ++i) lot.addSpot(0, ESpotType::Large);
    for(int i=0; i<3; ++i) lot.addSpot(1, ESpotType::Compact);
    for(int i=0; i<1; ++i) lot.addSpot(1, ESpotType::Large);

    ConsoleDisplay display;
    lot.addObserver(&display);

    // Park vehicles
    Vehicle v1{"KA01AB1234", EVehicleType::Car};
    Vehicle v2{"KA02ZZ9999", EVehicleType::EV};
    Vehicle v3{"KA03TT7777", EVehicleType::Truck};

    auto t1 = lot.parkVehicle(v1);
    auto t2 = lot.parkVehicle(v2);
    auto t3 = lot.parkVehicle(v3); // may fail if no large spot left

    cout << "Total free after entry: " << lot.totalFree() << "\n";

    // Simulate some time: in real system time passes; here keeping it simple

    if(t1) {
        auto r = lot.unparkAndPay(*t1, EPaymentMode::UPI);
        if(r) cout << "Ticket " << r->ticketId << " pair: Rs " << r->amount.to_rupees()
                   << " via UPI, txn=" << r->txnId << "\n";
    }

    if(t2) {
        auto r = lot.unparkAndPay(*t2, EPaymentMode::Card);
        if(r) cout << "Ticket " << r->ticketId << " pair: Rs " << r->amount.to_rupees()
                   << " via Card, txn=" << r->txnId << "\n";
    }

    cout << "Total free after exit: " << lot.totalFree() << "\n";

    // Floor-wise avalability
    auto f0 = lot.freeSpotsByFloor(0);
    cout << "Floor 0 avalability:\n";
    for(auto &kv: f0) {
        cout << " type=" << (int)kv.first << " free=" << kv.second << "\n";
    }

    return 0;
}
```

#### Output
```
[Thu Sep 04 17:26:49 2025] Floor 0 | Compact free: 4
[Thu Sep 04 17:26:49 2025] Floor 0 | EV free: 1
[Thu Sep 04 17:26:49 2025] Floor 0 | Large free: 1
Total free after entry: 10
[Thu Sep 04 17:26:49 2025] Floor 0 | Compact free: 5
Ticket T-1-757983391 pair: Rs 0 via UPI, txn=TXN-T-1-757983391-41
[Thu Sep 04 17:26:49 2025] Floor 0 | EV free: 2
Ticket T-6-757983393 pair: Rs 0 via Card, txn=TXN-T-6-757983393-18467
Total free after exit: 12
Floor 0 avalability:
 type=1 free=5
 type=2 free=1
 type=3 free=2
```
