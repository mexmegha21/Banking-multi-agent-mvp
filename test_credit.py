
from agents.credit_agent import check_loan_eligibility

result = check_loan_eligibility(1)

print("LOAN ELIGIBILITY ASSESSMENT")
print("-" * 30)
print("Customer:", result.get("customer_name", "Unknown"))
print("Monthly Income:", result.get("monthly_income", "N/A"))
print("Credit Score:", result.get("credit_score", "N/A"))
print("Meets Demo Criteria:", result["eligible"])
print("Result:", result["message"])

print("\nReasons:")
for reason in result["reasons"]:
    print("-", reason)
