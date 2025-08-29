# Simple Banking System
## 1. Features Required
- Account management
  - create, update, close accounts
  - different account types (Savings, Current)
- Transaction management
  - Deposit, Withdraw, Transfer
  - Transaction hisitory
  - Notifications
- User management
  - Add customers, authenticate, link accounts
- Extensibility
  - Loan management (request, approve and repay loans)
  - Suooprt for new account types (e.g. Fixed Deposit)
  - Support for new transaction types (e.g. Bill Payments)

## 2. Design Patterns used
- Factory -> For creating account types
- Strategy -> For different transaction behaviors (deposit, withdraw, transfer)
- Observer -> Notify customers on transactions (SMS/Email)
- Singleton -> Bank system as a single instance

## 3. Design Highlights
- **Separations of Concerns**: `Account`, `Customer`, `Transaction`, `BankSystem`
- **Polymorphism**: `Account` base class with `SavingsAccount` and `CurrentAccount`
- **Extensibility**: Easy to add new accounts/transactions

- ## Implementation
- ```cpp
  #include <string>
#include <memory>
#include <stdexcept>
#include <vector>
#include <iostream>
#include <unordered_map>

using namespace std;

using CustomerId = int;
using AccountId = int;

enum class AccountType {
    SAVINGS,
    CURRENT,
};

// ----------- Base Classes -----------
class Account {
protected:
    AccountId accountId;
    double balance;
public:
    Account(AccountId id, double initial) : accountId(id), balance(initial) {}
    virtual ~Account() = default;

    AccountId getId() const { return accountId; }
    double getBalance() const { return balance; }

    virtual void deposit(double amt) { balance += amt; }
    virtual bool withdraw(double amt) {
        if(balance >= amt) {
            balance -= amt;
            return true;
        }
        return false;
    }

    virtual AccountType getType() const = 0;
};

class SavingsAccount : public Account {
public:
    SavingsAccount(AccountId id, double initial) : Account(id, initial) {}
    AccountType getType() const { return AccountType::SAVINGS; }
};

class CurrentAccount : public Account {
public:
    CurrentAccount(AccountId id, double initial) : Account(id, initial) {}
    AccountType getType() const { return AccountType::CURRENT; }
};

// ----------- Factory Pattern -----------
class AccountFactory {
public:
    static shared_ptr<Account> createAccount(const AccountType &type, AccountId id, double initial) {
        if(type == AccountType::SAVINGS) return make_shared<SavingsAccount>(id, initial);
        if(type == AccountType::CURRENT) return make_shared<CurrentAccount>(id, initial);
        throw runtime_error("Invalid account type");
    }
};

// ----------- Customer -----------
class Customer {
    CustomerId customerId;
    string name;
    vector<shared_ptr<Account>> accounts;
public:
    Customer(CustomerId id, string n) : customerId(id), name(move(n)) {}

    string getName() const {return name; }
    CustomerId getId() const { return customerId; }

    void addAccount(shared_ptr<Account> acc) { accounts.push_back(acc); }
    const vector<shared_ptr<Account>>& getAccounts() const { return accounts; }
};

// ----------- Transaction (Strategy Pattern) -----------
class Transaction {
public:
    virtual ~Transaction() = default;
    virtual void execute(Account &Acc, double amt) = 0; // retrurn type could be bool
};

class Deposit : public Transaction {
public:
    void execute(Account &acc, double amt) override {
        acc.deposit(amt);
        cout << "Deposited " << amt << " into Account " << acc.getId() << "\n";
    }
};

class Withdraw : public Transaction {
public:
    void execute(Account &acc, double amt) override {
        if(acc.withdraw(amt)) 
            cout << "Withdrew " << amt << " from Account " << acc.getId() << "\n";
        else
            cout << "Insufficient funds in Account " << acc.getId() << "\n";
    }
};

class Transfer {
public:
    void execute(Account &from, double amt, Account &to) {
        if(from.withdraw(amt)) {
            to.deposit(amt);
            cout << "Transferred " << amt << " from Accout "
                 << from.getId() << " to Account " << to.getId() << "\n";
        } else {
            cout << "Insufficient funds to transfer\n";
        }
    }
};

// ----------- Notification (Observer Pattern) -----------
class INotifier {
public:
    virtual ~INotifier() = default;
    virtual void send(const string &recipient, const string &msg) = 0;
};

class EmailNotifier : public INotifier {
public:
    void send(const string &recipient, const string &msg) override {
        cout << "[EMAIL to " << recipient << "]: " << msg << "\n";
    }
};

class ConsoleNotifier : public INotifier {
public:
    void send(const string &recipient, const string &msg) override {
        cout << "[CONSOLE to " << recipient << "]: " << msg << "\n";
    }
};

class Subscription {
    string recipient; // e.g. email id, device id username etc
    shared_ptr<INotifier> notifier;
public:
    Subscription(string r, shared_ptr<INotifier> n)
        : recipient(move(r)), notifier(move(n)) {}
    
    void notify(const string &msg) {
        notifier->send(recipient, msg);
    }
};

// ----------- Banking System (Singleton) -----------
class BankingSystem {
    unordered_map<CustomerId, Customer> customers_;
    unordered_map<AccountId, vector<Subscription>> subscribers_;
    int nextAccountId = 101;

    BankingSystem() = default;

    BankingSystem(const BankingSystem&) = delete;
    BankingSystem &operator=(BankingSystem&) = delete;
    BankingSystem(BankingSystem&&) = delete;
    BankingSystem& operator=(BankingSystem&&) = delete;

public:
    static BankingSystem& getInstance() {
        static BankingSystem instance;
        return instance;
    }

    Customer& addCustomer(CustomerId id, const string &name) {
        customers_.emplace(id, Customer(id, name));
        // return customers_[id];
        return customers_.at(id);
    }

    shared_ptr<Account> openAccount(CustomerId id, AccountType type, double initial) {
        auto &cust = customers_.at(id);
        auto acc = AccountFactory::createAccount(type, nextAccountId++, initial);
        cust.addAccount(acc);
        return acc;
    }

    void subscribe(AccountId id, const Subscription &sub) {
        subscribers_[id].push_back(sub);
    }

    void notify(AccountId id, const string &msg) {
        auto it = subscribers_.find(id);
        if(it != subscribers_.end()) {
            for(auto &sub : subscribers_[id])
                sub.notify(msg);
        }
    }
};

// ----------- main (Demo) -----------
int main() {
    auto &bank = BankingSystem::getInstance();
    
    auto email = make_shared<EmailNotifier>();
    auto console = make_shared<ConsoleNotifier>();
    
    // Add customer
    Customer &c1 = bank.addCustomer(1, "Alice");

    // Open Accounts
    auto acc1 = bank.openAccount(1, AccountType::CURRENT, 1000);
    auto acc2 = bank.openAccount(1, AccountType::SAVINGS, 2000);

    // Subscribe to notifications
    bank.subscribe(acc1->getId(), Subscription("alice@example.com", email));
    bank.subscribe(acc1->getId(), Subscription("console@alice", console));
    bank.subscribe(acc2->getId(), Subscription("console@alice", console));

    // Transactions
    Deposit d;
    d.execute(*acc1, 500);
    bank.notify(acc1->getId(), "Deposit completed");

    Withdraw w;
    w.execute(*acc2, 300);
    bank.notify(acc2->getId(), "Withdraw completed");

    Transfer t;
    t.execute(*acc1, 50, *acc2);
    bank.notify(acc1->getId(), "Transfer From completed");
    bank.notify(acc2->getId(), "Transfer To completed");

    return 0;
 }
- ```

  #### Sample output
  ```
  Deposited 500 into Account 101
[EMAIL to alice@example.com]: Deposit completed
[CONSOLE to console@alice]: Deposit completed
Withdrew 300 from Account 102
[CONSOLE to console@alice]: Withdraw completed
Transferred 50 from Accout 101 to Account 102
[EMAIL to alice@example.com]: Transfer From completed
[CONSOLE to console@alice]: Transfer From completed
[CONSOLE to console@alice]: Transfer To completed
  ```
