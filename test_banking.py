
from agents.banking_agent import (
    get_account_balance,
    get_transactions,
    analyze_spending
)

customer_id = 1

print("ACCOUNT BALANCE")
print(get_account_balance(customer_id))

print("\nRECENT TRANSACTIONS")
for transaction in get_transactions(customer_id):
    print(transaction)

print("\nSPENDING ANALYSIS")
for category in analyze_spending(customer_id):
    print(category)
