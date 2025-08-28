# Digital Wellbeing App
## 1. Features Required
- Usage tracking (per-app, per-session)
- Focus sessions (do not distorb / block apps during sessions)
- App limits with enforcement (block after limit reached)
- Notifications/alerts
- Parental control (enforce hard limits for child accounts)
- Background aggregator that persists daily counters (in-memory demo)
- Simple reporting (daily/weekly summary)
- Thread-sefaty and a simulated event generator

## 2. Designs patterns used
- Observer -> Notifications
- Strategy -> report generation / limit policy
- Facade -> `WellbeingService`
- Producer-Consumer -> Event queue
- Background worker -> Aggregations/reports

## 3. Design Highlights
- **Architecture**: device <-> collector (events) -> WellbeingService (Aggregator + enforcer) -> notifier & parental console. Storage can be local(device) or cloud(server)
- **Enforcement**: soft(notify) vs hard(OS-level blocking). Hard blocking simulated by `Blocker`
- **Provacy**: do not store raw app content. Store aggregated metrics
- **Scaling**: shard user data, stream user events (Kafka) to analytics workers, use time-series DB for metrics, TTL/retention for data
- **Edge cases**: clock drift across devices, background throttling, offline mode (buffer events), cross-device merging (conflict resolution)
- **Extensibility**: add adaptive limits using ML (detect addictive patterns), social challenges & leaderboards, device-level MDM integrations for parental control

```cpp
#include <chrono>
#include <string>
#include <iostream>
#include <iomanip>
#include <unordered_map>
#include <mutex>
#include <unordered_set>
#include <memory>
#include <deque>
#include <condition_variable>
#include <atomic>
#include <thread>
#include <vector>

using namespace std;
using ms = chrono::milliseconds;
using Clock = chrono::steady_clock;
using TimePoint = Clock::time_point;

static TimePoint now() { return Clock::now(); }
static long long secs_since(const TimePoint &tp) {
    return chrono::duration_cast<chrono::seconds>(now() - tp).count();
}

// ----------- Domain -----------
using UserId = string;
using AppId =  string;

enum class EventType { 
    APP_FOREGROUND, 
    APP_BACKGROUND, 
    FOCUS_START, 
    FOCUS_END
};

struct UsageEvent {
    EventType type;
    UserId user;
    AppId app; // optional for focus events
    TimePoint ts;
};

// current foreground app per user + timestamp
struct ForegroundState {
    AppId app;
    TimePoint startedAt;
    bool active = false;
};

// ----------- Observer (notifications) -----------
struct INotifier {
    virtual ~INotifier() = default;
    virtual void notify(const UserId & user, const string &title, const string &msg) = 0;
};

struct ConsoleNotifier : public INotifier {
    void notify(const UserId &user, const string &title, const string &msg) {
        auto s = chrono::system_clock::to_time_t(chrono::system_clock::now());
        cout << "[" << std::put_time(std::localtime(&s), "%F %T") << "] NOTIFY(" << user <<") "
             << title << " - " << msg << "\n";
    }
};

// ----------- Limit policy / parental rules -----------
struct LimitPolicy {
    // daily limit in seconds for the app; 0 means no limit
    unordered_map<AppId, int> dailyLimitsSec;
    bool hardBlockOnLimit = true; // if true, block app when exceeded
};

// ----------- Storage: in-memory (swap with DB) -----------
class UsageStore {
    // user -> app -> usage seconds for current day
    unordered_map<UserId, unordered_map<AppId, long long>> dailyUsage_;
    // user ->app -> total seconds in this run (for reporting)
    unordered_map<UserId, unordered_map<AppId, long long>> sessionTotals_;
    mutable mutex mu_;

public:
    void add_usage(const UserId& user, const AppId &app, long long seconds) {
        lock_guard<mutex> lk(mu_);
        dailyUsage_[user][app] += seconds;
        sessionTotals_[user][app] += seconds;
    }

    long long get_daily(const UserId &user, const AppId &app) const {
        lock_guard<mutex> lk(mu_);
        auto it = dailyUsage_.find(user);
        if(it == dailyUsage_.end()) return 0;
        auto jt = it->second.find(app);
        return jt == it->second.end() ? 0LL : jt->second;
    }

    unordered_map<AppId, long long> snapshot_user(const UserId &user) const {
        lock_guard<mutex> lk(mu_);
        auto it = dailyUsage_.find(user);
        if (it == dailyUsage_.end()) return {};
        return it->second;
    }

    unordered_map<AppId, long long> snapshot_session(const UserId &user) const {
        lock_guard<mutex> lk(mu_);
        auto it = sessionTotals_.find(user);
        if(it == sessionTotals_.end()) return {};
        return it->second;
    }

    void reset_daily() {
        lock_guard<mutex> lk(mu_);
        dailyUsage_.clear();
    }
};

// ----------- EnforceMent: block table -----------
class Blocker {
    // user -> set of blocked apps
    unordered_map<UserId, unordered_set<AppId>> blocked_;
    mutable mutex mu_;

public:
    void block(const UserId &user, const AppId &app) {
        lock_guard<mutex> lk(mu_);
        blocked_[user].insert(app);
    }

    void unblock(const UserId &user, const AppId &app) {
        lock_guard<mutex> lk(mu_);
        if(blocked_.count(user))
            blocked_[user].erase(app);
    }

    bool is_blocked(const UserId &user, const AppId &app) {
        lock_guard<mutex> lk(mu_);
        return blocked_.count(user) ? (blocked_[user].count(app) > 0) : false;
    }
};

// ----------- Wellbeing service (Facade) -----------
class WellbeingService {
    // components
    UsageStore store_;
    Blocker blocker_;
    unique_ptr<INotifier> notifier_;

    // policies per user (can be inherited from defaults)
    unordered_map<UserId, LimitPolicy> policies_;

    // state: current foreground app per user + timestamp
    unordered_map<UserId, ForegroundState> fgState_;

    // event queue and background worker
    deque<UsageEvent> q_;
    mutex qmu_;
    condition_variable qcv_;
    atomic<bool> running_;
    thread worker_;

    // periodic reporter (daily rollover simulated by short interval)
    thread dailyReporter_;
    int rolloverIntervalSec_ = 20;

    // parental control set of child accounts -> parent id
    unordered_map<UserId, UserId> parentOf_;

public:
    WellbeingService(unique_ptr<INotifier> notifier = make_unique<ConsoleNotifier>())
        : notifier_(move(notifier)) {}
    
    void start() {
        if(running_) return;
        running_ = true;
        worker_ = thread([this]{ this->event_loop(); });
        dailyReporter_ = thread([this]{ this->daily_rollover_loop(); });
    }

    void stop() {
        if(!running_) return;
        running_ = false;
        qcv_.notify_all();
        if(worker_.joinable()) worker_.join();
        if(dailyReporter_.joinable()) dailyReporter_.join();
    }

    // API: user registers a policy (Could be parent's configured)
    void set_policy(const UserId &user, const LimitPolicy &p) {
        policies_[user] = p;
    }

    void set_parent(const UserId &child, const UserId &parent) {
        parentOf_[child] = parent;
    }

    // API: events from device / OS integration
    void publish_event(const UsageEvent &ev) {
        {
            lock_guard<mutex> lk(qmu_);
            q_.push_back(ev);
        }
        qcv_.notify_one();
    }

    // query
    long long get_daily_usage(const UserId &user, const AppId &app) const {
        return store_.get_daily(user, app);
    }

    bool is_blocked(const UserId &user, const AppId &app) {
        return blocker_.is_blocked(user, app);
    }

private:
    // Event processor
    void event_loop() {
        while(running_) {
            UsageEvent ev;
            {
                unique_lock<mutex> lk(qmu_);
                if(q_.empty()) qcv_.wait_for(lk, ms(500));
                if(!q_.empty()) { ev = q_.front(); q_.pop_front(); }
                else { continue; }
            }
            handle_event(ev);
        }
        // drain
        while(true) {
            UsageEvent ev;
            {
                lock_guard<mutex> lk(qmu_);
                if(q_.empty()) break;
                ev = q_.front(); q_.pop_front();
            }
            handle_event(ev);
        }
    }

    void handle_event(const UsageEvent &ev) {
        // basic routing
        if(ev.type == EventType::APP_FOREGROUND) {
            on_foreground(ev.user, ev.app, ev.ts);
        } else if(ev.type == EventType::APP_BACKGROUND) {
            on_background(ev.user, ev.app, ev.ts);
        } else if(ev.type == EventType::FOCUS_START) {
            on_focus_start(ev.user, ev.ts);
        } else if(ev.type == EventType::FOCUS_END) {
            on_focus_end(ev.user, ev.ts);
        }
    }

    // track fg start
    void on_foreground(const UserId &user, const AppId &app, TimePoint ts) {
        // if app blocked, send kill/notification back to device (in here, we just notify)
        if(blocker_.is_blocked(user, app)) {
            notifier_->notify(user, "App Blocker", "App '" + app + "' is blocked by policy. Closing it.");
            return;
        }

        // if already another active foreground, treat it as backgruond first
        if(fgState_[user].active) {
            // background the previous
            auto prev = fgState_[user];
            long long dur = secs_since(prev.startedAt);
            if(dur > 0) {
                store_.add_usage(user, app, dur);
                enforce_limits(user, prev.app);
            }
        }

        fgState_[user] = ForegroundState{user, ts, true};
    }

    // track fg end and add usage
    void on_background(const UserId &user, const AppId &app, TimePoint ts) {
        auto &st = fgState_[user];
        if(!st.active) return;
        if(st.app != app) {
            // ignore mismatch or treat as safety. In here, just ignoring
            return;
        }
        long long dur = secs_since(st.startedAt);
        if(dur > 0) {
            store_.add_usage(user, app, dur);
            enforce_limits(user, app);
        }
        st.active = false;
    }

    void on_focus_start(const UserId &user, TimePoint ts) {
        // block distracting apps during focus
        // policy: block apps with daily limit configured or user-specified list
        // In here, blocking any app with daily limit > 0
        auto it = policies_.find(user);
        if(it == policies_.end()) return;
        for(auto &kv : it->second.dailyLimitsSec) {
            if(kv.second > 0) blocker_.block(user, kv.first);
        }
        notifier_->notify(user, "Focus Mode", "Focus started - distracting apps blocked.");
    }

    void on_focus_end(const UserId &user, TimePoint ts) {
        // unblock what policy blocked earlier
        auto it = policies_.find(user);
        if(it == policies_.end()) return;
        for(auto &kv : it->second.dailyLimitsSec) {
            blocker_.unblock(user, kv.first);
        }
        notifier_->notify(user, "Focus Mode", "Focus ended - apps unblocked.");
    }

    // enforce dailt limit after adding usage (get daily usage from store_)
    void enforce_limits(const UserId &user, const  AppId &app) {
        auto pit = policies_.find(user);
        if(pit == policies_.end()) return ;
        auto &pol = pit->second;
        auto it = pol.dailyLimitsSec.find(app);
        if(it == pol.dailyLimitsSec.end()) return;
        int limit = it->second;
        if(limit <= 0) return;
        long long used = store_.get_daily(user, app);
        if(used >= limit) {
            if(pol.hardBlockOnLimit) {
                blocker_.block(user, app);
                notifier_->notify(user, "Limit Reached", "Daily limit reached for app '" + app + "'. App blocked.");
                // if user is currently foreground on that app, simulate it by notifying
                if(fgState_[user].active && fgState_[user].app == app) {
                    notifier_->notify(user, "App Closed", "App '" + app + "' closed bcause daily limit exceeded.");
                    fgState_[user].active = false;
                }
                // if user has a parent configured, notify parent
                auto pit2 = parentOf_.find(user);
                if(pit2 != parentOf_.end()) {
                    notifier_->notify(pit2->second, "Child Limit", "Child " + user + " reached limit for '" + app + "'.");
                }
            }
            else {
                // soft: just notify and allow
                notifier_->notify(user, "Limit Warning", "You reached the daily limit for '" + app + "'. Consider stopping.");
            }
        }
        else {
            // optionally notify when approaching limit (e.g., 90%)
            if(used * 10 >= (long long) limit * 9) {
                notifier_->notify(user, "Almost There", "You are at 90% of your daily limit for '" + app + "'.");
            }
        }
    }

    // daily rollover / reporting: in here, we run every rolloverIntervalSec_
    void daily_rollover_loop() {
        while (running_)
        {
            this_thread::sleep_for(chrono::seconds(rolloverIntervalSec_));
            // generate report for all users (snapshot)
            // In real app we would iterate users DB; in here, we iterate policies_ keys / fgState_
            unordered_set<UserId> users;
            for(auto &kv : policies_) users.insert(kv.first);
            for(auto &kv: fgState_) users.insert(kv.first);
            for(auto &u : users) {
                auto snap = store_.snapshot_user(u);
                stringstream ss;
                ss << "Daily usage report:\n";
                for(auto &p : snap) ss << p.first << " : " << p.second << " sec\n";
                notifier_->notify(u, "Daily Report", ss.str());
            }
            // reset daily counters (simulate next day)
            store_.reset_daily();
            // Also clear blockers tht were daily (not parental)
            // In here, we keep parental blocks; unblock all non-parental blocks
            // (In real system, we may track block origin)
            // Skip complex logic here for now

            // weekly: could aggregate weekly reports every 7 runs - ommited here
        } 
    }
};

// ----------- main (Demo simulation) -----------
int main() {
    WellbeingService svc;
    svc.start();

    // create users and policies
    string alice = "alice";
    string bob = "bob";         // bob is child of parent1
    string parent = "parent1";

    LimitPolicy polA;
    polA.dailyLimitsSec["YouTube"] = 10; // 10 seconds per day in this demo
    polA.dailyLimitsSec["Twitter"] = 15;
    polA.hardBlockOnLimit = true;
    svc.set_policy(alice, polA);

    LimitPolicy polB;
    polB.dailyLimitsSec["YouTube"] = 8;
    polB.hardBlockOnLimit = true;
    svc.set_policy(bob, polB);
    svc.set_parent(bob, parent);

    // small notifier to parent as well (parent is a user in the system)
    // (ConsoleNotifier used globally; parent will get notifications via same channel)

    // simulate app usageevents on background threads
    auto simulate_user = [&](const UserId &user, const vector<pair<AppId, int>> sequence) {
        // sequence: (app, foregroundDurationSec)
        for(auto &step : sequence) {
            AppId app = step.first;
            int dur = step.second;
            svc.publish_event({EventType::APP_FOREGROUND, user, app, now()});
            // sleep to simulate being in the app
            this_thread::sleep_for(chrono::seconds(dur));
            svc.publish_event({EventType::APP_BACKGROUND, user, app, now()});
            // short pause between apps
            this_thread::sleep_for(chrono::milliseconds(500));
        }
    };

    thread t1(simulate_user, alice, vector<pair<AppId, int>>{
        {"YouTube", 4}, {"Twitter", 7}, {"YouTube", 7} // second YouTube exceeds Alice limit (10s)
    });

    thread t2(simulate_user, bob, vector<pair<AppId, int>>{
        {"YouTube", 5}, {"YouTube", 5}, {"YouTube", 2} // will exceed bob's 8s limit
    });

    // simulate focus session for Alice in the middle
    thread tFocus([&](){
        this_thread::sleep_for(chrono::seconds(3));
        svc.publish_event({EventType::FOCUS_START, alice, "", now()});
        this_thread::sleep_for(chrono::seconds(6));
        svc.publish_event({EventType::FOCUS_END, alice, "", now()});
    });

    // run for a while
    t1.join();
    t2.join();
    tFocus.join();

    // wait enough for daily rollover to fire at least once
    this_thread::sleep_for(chrono::seconds(25));

    svc.stop();
    cout << "Demo finished\n";

    return 0;
}
```
