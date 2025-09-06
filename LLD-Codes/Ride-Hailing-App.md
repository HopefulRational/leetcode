# Ride Hailing App
## Features Required
- Riders can book a ride
- Drivers can accept/reject ride requests
- Matching system to assign nearest available driver
- Trip management - Start, update status, end trip
- Notifications - Updates to riders and drivers (ride assigned, trip started, completed)
- Payment options - Cash, wallet, Card/UPI

## Design Patterns Used
- Observer -> Notifications to Rider and Driver
- Strategy -> Payment mathods, matching policy (could extend to surge pricing)
- Factory -> Create payment objects
- Singleton -> Cantral `RideManager` to manage riders, drivers, trips

## Design Highlights
- `RideManager` is the orchestrator
- `IMatching` decides which driver to assign
- `TripStatus` maintains state
- `ConsoleObserver` implements Observer
- `IPayment` ensures flexible payment integration

## Implementation
```cpp
#include <bits/stdc++.h>
using namespace std;

// ---------------- Utilities ----------------
struct Location {
    double x = 0, y = 0;
    static double distance(const Location &a, const Location &b) {
        double dx = a.x - b.x, dy = a.y - b.y;
        return sqrt(dx*dx + dy*dy);
    }
    string toString() const {
        char buf[64];
        snprintf(buf, sizeof(buf), "(%.2f,%.2f)", x, y);
        return string(buf);
    }
};

static string genId(const string &prefix) {
    static mutex m;
    static unordered_map<string,int> ctr;
    lock_guard<mutex> lk(m);
    return prefix + "-" + to_string(++ctr[prefix]);
}

static void safePrint(const string &s) {
    static mutex coutM;
    lock_guard<mutex> lk(coutM);
    cout << s << endl;
}

// ---------------- Observer (Notifications) ----------------
struct IObserver {
    virtual ~IObserver()=default;
    virtual void notify(const string &msg) = 0;
};

struct ConsoleObserver : IObserver {
    string who;
    ConsoleObserver(string who_ = ""): who(move(who_)) {}
    void notify(const string &msg) override {
        safePrint("[" + who + "] " + msg);
    }
};

// ---------------- Payment Strategy ----------------
struct IPayment {
    virtual ~IPayment()=default;
    virtual void pay(double amount, const string &tripId) = 0;
    virtual string name() const = 0;
};

struct CashPayment : IPayment {
    void pay(double amount, const string &tripId) override {
        safePrint("[Payment][" + tripId + "] Cash collected: ₹" + to_string(amount));
    }
    string name() const override { return "Cash"; }
};

struct CardPayment : IPayment {
    void pay(double amount, const string &tripId) override {
        safePrint("[Payment][" + tripId + "] Card charged: ₹" + to_string(amount));
    }
    string name() const override { return "Card"; }
};

struct WalletPayment : IPayment {
    void pay(double amount, const string &tripId) override {
        safePrint("[Payment][" + tripId + "] Wallet debited: ₹" + to_string(amount));
    }
    string name() const override { return "Wallet"; }
};

struct PaymentFactory {
    static unique_ptr<IPayment> create(const string &type) {
        if (type == "cash") return make_unique<CashPayment>();
        if (type == "card") return make_unique<CardPayment>();
        if (type == "wallet") return make_unique<WalletPayment>();
        return make_unique<CashPayment>();
    }
};

// ---------------- Rider & Driver ----------------
struct Rider {
    string id;
    unique_ptr<IObserver> obs;
    Rider(): id(genId("R")) { obs = make_unique<ConsoleObserver>("Rider:" + id); }
};

struct Driver {
    string id;
    Location loc;
    bool available = true;
    unique_ptr<IObserver> obs;
    mutex m; // protects driver state (available and loc)
    Driver(Location start = {}): id(genId("D")), loc(start) {
        obs = make_unique<ConsoleObserver>("Driver:" + id);
    }
    void setLocation(const Location &p) {
        lock_guard<mutex> lk(m);
        loc = p;
    }
    Location getLocation() {
        lock_guard<mutex> lk(m);
        return loc;
    }
    bool tryAcquire() {
        lock_guard<mutex> lk(m);
        if (!available) return false;
        available = false;
        return true;
    }
    void release() {
        lock_guard<mutex> lk(m);
        available = true;
    }
};

// ---------------- Matching Strategy ----------------
struct IMatching {
    virtual ~IMatching() = default;
    virtual optional<string> chooseDriver(const vector<shared_ptr<Driver>> &drivers, const Location &pickup) = 0;
};

struct NearestMatching : IMatching {
    optional<string> chooseDriver(const vector<shared_ptr<Driver>> &drivers, const Location &pickup) override {
        double bestDist = numeric_limits<double>::infinity();
        string chosen;
        for (auto &d: drivers) {
            Location loc = d->getLocation();
            // only consider available drivers
            // we check availability inside choose by locking driver
            // getLocation() uses lock internally; now check their availability via tryAcquireCandidate
            // To avoid consuming the driver here, we only inspect available flag via a temporary lock:
            {
                lock_guard<mutex> lk(d->m);
                if (!d->available) continue;
                double dist = Location::distance(loc, pickup);
                if (dist < bestDist) { bestDist = dist; chosen = d->id; }
            }
        }
        if (chosen.empty()) return nullopt;
        return chosen;
    }
};

// ---------------- Trip ----------------
enum class TripStatus { Requested, Assigned, Ongoing, Completed, Cancelled };

struct Trip {
    string id;
    string riderId;
    string driverId;
    Location pickup, drop;
    TripStatus status = TripStatus::Requested;
    double fare = 0.0;
    unique_ptr<IPayment> payment;
    Trip(const string &rid, Location p, Location d, unique_ptr<IPayment> pay)
        : id(genId("T")), riderId(rid), pickup(p), drop(d), payment(move(pay)) {}
};

// ---------------- RideRequest (for queue) ----------------
struct RideRequest {
    string riderId;
    Location pickup;
    Location drop;
    string paymentType;
    RideRequest(const string &r, Location p, Location d, string pay)
        : riderId(r), pickup(p), drop(d), paymentType(move(pay)) {}
};

// ---------------- Ride Manager (orchestrator with concurrency) ----------------
class RideManager {
    vector<shared_ptr<Rider>> riders;
    vector<shared_ptr<Driver>> drivers;
    unordered_map<string, shared_ptr<Trip>> activeTrips;

    unique_ptr<IMatching> matcher;

    // request queue
    deque<RideRequest> queue_;
    mutex qmu_;
    condition_variable qcv_;
    atomic<bool> running{false};
    thread worker_;

    // locks
    mutex driversMu;
    mutex tripsMu;

public:
    RideManager(): matcher(make_unique<NearestMatching>()) {}

    ~RideManager() { stop(); }

    // lifecycle
    void start() {
        running = true;
        worker_ = thread([this]{ this->bookingWorker(); });
    }
    void stop() {
        running = false;
        qcv_.notify_all();
        if (worker_.joinable()) worker_.join();
        // join leftover trip threads? we launch trip threads detached; in prod we'd manage them properly
    }

    // register
    shared_ptr<Rider> createRider() {
        auto r = make_shared<Rider>();
        {
            lock_guard<mutex> lk(driversMu); // reuse driversMu for riders; ok for demo
            riders.push_back(r);
        }
        return r;
    }
    shared_ptr<Driver> createDriver(Location start) {
        auto d = make_shared<Driver>(start);
        lock_guard<mutex> lk(driversMu);
        drivers.push_back(d);
        return d;
    }

    // API: rider requests a ride (non-blocking)
    void requestRide(const RideRequest &req) {
        {
            lock_guard<mutex> lk(qmu_);
            queue_.push_back(req);
        }
        qcv_.notify_one();
    }

    // query helpers
    vector<shared_ptr<Driver>> listDrivers() {
        lock_guard<mutex> lk(driversMu);
        return drivers;
    }
    optional<shared_ptr<Trip>> getTrip(const string &tripId) {
        lock_guard<mutex> lk(tripsMu);
        if (activeTrips.count(tripId)) return activeTrips[tripId];
        return nullopt;
    }

private:
    // background worker: processes queue, matches driver, starts trip thread
    void bookingWorker() {
        safePrint("[Worker] Booking worker started");
        while (running) {
            RideRequest req("", {}, {}, "");
            {
                unique_lock<mutex> lk(qmu_);
                qcv_.wait(lk, [&]{ return !queue_.empty() || !running; });
                if (!running && queue_.empty()) break;
                if (!queue_.empty()) {
                    req = queue_.front();
                    queue_.pop_front();
                } else continue;
            }

            // choose driver
            shared_ptr<Driver> chosenDriver = chooseDriverFor(req.pickup);
            if (!chosenDriver) {
                safePrint("[Worker] No available driver for rider " + req.riderId + " at " + req.pickup.toString());
                // notify rider in real system
                continue;
            }

            // acquire driver (mark unavailable)
            bool got = chosenDriver->tryAcquire();
            if (!got) {
                safePrint("[Worker] Driver " + chosenDriver->id + " became unavailable; requeueing");
                // requeue at end
                requestRide(req);
                this_thread::sleep_for(chrono::milliseconds(200)); // small backoff
                continue;
            }

            // create trip
            auto payment = PaymentFactory::create(req.paymentType);
            auto trip = make_shared<Trip>(req.riderId, req.pickup, req.drop, move(payment));
            trip->driverId = chosenDriver->id;
            trip->status = TripStatus::Assigned;
            trip->fare = estimateFare(req.pickup, req.drop);

            {
                lock_guard<mutex> lk(tripsMu);
                activeTrips[trip->id] = trip;
            }

            // notify rider & driver
            notifyRider(req.riderId, "Driver " + chosenDriver->id + " assigned. TripId=" + trip->id);
            chosenDriver->obs->notify("Assigned to trip " + trip->id + ". Pickup at " + req.pickup.toString());

            // start trip thread (detached) to simulate driver movement and completion
            thread([this, trip, chosenDriver]() {
                runTrip(trip, chosenDriver);
            }).detach();
        }
        safePrint("[Worker] Booking worker stopping");
    }

    shared_ptr<Driver> chooseDriverFor(const Location &pickup) {
        vector<shared_ptr<Driver>> snapshot;
        {
            lock_guard<mutex> lk(driversMu);
            snapshot = drivers;
        }
        optional<string> driverId = matcher->chooseDriver(snapshot, pickup);
        if (!driverId) return nullptr;
        // find driver pointer
        for (auto &d : snapshot) if (d->id == *driverId) return d;
        return nullptr;
    }

    static double estimateFare(const Location &p, const Location &d) {
        double km = Location::distance(p, d);
        double base = 50.0;
        double perKm = 10.0;
        return base + perKm * km;
    }

    void runTrip(shared_ptr<Trip> trip, shared_ptr<Driver> driver) {
        safePrint("[Trip " + trip->id + "] started by driver " + driver->id + " for rider " + trip->riderId);
        trip->status = TripStatus::Ongoing;

        // simulate: driver moves from current location to pickup, then to drop
        Location start = driver->getLocation();
        moveDriverAlong(driver, start, trip->pickup, trip->id, "Heading to pickup");
        driver->obs->notify("Arrived at pickup. Starting trip to drop " + trip->drop.toString());
        // simulate travel to drop
        moveDriverAlong(driver, trip->pickup, trip->drop, trip->id, "En route to drop-off");

        // complete
        trip->status = TripStatus::Completed;
        // process payment
        trip->payment->pay(trip->fare, trip->id);
        // mark driver available & update location
        driver->setLocation(trip->drop);
        driver->release();

        // notify completion
        notifyRider(trip->riderId, "Trip " + trip->id + " completed. Fare: ₹" + to_string(trip->fare));
        driver->obs->notify("Trip " + trip->id + " completed. You are now available.");

        // cleanup
        {
            lock_guard<mutex> lk(tripsMu);
            activeTrips.erase(trip->id);
        }
    }

    static void moveDriverAlong(shared_ptr<Driver> driver, const Location &from, const Location &to,
                                const string &tripId, const string &stage) {
        int steps = 5;
        for (int i = 1; i <= steps; ++i) {
            Location p;
            p.x = from.x + (to.x - from.x) * (double(i)/steps);
            p.y = from.y + (to.y - from.y) * (double(i)/steps);
            driver->setLocation(p);
            driver->obs->notify(stage + " | " + driver->getLocation().toString() + " | trip=" + tripId);
            this_thread::sleep_for(chrono::milliseconds(400));
        }
    }

    void notifyRider(const string &riderId, const string &msg) {
        // find rider and notify
        lock_guard<mutex> lk(driversMu); // reuse driversMu for riders list protection in this demo
        for (auto &r : riders) if (r->id == riderId) { r->obs->notify(msg); return; }
    }

    // Note: in this simplified demo riders vector is protected by driversMu lock; in production separate locks/data stores would be used
};

// ---------------- Demo ----------------
int main() {
    RideManager mgr;
    mgr.start();

    // create drivers
    auto d1 = mgr.createDriver({0,0});
    auto d2 = mgr.createDriver({5,5});
    auto d3 = mgr.createDriver({10,0});

    // create riders
    auto r1 = mgr.createRider();
    auto r2 = mgr.createRider();
    auto r3 = mgr.createRider();

    // simulate concurrent ride requests
    vector<thread> clients;
    clients.emplace_back([&mgr, id=r1->id](){
        mgr.requestRide( RideRequest(id, {1,1}, {8,8}, "wallet") );
    });
    clients.emplace_back([&mgr, id=r2->id](){
        this_thread::sleep_for(chrono::milliseconds(100));
        mgr.requestRide( RideRequest(id, {6,4}, {12,0}, "card") );
    });
    clients.emplace_back([&mgr, id=r3->id](){
        this_thread::sleep_for(chrono::milliseconds(200));
        mgr.requestRide( RideRequest(id, {2,0}, {3,9}, "cash") );
    });

    // wait for clients to enqueue
    for (auto &t: clients) if (t.joinable()) t.join();

    // let system run for some time to process trips
    this_thread::sleep_for(chrono::seconds(12));

    mgr.stop();
    safePrint("[Main] Ride manager stopped. Exiting.");
    return 0;
}
```

#### Output
```
[Worker] Booking worker started
[Rider:R-1] Driver D-1 assigned. TripId=T-1
[Driver:D-1] Assigned to trip T-1. Pickup at (1.00,1.00)
[Trip T-1] started by driver D-1 for rider R-1
[Driver:D-1] Heading to pickup | (0.20,0.20) | trip=T-1
[Rider:R-2] Driver D-2 assigned. TripId=T-2
[Driver:D-2] Assigned to trip T-2. Pickup at (6.00,4.00)
[Trip T-2] started by driver D-2 for rider R-2
[Driver:D-2] Heading to pickup | (5.20,4.80) | trip=T-2
[Rider:R-3] Driver D-3 assigned. TripId=T-3
[Driver:D-3] Assigned to trip T-3. Pickup at (2.00,0.00)
[Trip T-3] started by driver D-3 for rider R-3
[Driver:D-3] Heading to pickup | (8.40,0.00) | trip=T-3
[Driver:D-1] Heading to pickup | (0.40,0.40) | trip=T-1
[Driver:D-2] Heading to pickup | (5.40,4.60) | trip=T-2
[Driver:D-3] Heading to pickup | (6.80,0.00) | trip=T-3
[Driver:D-1] Heading to pickup | (0.60,0.60) | trip=T-1
[Driver:D-2] Heading to pickup | (5.60,4.40) | trip=T-2
[Driver:D-3] Heading to pickup | (5.20,0.00) | trip=T-3
[Driver:D-1] Heading to pickup | (0.80,0.80) | trip=T-1
[Driver:D-2] Heading to pickup | (5.80,4.20) | trip=T-2
[Driver:D-3] Heading to pickup | (3.60,0.00) | trip=T-3
[Driver:D-1] Heading to pickup | (1.00,1.00) | trip=T-1
[Driver:D-2] Heading to pickup | (6.00,4.00) | trip=T-2
[Driver:D-3] Heading to pickup | (2.00,0.00) | trip=T-3
[Driver:D-1] Arrived at pickup. Starting trip to drop (8.00,8.00)
[Driver:D-1] En route to drop-off | (2.40,2.40) | trip=T-1
[Driver:D-2] Arrived at pickup. Starting trip to drop (12.00,0.00)
[Driver:D-2] En route to drop-off | (7.20,3.20) | trip=T-2
[Driver:D-3] Arrived at pickup. Starting trip to drop (3.00,9.00)
[Driver:D-3] En route to drop-off | (2.20,1.80) | trip=T-3
[Driver:D-1] En route to drop-off | (3.80,3.80) | trip=T-1
[Driver:D-2] En route to drop-off | (8.40,2.40) | trip=T-2
[Driver:D-3] En route to drop-off | (2.40,3.60) | trip=T-3
[Driver:D-1] En route to drop-off | (5.20,5.20) | trip=T-1
[Driver:D-2] En route to drop-off | (9.60,1.60) | trip=T-2
[Driver:D-3] En route to drop-off | (2.60,5.40) | trip=T-3
[Driver:D-1] En route to drop-off | (6.60,6.60) | trip=T-1
[Driver:D-2] En route to drop-off | (10.80,0.80) | trip=T-2
[Driver:D-3] En route to drop-off | (2.80,7.20) | trip=T-3
[Driver:D-1] En route to drop-off | (8.00,8.00) | trip=T-1
[Driver:D-2] En route to drop-off | (12.00,0.00) | trip=T-2
[Driver:D-3] En route to drop-off | (3.00,9.00) | trip=T-3
[Payment][T-1] Wallet debited: Γé╣148.994949
[Rider:R-1] Trip T-1 completed. Fare: Γé╣148.994949
[Driver:D-1] Trip T-1 completed. You are now available.
[Payment][T-2] Card charged: Γé╣122.111026
[Rider:R-2] Trip T-2 completed. Fare: Γé╣122.111026
[Driver:D-2] Trip T-2 completed. You are now available.
[Payment][T-3] Cash collected: Γé╣140.553851
[Rider:R-3] Trip T-3 completed. Fare: Γé╣140.553851
[Driver:D-3] Trip T-3 completed. You are now available.
[Worker] Booking worker stopping
[Main] Ride manager stopped. Exiting.
```
