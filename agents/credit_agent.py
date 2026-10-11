
from database.db import get_connection


def check_loan_eligibility(customer_id: int):
    """Evaluate sample customer data against demo criteria."""

    with get_connection() as conn:
        customer = conn.execute(
            """
            SELECT name, monthly_income, credit_score
            FROM customers
            WHERE customer_id = ?
            """,
            (customer_id,)
        ).fetchone()

    if customer is None:
        return {
            "eligible": False,
            "message": "Customer not found.",
            "reasons": ["No customer record exists."]
        }

    income = customer["monthly_income"]
    credit_score = customer["credit_score"]

    reasons = []

    if income < 25000:
        reasons.append("Monthly income is below ₹25,000.")

    if credit_score < 700:
        reasons.append("Credit score is below 700.")

    eligible = len(reasons) == 0

    if eligible:
        message = (
            "The customer meets the configured demo criteria. "
            "This is not a loan approval."
        )
        reasons.append("All configured demo criteria are met.")
    else:
        message = (
            "The customer does not meet all configured "
            "demo criteria."
        )

    return {
        "customer_name": customer["name"],
        "monthly_income": income,
        "credit_score": credit_score,
        "eligible": eligible,
        "message": message,
        "reasons": reasons,
    }
