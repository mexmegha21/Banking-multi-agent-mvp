
from agents.supervisor import handle_request


requests = [
    "How much money do I have left?",
    "Show me my recent transactions",
    "Where is most of my money going?",
    "Did anything unusual happen in my account?",
    "Can I qualify for a loan?",
    "Check my balance and flag suspicious transactions",
    "Tell me a joke",
]

for request in requests:
    print("\n" + "=" * 55)
    print("USER:", request)

    result = handle_request(request)

    print("SUPERVISOR RESULT:")
    print(result)
