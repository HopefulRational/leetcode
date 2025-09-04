# Elevator System
## 1. Features Required
- Support for multiple elevators in the building
- Each lelevator should move between floors, open/close doors, handle requests from inside and outside
- Requests can be up or down from floors, or direct destination floors (here, only destination fllor considered in the design)
- Elevator scheduling: decide which elevator serves which requests (basic strategy: nearest elevator, advanced: look at direction + load)
- Fault tolerance: if an elevator is busy, another should take the request

## 2. Design Patterns Used
- Singleton -> ElevatorController (only one global controller to assign requests)
- Observer -> Floors observing elevator state changes
- Command Pattern -> Encapsulate requests as commands
- Strategy -> Different scheduling algorithms (nearest elevator, load-based, etc.)

## 3. Design Highlights
- **Thread Safety**
- **Background thread** for `runLoop`

## Solution
```cpp
#include <set>
#include <iostream>
#include <vector>
#include <mutex>
#include <memory>
#include <thread>
#include <chrono>
#include <queue>
#include <condition_variable>
#include <atomic>
 

using namespace std;

enum class Direction { UP, DOWN, IDLE };

struct Request {
    int floor;
    Direction dir;
    Request(int f, Direction d = Direction::IDLE) : floor(f), dir(d) {}
};

// ----------- Elevator -----------

class Elevator {
    int id;
    int currentFloor;
    Direction direction;
    bool doorsOpen;
    set<int> requests;
 
public:
    Elevator(int eid, int startFloor = 0)
        : id(eid), currentFloor(startFloor), direction(Direction::IDLE), doorsOpen(false) {}
   
    int         getId()             const { return id; }
    int         getCurrentFloor()   const { return currentFloor; }
    Direction   getDirection()      const { return direction; }
    bool        isIdle()            const { return requests.empty(); }
 
    void addRequest(int floor) { requests.insert(floor); }
 
    void step() {
        if(requests.empty()) {
            direction = Direction::IDLE;
            return;
        }
 
        int target = *requests.begin();
        if(currentFloor < target) {
            direction = Direction::UP;
            currentFloor++;
        }
        else if(currentFloor > target) {
            direction = Direction::DOWN;
            currentFloor--;
        }
        else {
            // Arrived

            openDoors();
            requests.erase(target);
            closeDoors();
        }
    }
 
    void openDoors() {
        doorsOpen = true;
        cout << "Elevator " << id << " opened doors at floor " << currentFloor << "\n";
    }
 
    void closeDoors() {
        doorsOpen = false;
        cout << "Elevator " << id << " closed doors\n";
    }
};
 
// ----------- Scheduler (Strategy) -----------

class Scheduler {
public:
    virtual int selectElevator(vector<shared_ptr<Elevator>> &elevators, const Request &req) = 0;
};
 
// Nearest elevator strategy

class NearestScheduler : public Scheduler {
public:
    int selectElevator(vector<shared_ptr<Elevator>> &elevators, const Request &req) override {
        int bestId = -1;
        int minDist = INT_MAX;
 
        for(auto &e : elevators) {
            int dist = abs(e->getCurrentFloor() - req.floor);
            if(dist < minDist) {
                minDist = dist;
                bestId = e->getId();
            }
        }
        return bestId;
    }
};
 
// ----------- Elevator Controller (singleton) -----------

class ElevatorController {
    vector<shared_ptr<Elevator>> elevators;
    unique_ptr<Scheduler> scheduler;
   
    // Threading/queue

    mutex q_mtx;
    condition_variable cv;
    queue<Request> q;
    atomic<bool> stop{false};
    thread sim;

public:
    ElevatorController(int numElevators, unique_ptr<Scheduler> s) {
        scheduler = move(s);
        for(int i=0; i<numElevators; ++i) {
            elevators.push_back(make_shared<Elevator>(i));
        }
        sim = thread([this]{ runLoop(); });
    }
 
    ~ElevatorController() {
        stopApp();
    }
 
    // Producer API: can be called from any thread

    void handleRequest(const Request &req) {
        {
            lock_guard<mutex> lock(q_mtx);
            q.push(req);
        }
        cv.notify_one();
    }
 
    void stopApp() {
        {
            lock_guard<mutex> lock(q_mtx);
            stop = true;
        }
        cv.notify_all();
        if(sim.joinable()) sim.join();
    }
 

private:
    void runLoop() {
        while(!stop) {
            // 1. Drain requests
            vector<Request> batch;
            {
                unique_lock<mutex> lock(q_mtx);
                cv.wait_for(lock, chrono::milliseconds(100), [this]{ return stop || !q.empty(); });
                while(!q.empty()) { batch.push_back(q.front()); q.pop(); }
            }
 
            // 2. Apply requests (single-threaded access to elevator)
            for(auto &req : batch) {
                int chosenId = scheduler->selectElevator(elevators, req);
                if(chosenId >= 0) elevators[chosenId]->addRequest(req.floor);
            }
 
            // 3. Step simulation
            for(auto &e : elevators) e->step();
        }
    }
};
 
// ----------- Demo -----------

int main() {
    auto scheduler = make_unique<NearestScheduler>();
    ElevatorController controller(3, move(scheduler));
 
    // Some requests
    controller.handleRequest(Request(7, Direction::UP));
    
    this_thread::sleep_for(chrono::milliseconds(200));

    controller.handleRequest(Request(2, Direction::DOWN));
    
    this_thread::sleep_for(chrono::milliseconds(200));
    
    controller.handleRequest(Request(1, Direction::DOWN));
    
    this_thread::sleep_for(chrono::milliseconds(50));
    
    controller.handleRequest(Request(4, Direction::DOWN));
    
    this_thread::sleep_for(chrono::milliseconds(250));
    
    controller.handleRequest(Request(1, Direction::DOWN));
    
    this_thread::sleep_for(chrono::milliseconds(150));
    
    controller.handleRequest(Request(6, Direction::UP));
    
    this_thread::sleep_for(chrono::milliseconds(150));

    return 0;
}
```

#### Output
```
Elevator 0 opened doors at floor 2
Elevator 0 closed doors
Elevator 0 opened doors at floor 4
Elevator 0 closed doors
Elevator 1 opened doors at floor 1
Elevator 1 closed doors
Elevator 1 opened doors at floor 1
Elevator 1 closed doors
Elevator 0 opened doors at floor 7
Elevator 0 closed doors
Elevator 0 opened doors at floor 6
Elevator 0 closed doors
```
