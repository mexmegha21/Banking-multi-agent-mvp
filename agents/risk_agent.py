
from database.db import get_connection


def detect_suspicious_transactions(customer_id: int):
    """
    Flag debit transactions that meet the configured
    high-value threshold.
    """

    threshold = 20000

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT transaction_id, description, category,
                   amount, transaction_type
            FROM transactions
            WHERE customer_id = ?
              AND transaction_type = 'DEBIT'
              AND amount >= ?
            ORDER BY amount DESC
            """,
            (customer_id, threshold)
        ).fetchall()

    alerts = []

    for row in rows:
        alerts.append({
            "transaction_id": row["transaction_id"],
            "description": row["description"],
            "amount": row["amount"],
            "reason": (
                f"Debit amount meets the ₹{threshold:,} "
                "high-value review threshold"
            ),
            "status": "Flagged for review",
        })

    return alerts
