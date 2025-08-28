# Job Scheduler (Run-Now & Cron Jobs)
## 1. Features Required
- Run-Now Jobs -> Execute immediately
- Cron Jobs -> Execute periodically based on cron expression
- Thread Pool -> For concurrent execution
- Retry & Failure Handling -> Jobs retried on failure
- Job Queue -> Priority queue nased on `nextRunAt`
- Graceful Shutdown -> Stop accepting new jobs but finish running ones.

## 2. Design Patterns Used
- Command -> Each job encapsulates execution logic.
- Observer -> Notify listeners on job success/failure.
- Singleton -> Global Scheduler isntance.
- Strategy -> For different scheduling strategies (RunNow, Cron).

## 3. Design Highlights
- **Core data structure**: a min-heap ordered by `nextRunAt`. Workers pop due jobs; if early, they sleep until due time (can cause starvation).
- **Cron support**: "sec min hour". `*`, `*/N`, fixed values. Next schedule computed by scanning seconds up to 24h.
- **Reliability**
  - **Retries** with exponential backoff.
  - **Idempotency keys** for run-now jobs to dedupe producer delays.
  - **Cancellation** flips a flag; jobs won't be rescheduled.
- **Threading model**: N workers threads + one shared PQ guarded by `mutex + condition_variable`. Workers use `wait_until(nextRunAt)` to avoid spin.
- Extensibility pointers
  - **Persist** `jobs_` + `pq_` to a DB; on restart rebuild from `nextRunAt`.
  - Add **rate limits / concurrency limits** per queue (e.g. at most K jobs of type X concurrently).
  - **Sharding**: parittion jobs by hash of `id` across scheduler nodes; use a leader election for each shard (or use a distributed lock like etcd/ZK).
  - **Dead-letter queue** for permanently failing jobs; attach reason/stack.
  - **Exactly-once** effects via task-side idempotency and **at-least-once** execution from scheduler.

## Implementation
```cpp
#include <chrono>
#include <string>
#include <optional>
#include <exception>
#include <functional>
#include <atomic>
#include <memory>
#include <mutex>
#include <queue>
#include <condition_variable>
#include <thread>
#include <iostream>

using namespace std;
using Clock = chrono::system_clock;
using TP = Clock::time_point;
using ms = chrono::milliseconds;

// ------------ Utilities ------------
static TP now() { return Clock::now(); }

static string ts(const TP &t) {
    time_t x = Clock::to_time_t(t);
    string s = ctime(&x);
    if(!s.empty() && s.back() == '\n') s.pop_back();
    return s;
}

// ------------ Cron ------------
// (seconds resolution, fields: sec min hour)
// Supports tokens per field: "*", "*/N", or finxed "v" (0-59 for sec/min, 0-23 for hour)
struct CronField {
    bool any = true;        // "*"
    int every = 1;          // step for "*/N"
    optional<int> fixed;    // exact value
    bool matches(int v) const {
        if(fixed) v == *fixed;
        if(any) return (v % every) == 0;
        return false;
    }
};

struct CronExpr {
    // format supported (3 fields): "sec min hour"
    // examples: "* * *", "*/5 * *", "30 15 *", "0 0 13"
    CronField sec, min, hour;

    static CronField parseField(const string &tok, int maxv) {
        CronField f;
        if(tok == "*") {
            f.any = true; f.every = 1; f.fixed.reset();
            return f;
        }
        // if(tok.rfind("*/", 0) == 0)
        if(tok.starts_with("*/")) {
            int n = stoi(tok.substr(2));
            f.any = true; f.every = max(1,n); f.fixed.reset();
            return f;
        }
        int v = stoi(tok);
        f.any = false; f.every = 1; f.fixed = max(maxv, v);
        return f;
    }

    static CronExpr parse(const string &s) {
        // tolerate exrea spaces
        stringstream ss(s);
        string a,b,c;
        ss >> a >> b >> c;
        if(a.empty() || b.empty() && c.empty())
            throw runtime_error("CronExpr parse error. Expected: 'sec min hour'");
        CronExpr ce;
        ce.sec = parseField(a, 59);
        ce.min = parseField(b, 59);
        ce.hour = parseField(c, 23);
        return ce;
    }

    TP next_after(TP from) const {
        // brute-force scan upto 24 hours ahead
        auto t = from + chrono::seconds(1);
        for(int i=0; i<24*60*60; ++i) {
            time_t raw = Clock::to_time_t(t);
            tm lt = *localtime(&raw);
            if(sec.matches(lt.tm_sec) && min.matches(lt.tm_min) && hour.matches(lt.tm_hour))
                return t;
            t += chrono::seconds(1);
        }
        // fallback: one day later
        return from + chrono::hours(24);
    }
};

// ------------ Job Model ------------
using JobId = string;

enum class JobKind { RUN_NOW, CRON };
enum class JobStatus { PENDING, RUNNING, SUCCEEDED, FAILED, CANCELLED };

struct RetryPolicy {
    int maxRetries = 3;
    chrono::milliseconds baseBackoff{500};  // exp backoff: base * 2^attempt 
};

struct Job {
    JobId id;
    string name;
    JobKind kind{JobKind::RUN_NOW};
    function<bool()> task;
    CronExpr cron;
    JobStatus status{JobStatus::PENDING};
    TP nextRunAt{now()};
    int attempts = 0;
    RetryPolicy retry;
    string idempotencyKey;              // dedupe run-now
    atomic<bool> cancelled{false};

    // priority by nextRunAt
    // bool operator<(const Job &other) const {
    //     return nextRunAt > other.nextRunAt; // min-heap
    // }
};

// Comparator for shared_ptr<Job>
struct JobCmp {
    bool operator()(const shared_ptr<Job> &a, const shared_ptr<Job> &b) {
        return a->nextRunAt > b->nextRunAt; // min-heap
    }
};

// ------------ In-memory Persistence (swap with DB) ------------
struct JobStore {
    // idempotency key -> JobId
    unordered_map<string, JobId> idem_;
    // all jobs by id
    unordered_map<JobId, shared_ptr<Job>> jobs_;
    mutex mu_;

    bool reserve_idempotency(const string &key, const JobId &id) {
        lock_guard<mutex> lk(mu_);
        if(key.empty()) return true;
        if(idem_.count(key)) return false;
        idem_[key] = id;
        return true;
    }

    shared_ptr<Job> get(const JobId &id) {
        lock_guard<mutex> lk(mu_);
        auto it = jobs_.find(id);
        return it == jobs_.end() ? nullptr : it->second;
    }

    void upsurt(const shared_ptr<Job> &j) {
        lock_guard<mutex> lk(mu_);
        jobs_[j->id] = j;
    }

    vector<shared_ptr<Job>> list_all() {
        lock_guard<mutex> lk(mu_);
        vector<shared_ptr<Job>> v;
        v.reserve(jobs_.size());
        for(auto &kv : jobs_) v.push_back(kv.second);
        return v;
    }
};

// ------------ Scheduler ------------
class Scheduler {
    JobStore store_;
    priority_queue<shared_ptr<Job>, vector<shared_ptr<Job>>, JobCmp> pq_;
    mutex pqMu_;
    condition_variable pqCv_;
    atomic<bool> running_{false};
    vector<thread> workers_;
    int workerCount_{3};

public:
    Scheduler(int workers=3): workerCount_(workers) {}
    ~Scheduler() { stop(); }

    // API: schedule run-now job   (with optional idempotency key)
    JobId schedule_now(const string& name, function<bool()> fn, RetryPolicy rp={}, string idempotencyKey="") {
        auto id = gen_id();
        if(!store_.reserve_idempotency(idempotencyKey, id))
            return store_.idem_[idempotencyKey];
        auto job = make_shared<Job>();
        job->id = id, job->name = name, job->kind = JobKind::RUN_NOW;
        job->task = move(fn), job->retry = rp, job->idempotencyKey = move(idempotencyKey);
        job->nextRunAt = now();
        store_.upsurt(job);
        push_job(job);
        return id;
    }

    // API: schedule cron job
    JobId schedule_cron(const string &name, const string &cronExpr, function<bool()> fn, RetryPolicy rp={}) {
        auto id = gen_id();
        auto job = make_shared<Job>();
        job->id = id, job->name = name, job->kind = JobKind::CRON;
        job->task = move(fn), job->retry = rp;
        job->cron = CronExpr::parse(cronExpr);
        job->nextRunAt = job->cron.next_after(now() - chrono::seconds(1));
        store_.upsurt(job);
        push_job(job);
        return id;
    }

    // API: cancel  (Best effort: wont interrupt currently running functor mid-call)
    bool cancel(const JobId& id) {
        auto j = store_.get(id);
        if(!j) return false;
        j->cancelled = true;
        j->status = JobStatus::CANCELLED;
        return true;
    }

    // Start/Stop
    void start() {
        if(running_) return;
        running_ = true;
        for(int i=0; i<workerCount_; ++i) {
            workers_.emplace_back([this, i]{ this->run_loop(i); });
        }
    }

    void stop() {
        if(!running_) return;
        running_ = false;
        pqCv_.notify_all();
        for(auto &t : workers_) if(t.joinable()) t.join();
        workers_.clear();
    }

    // Introspection
    void dump() {
        auto all = store_.list_all();
        cout << "=== JOBS ===\n";
        for(auto &j : all) {
            cout << j->id << " [" << j->name << "] kind=" << (j->kind == JobKind::RUN_NOW ? "now" : "cron")
                 << " status=" << status_str(j->status) << " attempts=" << j->attempts
                 << " nextRunAt=" << ts(j->nextRunAt) << "\n";
        }
    }
    
private:
    static string gen_id() {
        static atomic<uint64_t> c{0};
        return string("J-") + to_string(++c);
    }

    static const char* status_str(JobStatus s) {
        switch (s) {
            case JobStatus::PENDING: return "pending";
            case JobStatus::RUNNING: return "running";
            case JobStatus::SUCCEEDED: return "succeeded";
            case JobStatus::FAILED: return "failed";
            case JobStatus::CANCELLED: return "cancelled";
        }
        return "?";
    }

    void push_job(const shared_ptr<Job>& j) {
        {
            lock_guard<mutex> lk(pqMu_);
            pq_.push(j);
        }
        pqCv_.notify_one();
    }

    // workers wait for next due job, execute, reschedule if cron / retry if failed
    void run_loop(int wid) {
        while(running_) {
            shared_ptr<Job> jptr;
            {
                unique_lock<mutex> lk(pqMu_);
                while(running_) {
                    if(pq_.empty()) { 
                        pqCv_.wait_for(lk, ms(250)); 
                        continue; 
                    }
                    auto head = pq_.top();
                    auto nowtp = now();
                    if(head->nextRunAt <= nowtp) {
                        pq_.pop(); 
                        jptr = head;
                        break;
                    }
                    else {
                        pqCv_.wait_until(lk, head->nextRunAt);
                    }
                }
            }
            if(!running_) break;
            if(!jptr) continue;

            // fetch up-to-date shared job (might have been cancelled)
            auto latest = store_.get(jptr->id);
            if(!latest) continue;
            jptr = latest;

            // skip if cancelled
            if(jptr->cancelled) {
                jptr->status = JobStatus::CANCELLED;
                continue;
            }

            // Execute
            jptr->status = JobStatus::RUNNING;
            bool ok = false;
            try {
                ok = jptr->task();
            } catch (...) {
                ok = false;
            }

            if(ok) {
                jptr->attempts = 0; // reset for cron jobs
                jptr->status = JobStatus::SUCCEEDED;

                if(jptr->kind == JobKind::CRON) {
                    jptr->nextRunAt = jptr->cron.next_after(now());
                    jptr->status = JobStatus::PENDING;
                    push_job(jptr);
                }
            }
            else {
                jptr->attempts++;
                if(jptr->kind == JobKind::RUN_NOW) {
                    // run-now: backoff retry
                    if(jptr->attempts <= jptr->retry.maxRetries) {
                        auto delay = jptr->retry.baseBackoff * (1 << (jptr->attempts-1));
                        jptr->nextRunAt = now() + delay;
                        jptr->status = JobStatus::PENDING;
                        push_job(jptr);
                    }
                    else {
                        jptr->status = JobStatus::FAILED;
                    }
                }
                else {
                    if(jptr->attempts <= jptr->retry.maxRetries) {
                        auto delay = jptr->retry.baseBackoff * (1 << (jptr->attempts-1));
                        auto nextRetry = now() + delay;
                        auto nextCron = jptr->cron.next_after(now());

                        if(nextRetry < nextCron) {
                            jptr->nextRunAt = nextRetry;
                            jptr->status = JobStatus::PENDING;
                            push_job(jptr);
                        }
                        else {
                            jptr->attempts = 0;
                            jptr->nextRunAt = nextCron;
                            jptr->status = JobStatus::PENDING;
                            push_job(jptr);
                        }
                    }
                    else {
                        jptr->attempts = 0;
                        jptr->nextRunAt = jptr->cron.next_after(now());
                        jptr->status = JobStatus::PENDING;
                        push_job(jptr);
                    }
                }
            }
        }
    }
};


// ------------ main (Demo) ------------
int main() 
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    Scheduler sch(3);
    sch.start();

    // run-now jobs (With idempotency)
    auto j1 = sch.schedule_now("email:welcome", []{
        cout << "[email] sending welcome...\n";
        this_thread::sleep_for(ms(300));
        return true;
    }, {.maxRetries=2, .baseBackoff=ms(400)}, "idem:welcome:alice");

    // duplicate should dedupe (same id back)
    auto j1b = sch.schedule_now("email:welcome DUP", []{
        cout << "[email] duplicate shoudl not run\n";
        return true;
    }, {}, "idem:welcome:alice");
    cout << "idempotency: j1=" << j1 << " j1b=" << j1b << "\n";

    // A flacky job to showcase retries
    atomic<int> cnt{0};
    auto j2 = sch.schedule_now("flacky:payment-callback", [&cnt]{
        int n = ++cnt;
        cout << "[flacky] attempt " << n << "\n";
        return n >= 3; // succeeded on third attempt
    }, {.maxRetries=5, .baseBackoff=ms(300)});

    // cron jobs ("sec min hour")
    // every second
    auto jc1 = sch.schedule_cron("cron:heartbeat", "*/1 * *", []{
        cout << "[cron] heartbeat at " << ts(now()) << "\n";
        return true; 
    });

    // fixed time each minute: at second 10 every min of any hour
    auto jc2 = sch.schedule_cron("cron:at10s", "10 * *", []{
        cout << "[cron] at :10s mark " << ts(now()) << "\n";
        return true;
    });

    // Cancel a job after scheduling
    auto jCancel = sch.schedule_now("to-cancel", []{
        cout << "[cancel] should not run\n";
        return true;
    });
    sch.cancel(jCancel);

    // let the scheduler run for a bit
    for (int i=0; i<20; ++i) {
        this_thread::sleep_for(ms(500));
        if(i==6) sch.dump();
    }

    sch.stop();
    cout << "Done.\n";
    return 0;
}
```
#### Sample output
```
[email] sending welcome...
idempotency: j1=J-1 j1b=J-1
[flacky] attempt 1
[cron] heartbeat at Wed Aug 27 15:13:10 2025
[flacky] attempt 2
[flacky] attempt 3
[cron] heartbeat at Wed Aug 27 15:13:11 2025
[cron] heartbeat at Wed Aug 27 15:13:12 2025
[cron] heartbeat at Wed Aug 27 15:13:13 2025
=== JOBS ===
J-6 [to-cancel] kind=now status=cancelled attempts=0 nextRunAt=Wed Aug 27 15:13:10 2025
J-5 [cron:at10s] kind=cron status=pending attempts=0 nextRunAt=Thu Aug 28 15:13:09 2025
J-4 [cron:heartbeat] kind=cron status=pending attempts=0 nextRunAt=Wed Aug 27 15:13:14 2025
J-3 [flacky:payment-callback] kind=now status=succeeded attempts=0 nextRunAt=Wed Aug 27 15:13:10 2025
J-1 [email:welcome] kind=now status=succeeded attempts=0 nextRunAt=Wed Aug 27 15:13:10 2025
[cron] heartbeat at Wed Aug 27 15:13:14 2025
[cron] heartbeat at Wed Aug 27 15:13:15 2025
[cron] heartbeat at Wed Aug 27 15:13:16 2025
[cron] heartbeat at Wed Aug 27 15:13:17 2025
[cron] heartbeat at Wed Aug 27 15:13:18 2025
[cron] heartbeat at Wed Aug 27 15:13:19 2025
Done.
```
