# Simple Fitness Tracking App
## 1. Features Required
- User Profile (height, weight, age, fitness goals)
- Activity Tracking (steps, distance, calories, heart rate)
- Workout logging (running, cycling gym sessions)
- Goal Management (calory burn targets, daily/weekly step goals)
- Social Features (friends, leaderboard)
- Notifications (goal achievement, reminders)
- Data Sync (sync across devices)

## 2. Design Patterns Used
- Observer -> Notify users when goals are achieved
- Strategy -> Different calculation strategies (calories burnt for running vs cycling)
- Singleton -> Centralized DataStore
- Pub-Sub -> `SyncService` maintains per-user device subscriptions

## 3. Design Highlights
- **Modular Structure**: Users, workouts, activities, goals, sync and leaderboard decoupled
- **Extensible Workout Types**: Just add a new WorkoutStrategy
- **Scalable Goal Management**: Multiple observers possible
- **Sync Across Devices**: Multi-device support per user
- **Unified Leaderboard**: Aggregates both workouts and daily activities
- **Safe Singletom Implementations**: Copy/move constructors deleted to enforce single instance
- **Extensibiity**
  - Add **new workout strategies** (e.g. swimming, weightlifting) without changing `Workout`
  - Add new metrics to **Activity** (e.g. sleep, hydration) with minimal changes
  - Extend **SyncService** to support offline sync (storing updates until device reconnects)
  - Expand **Leaderboard** with weekly/monthly rankings
  - Add **Friends/Social Graph** (users can follow each other for comparative stats

## Solution
```cpp
#include <string>
#include <iostream>
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <functional>

using namespace std;

// ----------- Core Entities -----------
class User {
    string name;
    int age;
    double height, weight; // add suffix for unit
public:
    User(string n, int a, double h, double w)
        : name(move(n)), age(a), height(h), weight(w) {}
    string getName() const { return name; }
};

// ----------- Strategy Pattern for Calories Calculation -----------
class WorkoutStrategy {
public:
    virtual ~WorkoutStrategy() = default;
    virtual double calculateCalories(double durationMin, double intensity) = 0;
};

class RunningStrategy : public WorkoutStrategy {
public:
    double calculateCalories(double durationMin, double intensity) override {
        return durationMin * intensity * 10; // simplified
    }
};

class CyclingStrategy : public WorkoutStrategy {
public:
    double calculateCalories(double durationMin, double intensity) override {
        return durationMin * intensity * 8;
    }
};

// ----------- Workout Logging -----------
class Workout {
    string type;
    double duration;
    double intensity;
    WorkoutStrategy* strategy;
public:
    Workout(string t, double d, double i, WorkoutStrategy *s) 
        : type(move(t)), duration(d), intensity(i), strategy(s) {}
    
    virtual double getCalories() const {
        return strategy->calculateCalories(duration, intensity);
    }

    string getType() const { return type; }
};

// ----------- Observer Pattern for Notifications -----------
class Observer {
public:
    virtual ~Observer() = default;
    virtual void update(string msg) = 0;
};

class NotificationService : public Observer {
public:
    void update(string msg) override {
        cout << "[Notification]: " << msg << "\n";
    }
};

// ----------- Goal Tracking -----------
class Goal {
    double targetCalories;
    double currentCalories = 0;
    vector<Observer*> observers;
public:
    Goal(double target): targetCalories(target) {}

    void addObserver(Observer *obs) { observers.push_back(obs); }

    void logWorkout(const Workout &w) {
        currentCalories += w.getCalories();
        if(currentCalories >= targetCalories) {
            for(auto &obs : observers) {
                obs->update("Goal Achieved: Total Calories Burnt = " + to_string(currentCalories));
            }
        }
    }
};

// ----------- Singleton Datastore -----------
class DataStore {
    unordered_map<string, vector<Workout>> userWorkouts;

    DataStore() = default;

    DataStore(const DataStore&) = delete;
    DataStore& operator=(DataStore&) = delete;
    DataStore(DataStore&&) = delete;
    DataStore& operator=(DataStore&&) = delete;

public:
    static DataStore& getInstance() {
        static DataStore instance;
        return instance;
    }

    void logWorkout(string user, Workout w) {
        userWorkouts[user].push_back(w);
    }

    void showWorkouts(string user) {
        cout << "Workouts for " << user << ":\n";
        if(!userWorkouts.count(user)) return;
        for(auto &w : userWorkouts[user]) {
            cout << "- " << w.getType() << " burnt " << w.getCalories() << " cal\n";
        }
    }
};

// ----------- Activity Tracking (daily activity stats outside workouts) -----------
class Activity {
    int steps;
    double distanceKm;
    int avgHeartRate;
    double calories;

public:
    Activity(int s, double d, int hr, double c) 
        : steps(s), distanceKm(d), avgHeartRate(hr), calories(c) {}
    
    int getSteps() const { return steps; }
    int getDistance() const { return distanceKm; }
    int getHeartRate() const { return avgHeartRate; }
    int getCalories() const { return calories; }
};

// Singleton for tracking user activities
class ActivityTracker {
    unordered_map<string, vector<Activity>> userActivies;

    ActivityTracker() = default;
    ActivityTracker(const ActivityTracker&) = delete;
    ActivityTracker& operator=(ActivityTracker&) = delete;
    ActivityTracker(ActivityTracker&&) = delete;
    ActivityTracker& operator=(ActivityTracker&&) = delete;
public:
    static ActivityTracker& getInstance() {
        static ActivityTracker instance;
        return instance;
    }

    void logActivity(const string &user, const Activity &a) {
        userActivies[user].push_back(a);
    }

    void showActivities(const string &user) {
        cout << "Activities for " << user << ":\n";
        auto it = userActivies.find(user);
        if(it == userActivies.end()) {
            cout << " (No activities logged)\n";
            return;
        }
        for(auto &a : userActivies[user]) {
            cout << "- Steps: " << a.getSteps()
                 << ", Distance: " << a.getDistance() << " km"
                 << ", HeartRate: " << a.getHeartRate()
                 << ", Calories: " << a.getCalories() << " cal\n";
        }
    }
};

// ----------- Sync Layer (Data Sync across devices) -----------
enum class UpdateType { 
    WORKOUT_ADDED, 
    ACTIVITY_ADDED
};

struct Update {
    UpdateType type;
    string user;
    string summary; // human-readable summary of update
};

class SyncService {
    // user -> list of device ids
    unordered_map<string, vector<string>> userDevices;
    // device id -> callback
    unordered_map<string, function<void(const Update &)>> deviceCallbacks;

    SyncService() = default;
    SyncService(const SyncService&) = delete;
    SyncService& operator=(SyncService&) = delete;
    SyncService(SyncService&&) = delete;
    SyncService& operator=(SyncService&&) = delete;
public:
    static SyncService& getInstance() {
        static SyncService instance;
        return instance;
    }

    // register a device callabck for a user. deviceId shld be unique globally
    void registerDevice(const string &user, const string &deviceId, function<void(const Update &)> cb) {
        deviceCallbacks[deviceId] = move(cb);
        auto &vec = userDevices[user];
        // avoid duplicate device ids
        if(find(vec.begin(), vec.end(), deviceId) == vec.end())
            vec.push_back(deviceId);
        
        cout << "[SyncService] Device " << deviceId << " registered for user " << user << "\n";
    }

    void unregisterDevice(const string &user, const string &deviceId) {
        auto it = userDevices.find(user);
        if(it != userDevices.end()) {
            auto &vec = it->second;
            vec.erase(remove(vec.begin(), vec.end(), deviceId), vec.end());
        }
        cout << "[SyncService] Device " << deviceId << " unregistered for user " << user << "\n";
    }

    // Notify all devices of a usr abt an update
    void notifyUserUpdate(const string &user, const Update &upd) {
        auto it = userDevices.find(user);
        if(it == userDevices.end()) return ;
        for(const auto &devId: it->second) {
            auto cbIt = deviceCallbacks.find(devId);
            if(cbIt != deviceCallbacks.end()) {
                cbIt->second(upd);
            }
        }
    }
};

// Device Simulator (represents a user's device)
class Device {
    string deviceId;
    string owner; // user name
    vector<string> inbox; //recvd summaries
public:
    Device(string did, string user)
        : deviceId(move(did)), owner(move(user)) {}
    
    void start() {
        // register callback with sync service
        SyncService::getInstance().registerDevice(owner, deviceId, [this](const Update &u){ this->onUpdate(u); });
    }

    void stop() {
        SyncService::getInstance().unregisterDevice(owner, deviceId);
    }

    void onUpdate(const Update &u) {
        string line = "[Device " + deviceId + " received] " + u.summary;
        cout << line << "\n";
        inbox.push_back(line);
    }

    const vector<string>& getInbox() const { return inbox; }
};

// ----------- Singleton Leaderboard -----------
class Leaderboard {
    unordered_map<string, double> userCalories;

    Leaderboard() = default;
    Leaderboard(const Leaderboard&) = delete;
    Leaderboard& operator=(Leaderboard&) = delete;
    Leaderboard(Leaderboard&&) = delete;
    Leaderboard& operator=(Leaderboard&&) = delete;

public:
    static Leaderboard& getInstance() {
        static Leaderboard instance;
        return instance;
    }

    void updateUser(const string &name, double calories) {
        userCalories[name] += calories;
    }

    void showTopN(int n) {
        vector<pair<string,double>> vec(userCalories.begin(), userCalories.end());
        sort(vec.begin(), vec.end(), [](auto &a, auto &b){
            return a.second > b.second;
        });

        cout << "\n=== Leaderboard (Top " << n << ") ===\n";
        for(int i=0; i<min(n,(int)vec.size()); ++i) {
            cout << i+1 << ". " << vec[i].first
                 << " - " << vec[i].second << " cal\n"; 
        }
    }
};

// ----------- FitnessApp Driver -----------
class FitnessApp {
    NotificationService notifier;
    unordered_map<string, Goal> userGoals;

public:
    void setGoal(const User &u, double calories) {
        Goal g(calories);
        g.addObserver(&notifier);
        // userGoals[u.getName()] = move(g); // this gives error
        userGoals.insert_or_assign(u.getName(), move(g));
    }

    void logWorkout(const User &user, const Workout &w) {
        // 1. log workout in datastore
        DataStore::getInstance().logWorkout(user.getName(), w);

        // 2. update goal if present
        if(userGoals.count(user.getName())) {
            userGoals.at(user.getName()).logWorkout(w);
        }

        // 3. update leaderboard
        Leaderboard::getInstance().updateUser(user.getName(), w.getCalories());

        // 4. notify registered devices via SyncService
        Update upd;
        upd.type = UpdateType::WORKOUT_ADDED;
        upd.user = user.getName();
        upd.summary = "Workout added: " + w.getType() + " (" + to_string(w.getCalories()) + " cal)";
        SyncService::getInstance().notifyUserUpdate(user.getName(), upd);
    }

    void showUserWorkouts(const User &user) {
        DataStore::getInstance().showWorkouts(user.getName());
    }

    void showLeaderboard(int n) {
        Leaderboard::getInstance().showTopN(n);
    }

    void logActivity(const User &user, const Activity &a) {
        ActivityTracker::getInstance().logActivity(user.getName(), a);

        // update leaderboard
        Leaderboard::getInstance().updateUser(user.getName(), a.getCalories());

        // update goal if present
        if(userGoals.count(user.getName())) {
            // create a dummy workout-equivalent for goal (using calories directly)
            class DummyWorkout : public Workout {
            public:
                double cals;
                DummyWorkout(double c): Workout("Activity", 0, 0, nullptr), cals(c) {}
                double getCalories() const { return cals; }
            } dummy(a.getCalories());

            userGoals.at(user.getName()).logWorkout(dummy);
        }

        // notify devices
        Update upd;
        upd.type = UpdateType::ACTIVITY_ADDED;
        upd.user = user.getName();
        upd.summary = "Activity added: steps=" + to_string(a.getSteps())
                        + " dist=" + to_string(a.getDistance()) + " km"
                        + " cal=" + to_string(a.getCalories());
        SyncService::getInstance().notifyUserUpdate(user.getName(), upd);
    }

    void showUserActivities(const User &user) {
        ActivityTracker::getInstance().showActivities(user.getName());
    }
};

// ----------- main (Demo) -----------
int main() {
    FitnessApp app;

    User u1("Alice", 25, 165, 60);
    User u2("Bob", 30, 170, 75);

    // create device simulators for Alice and Bob
    Device alicePhone("alice-phone-1", u1.getName());
    Device aliceWatch("alice-watch-1", u1.getName());
    Device bobPhone("bob-phone-1", u2.getName());

    // devices register with sync service
    alicePhone.start();
    aliceWatch.start();
    bobPhone.start();

    // Strategies
    RunningStrategy runningStrategy;
    CyclingStrategy cyclingStrategy;

    // Workouts
    Workout w1("Running", 30, 1.2, &runningStrategy); // 360 cal
    Workout w2("Cycling", 40, 1.0, &cyclingStrategy); // 320 cal
    Workout w3("Running", 20, 1.5, &runningStrategy); // 300 cal

    // Raw Activity Tracking
    Activity a1(5000, 3.5, 80, 200);
    Activity a2(8000, 6.0, 85, 350);

    // Set Goals
    app.setGoal(u1, 500);

    // Logging workouts
    app.logWorkout(u1, w1);
    app.logWorkout(u1, w2);
    app.logWorkout(u2, w3);

    // Logging activities
    app.logActivity(u1, a1);
    app.logActivity(u2, a2);

    // Show user data
    app.showUserWorkouts(u1);
    app.showUserWorkouts(u2);

    app.showUserActivities(u1);
    app.showUserActivities(u2);

    // Show leaderboard
    app.showLeaderboard(5);

    // devices could be stopped or unregistered
    alicePhone.stop();
    aliceWatch.stop();
    bobPhone.stop();

    return 0;
}
```

#### Sample output
```
[SyncService] Device alice-phone-1 registered for user Alice
[SyncService] Device alice-watch-1 registered for user Alice
[SyncService] Device bob-phone-1 registered for user Bob
[Device alice-phone-1 received] Workout added: Running (360.000000 cal)
[Device alice-watch-1 received] Workout added: Running (360.000000 cal)
[Notification]: Goal Achieved: Total Calories Burnt = 680.000000
[Device alice-phone-1 received] Workout added: Cycling (320.000000 cal)
[Device alice-watch-1 received] Workout added: Cycling (320.000000 cal)
[Device bob-phone-1 received] Workout added: Running (300.000000 cal)
[Notification]: Goal Achieved: Total Calories Burnt = 880.000000
[Device alice-phone-1 received] Activity added: steps=5000 dist=3 km cal=200
[Device alice-watch-1 received] Activity added: steps=5000 dist=3 km cal=200
[Device bob-phone-1 received] Activity added: steps=8000 dist=6 km cal=350
Workouts for Alice:
- Running burnt 360 cal
- Cycling burnt 320 cal
Workouts for Bob:
- Running burnt 300 cal
Activities for Alice:
- Steps: 5000, Distance: 3 km, HeartRate: 80, Calories: 200 cal
Activities for Bob:
- Steps: 8000, Distance: 6 km, HeartRate: 85, Calories: 350 cal

=== Leaderboard (Top 5) ===
1. Alice - 880 cal
2. Bob - 650 cal
[SyncService] Device alice-phone-1 unregistered for user Alice
[SyncService] Device alice-watch-1 unregistered for user Alice
[SyncService] Device bob-phone-1 unregistered for user Bob
```
