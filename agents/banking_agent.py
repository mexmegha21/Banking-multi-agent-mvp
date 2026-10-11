
from database.db import get_connection


def get_account_balance(customer_id: int):
    """Retrieve the customer's account balance."""

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT SUM(balance) AS total_balance
            FROM accounts
            WHERE customer_id = ?
            """,
            (customer_id,)
        ).fetchone()

    return row["total_balance"] or 0.0


def get_transactions(customer_id: int, limit: int = 5):
    """Retrieve the customer's latest transactions."""

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT transaction_id, description, category,
                   amount, transaction_type
            FROM transactions
            WHERE customer_id = ?
            ORDER BY transaction_id DESC
            LIMIT ?
            """,
            (customer_id, limit)
        ).fetchall()

    return [dict(row) for row in rows]


def analyze_spending(customer_id: int):
    """Calculate debit spending grouped by category."""

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT category, SUM(amount) AS total
            FROM transactions
            WHERE customer_id = ?
              AND transaction_type = 'DEBIT'
            GROUP BY category
            ORDER BY total DESC
            """,
            (customer_id,)
        ).fetchall()

    return [dict(row) for row in rows]
