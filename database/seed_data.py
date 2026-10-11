
from database.db import initialize_database, get_connection


def seed_database():
    initialize_database()

    with get_connection() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO customers
            VALUES (1, 'Arun Kumar', 45000, 750)
        """)

        conn.execute("""
            INSERT OR IGNORE INTO accounts
            VALUES (1, 1, 50000)
        """)

        transactions = [
            (1, 1, "Supermarket", "Food", 1200, "DEBIT"),
            (2, 1, "Salary", "Income", 45000, "CREDIT"),
            (3, 1, "Electricity Bill", "Utilities", 1800, "DEBIT"),
            (4, 1, "Online Transfer", "Transfer", 25000, "DEBIT"),
            (5, 1, "Restaurant", "Food", 850, "DEBIT"),
        ]

        conn.executemany("""
            INSERT OR IGNORE INTO transactions
            VALUES (?, ?, ?, ?, ?, ?)
        """, transactions)

        conn.execute("""
            INSERT OR IGNORE INTO loans
            VALUES (1, 1, 100000, 'UNDER_REVIEW')
        """)

        conn.commit()


if __name__ == "__main__":
    seed_database()
    print("Banking database initialized with sample data!")
