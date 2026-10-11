
from agents.banking_agent import (
    get_account_balance,
    get_transactions,
    analyze_spending,
)
from agents.risk_agent import detect_suspicious_transactions
from agents.credit_agent import check_loan_eligibility
from services.llm_service import classify_request


def handle_request(request: str, customer_id: int = 1):
    """
    Supervisor Agent:
    Uses Gemini to classify the request, then delegates
    to predefined Python agents and tools.
    """

    if not request or not request.strip():
        return {
            "message": "Please enter a banking-related request.",
            "agent_used": [],
        }

    try:
        classification = classify_request(request)
        intents = classification.get("intents", ["unknown"])

    except Exception as error:
        return {
            "message": (
                "I couldn't process your request using Gemini. "
                "Please try again."
            ),
            "error": str(error),
            "agent_used": [],
        }

    if "unknown" in intents or not intents:
        return {
            "message": (
                "I couldn't identify your request. You can ask about "
                "account balance, transactions, spending, suspicious "
                "activity, or loan eligibility."
            ),
            "agent_used": [],
        }

    results = {}
    agents_used = []

    # Banking Agent: Account balance
    if "account_balance" in intents:
        results["account_balance"] = get_account_balance(customer_id)
        agents_used.append("Banking Agent")

    # Banking Agent: Transaction history
    if "transactions" in intents:
        results["transactions"] = get_transactions(customer_id)
        if "Banking Agent" not in agents_used:
            agents_used.append("Banking Agent")

    # Banking Agent: Spending analysis
    if "spending_analysis" in intents:
        results["spending_analysis"] = analyze_spending(customer_id)
        if "Banking Agent" not in agents_used:
            agents_used.append("Banking Agent")

    # Risk Agent: Suspicious transaction detection
    if "risk_assessment" in intents:
        results["risk_assessment"] = (
            detect_suspicious_transactions(customer_id)
        )
        agents_used.append("Risk Agent")

    # Credit Agent: Loan eligibility assessment
    if "loan_assessment" in intents:
        results["loan_assessment"] = (
            check_loan_eligibility(customer_id)
        )
        agents_used.append("Credit Agent")

    results["agent_used"] = agents_used

    return results
