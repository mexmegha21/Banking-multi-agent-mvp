
from agents.risk_agent import detect_suspicious_transactions

alerts = detect_suspicious_transactions(1)

if alerts:
    print("SUSPICIOUS TRANSACTION ALERTS")

    for alert in alerts:
        print(alert)
else:
    print("No transactions met the configured threshold.")
