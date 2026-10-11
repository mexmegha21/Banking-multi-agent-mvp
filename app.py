
import streamlit as st
import pandas as pd

from database.seed_data import seed_database
from agents.banking_agent import (
    get_account_balance,
    get_transactions,
    analyze_spending,
)
from agents.risk_agent import detect_suspicious_transactions
from agents.credit_agent import check_loan_eligibility
from agents.supervisor import handle_request


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AI Banking Assistant",
    page_icon="🏦",
    layout="wide",
)

CUSTOMER_ID = 1


# --------------------------------------------------
# Initialize simulated database
# --------------------------------------------------

seed_database()


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("🏦 AI Multi-Agent Banking Assistant")

st.caption(
    "Simulated banking environment | "
    "Python agents + Gemini AI | No real bank connection"
)

st.info(
    "Demo only: account information and financial assessments "
    "use sample data. Flagged transactions require review and "
    "do not automatically indicate fraud."
)


# --------------------------------------------------
# Load dashboard data
# --------------------------------------------------

try:
    balance = get_account_balance(CUSTOMER_ID)
    transactions = get_transactions(CUSTOMER_ID)
    spending = analyze_spending(CUSTOMER_ID)
    risk_results = detect_suspicious_transactions(CUSTOMER_ID)
    loan_result = check_loan_eligibility(CUSTOMER_ID)

except Exception as error:
    st.error(f"Could not load the simulated banking data: {error}")
    st.stop()


# --------------------------------------------------
# Navigation
# --------------------------------------------------

overview_tab, transactions_tab, risk_tab, loan_tab, assistant_tab = (
    st.tabs([
        "📊 Overview",
        "💳 Transactions",
        "🛡️ Risk Monitoring",
        "🏠 Loan Assessment",
        "🤖 AI Assistant",
    ])
)


# --------------------------------------------------
# Overview
# --------------------------------------------------

with overview_tab:
    st.subheader("Account Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Account Balance",
        f"₹{balance:,.2f}",
    )

    col2.metric(
        "Recent Transactions",
        len(transactions),
    )

    col3.metric(
        "Flagged Transactions",
        len(risk_results),
    )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Spending by Category")

        if spending:
            spending_df = pd.DataFrame(spending)

            st.bar_chart(
                spending_df.set_index("category")["total"]
            )

            st.dataframe(
                spending_df,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No spending data is available.")

    with right:
        st.subheader("Recent Activity")

        if transactions:
            transaction_df = pd.DataFrame(transactions)

            st.dataframe(
                transaction_df,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No transactions are available.")


# --------------------------------------------------
# Transaction history
# --------------------------------------------------

with transactions_tab:
    st.subheader("Transaction History")

    if transactions:
        transaction_df = pd.DataFrame(transactions)

        transaction_types = ["All"] + sorted(
            transaction_df["transaction_type"].unique().tolist()
        )

        selected_type = st.selectbox(
            "Filter by transaction type",
            transaction_types,
            key="transaction_filter",
        )

        if selected_type != "All":
            transaction_df = transaction_df[
                transaction_df["transaction_type"] == selected_type
            ]

        st.dataframe(
            transaction_df,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Transaction order follows the current database query; "
            "timestamps are not yet recorded."
        )
    else:
        st.info("No transactions found.")


# --------------------------------------------------
# Risk monitoring
# --------------------------------------------------

with risk_tab:
    st.subheader("Suspicious Transaction Monitoring")

    st.write(
        "The Risk Agent flags debit transactions that meet the "
        "configured high-value review threshold of ₹20,000."
    )

    if risk_results:
        risk_df = pd.DataFrame(risk_results)

        st.warning(
            f"{len(risk_results)} transaction(s) flagged for review."
        )

        st.dataframe(
            risk_df,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "A flag is a review alert, not proof of fraudulent activity."
        )
    else:
        st.success("No transactions met the current demo risk rule.")


# --------------------------------------------------
# Loan assessment
# --------------------------------------------------

with loan_tab:
    st.subheader("Demo Loan Eligibility Assessment")

    st.write(
        "The Credit Agent checks sample customer data against "
        "configurable demonstration criteria."
    )

    st.metric(
        "Monthly Income",
        f"₹{loan_result.get('monthly_income', 0):,.2f}",
    )

    st.metric(
        "Credit Score",
        loan_result.get("credit_score", "N/A"),
    )

    if loan_result.get("eligible"):
        st.success("Meets the configured demo criteria")
    elif loan_result.get("customer_name"):
        st.warning("Does not meet all configured demo criteria")
    else:
        st.error("Customer assessment could not be completed.")

    st.write(loan_result.get("message", "No assessment message."))

    st.write("**Assessment details**")

    for reason in loan_result.get("reasons", []):
        st.write(f"- {reason}")

    st.caption(
        "This is a simulated eligibility check, not a real loan "
        "approval or a complete credit underwriting decision."
    )


# --------------------------------------------------
# AI assistant
# --------------------------------------------------

with assistant_tab:
    st.subheader("Chat with the AI Banking Assistant")

    st.write(
        "Ask about your sample balance, transaction history, "
        "spending, suspicious activity, or loan eligibility."
    )

    # Keep the conversation during Streamlit reruns.
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display previous messages.
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("agents"):
                st.caption(
                    "Agents used: " + ", ".join(message["agents"])
                )

    # Chat input
    user_request = st.chat_input(
        "Example: Check my balance and flag suspicious transactions"
    )

    if user_request:
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_request,
        })

        with st.chat_message("user"):
            st.markdown(user_request)

        with st.chat_message("assistant"):
            with st.spinner("Supervisor is coordinating the agents..."):
                result = handle_request(
                    user_request,
                    customer_id=CUSTOMER_ID,
                )

            # Account balance
            if "account_balance" in result:
                st.markdown(
                    "**Account Balance:** "
                    f"₹{result['account_balance']:,.2f}"
                )

            # Transaction history
            if "transactions" in result:
                st.markdown("**Recent Transactions**")
                st.dataframe(
                    pd.DataFrame(result["transactions"]),
                    use_container_width=True,
                    hide_index=True,
                )

            # Spending analysis
            if "spending_analysis" in result:
                st.markdown("**Spending Analysis**")

                if result["spending_analysis"]:
                    st.dataframe(
                        pd.DataFrame(result["spending_analysis"]),
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("No spending data is available.")

            # Risk assessment
            if "risk_assessment" in result:
                st.markdown("**Risk Assessment**")

                if result["risk_assessment"]:
                    st.warning(
                        "The Risk Agent flagged transactions for review."
                    )

                    st.dataframe(
                        pd.DataFrame(result["risk_assessment"]),
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.success(
                        "No transactions met the configured risk rule."
                    )

            # Loan assessment
            if "loan_assessment" in result:
                loan = result["loan_assessment"]

                st.markdown("**Loan Assessment**")

                if loan.get("customer_name"):
                    st.write(
                        f"Customer: {loan['customer_name']}"
                    )
                    st.write(
                        f"Monthly income: "
                        f"₹{loan['monthly_income']:,.2f}"
                    )
                    st.write(
                        f"Credit score: {loan['credit_score']}"
                    )

                st.write(loan["message"])

                for reason in loan.get("reasons", []):
                    st.write(f"- {reason}")

            # Unknown request or Supervisor error
            if "message" in result:
                st.info(result["message"])

            if "error" in result:
                st.caption(
                    "The AI service may be temporarily unavailable. "
                    "Try a supported banking request or try again later."
                )

            agents = result.get("agent_used", [])

            if agents:
                st.caption("Agents used: " + ", ".join(agents))

            # Save a readable summary for conversation history.
            summary_parts = []

            if "account_balance" in result:
                summary_parts.append(
                    f"Account balance: ₹{result['account_balance']:,.2f}"
                )

            if "transactions" in result:
                summary_parts.append(
                    f"Displayed {len(result['transactions'])} transactions."
                )

            if "spending_analysis" in result:
                summary_parts.append("Spending analysis displayed.")

            if "risk_assessment" in result:
                summary_parts.append(
                    f"{len(result['risk_assessment'])} transaction(s) "
                    "flagged for review."
                )

            if "loan_assessment" in result:
                summary_parts.append(
                    result["loan_assessment"]["message"]
                )

            if "message" in result:
                summary_parts.append(result["message"])

            if "error" in result:
                summary_parts.append(
                    "The AI service encountered an error."
                )

            if not summary_parts:
                summary_parts.append("The request was processed.")

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "\n\n".join(summary_parts),
                "agents": agents,
            })


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "AI Multi-Agent Banking Prototype | "
    "Uses simulated customer and transaction records | "
    "Not connected to real banking infrastructure"
)
