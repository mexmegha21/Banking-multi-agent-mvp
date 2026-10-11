
from services.llm_service import ask_gemini


try:
    response = ask_gemini(
        "You are an assistant for a simulated banking application. "
        "In two sentences, explain what a Banking Agent does. "
        "Do not claim to access any real bank account."
    )

    print("GEMINI CONNECTION SUCCESSFUL")
    print("-" * 35)
    print(response)

except Exception as error:
    print("GEMINI CONNECTION FAILED")
    print(type(error).__name__ + ":", error)
