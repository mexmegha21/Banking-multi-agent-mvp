import json
import os
import re

from dotenv import load_dotenv
from google import genai


# Load environment variables from the project root
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

MODEL_NAME = "gemini-3.6-flash"


ALLOWED_INTENTS = {
    "account_balance",
    "transactions",
    "spending_analysis",
    "risk_assessment",
    "loan_assessment",
    "unknown",
}


def get_gemini_client():
    """Create the Gemini API client."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing from the .env file."
        )

    return genai.Client(api_key=api_key)


def ask_gemini(prompt: str) -> str:
    """Send a prompt to Gemini and return its response."""

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    response = get_gemini_client().models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text.strip()


def normalize_text(request: str) -> str:
    """Normalize user input for intent matching."""

    text = request.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text


def contains_phrase(text: str, phrases: list) -> bool:
    """Check whether any complete phrase exists in the text."""

    return any(
        re.search(
            r"\b" + re.escape(phrase) + r"\b",
            text,
        )
        for phrase in phrases
    )


def classify_with_rules(request: str) -> list:
    """Identify banking intents without calling Gemini."""

    text = normalize_text(request)
    intents = []

    # 1. Account balance
    balance_phrases = [
        "balance",
        "money left",
        "money is left",
        "how much money",
        "how much money is left",
        "how much money do i have",
        "how much do i have",
        "how much is left",
        "how much do i have left",
        "money do i have",
        "money do i have left",
        "available money",
        "cash left",
        "funds available",
        "remaining balance",
        "remaining money",
        "account balance",
        "check my balance",
        "show my balance",
        "my account balance",
    ]

    if contains_phrase(text, balance_phrases):
        intents.append("account_balance")

    # 2. Transaction history
    transaction_phrases = [
        "transaction",
        "transactions",
        "transaction history",
        "recent transactions",
        "latest transactions",
        "show transactions",
        "list transactions",
        "payment history",
        "recent payments",
        "show payments",
        "payments i made",
        "my transactions",
    ]

    if contains_phrase(text, transaction_phrases):
        intents.append("transactions")

    # 3. Spending analysis
    spending_phrases = [
        "spending",
        "spent",
        "expenses",
        "expense",
        "spending analysis",
        "spend analysis",
        "spending by category",
        "where is my money going",
        "where does my money go",
        "where is most of my money going",
        "money spent",
        "analyze my spending",
    ]

    if contains_phrase(text, spending_phrases):
        intents.append("spending_analysis")

    # 4. Suspicious activity and risk
    risk_phrases = [
        "suspicious",
        "fraud",
        "risk",
        "unusual",
        "flagged transaction",
        "suspicious activity",
        "possible fraud",
        "check for fraud",
        "risk assessment",
    ]

    if contains_phrase(text, risk_phrases):
        intents.append("risk_assessment")

    # 5. Loan eligibility
    loan_phrases = [
        "loan",
        "eligibility",
        "credit score",
        "qualify for",
        "loan eligibility",
        "eligible for a loan",
        "loan approval",
    ]

    if contains_phrase(text, loan_phrases):
        intents.append("loan_assessment")

    # Return unique intents in their original order
    return list(dict.fromkeys(intents))


def classify_request(request: str) -> dict:
    """
    Classify banking requests using local rules first.
    Use Gemini only when no rule matches.
    """

    if not request or not request.strip():
        return {
            "intents": ["unknown"],
            "method": "fallback",
        }

    # First attempt: local rule-based classification
    rule_intents = classify_with_rules(request)

    if rule_intents:
        return {
            "intents": rule_intents,
            "method": "rules",
        }

    # Second attempt: Gemini classification
    prompt = f"""
You are an intent classifier for a simulated banking application.

Select applicable intents from this list:
- account_balance
- transactions
- spending_analysis
- risk_assessment
- loan_assessment
- unknown

Return only valid JSON in this format:
{{"intents": ["unknown"]}}

Instructions:
- Return all applicable intents.
- Use unknown for unrelated requests.
- Do not answer the banking question.
- Do not invent account information.

User request: {json.dumps(request)}
"""

    try:
        response = get_gemini_client().models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        if not response.text:
            return {
                "intents": ["unknown"],
                "method": "fallback",
            }

        response_text = response.text.strip()

        # Remove optional Markdown code fences
        if response_text.startswith("```"):
            response_text = re.sub(
                r"^```(?:json)?\s*",
                "",
                response_text,
            )
            response_text = re.sub(
                r"\s*```$",
                "",
                response_text,
            )

        result = json.loads(response_text)
        raw_intents = result.get("intents", [])

        if not isinstance(raw_intents, list):
            return {
                "intents": ["unknown"],
                "method": "fallback",
            }

        valid_intents = list(dict.fromkeys(
            intent
            for intent in raw_intents
            if isinstance(intent, str)
            and intent in ALLOWED_INTENTS
            and intent != "unknown"
        ))

        if valid_intents:
            return {
                "intents": valid_intents,
                "method": "gemini",
            }

        return {
            "intents": ["unknown"],
            "method": "gemini",
        }

    except Exception as error:
        print(
            "Gemini classification unavailable: "
            f"{type(error).__name__}"
        )

        return {
            "intents": ["unknown"],
            "method": "fallback",
        }