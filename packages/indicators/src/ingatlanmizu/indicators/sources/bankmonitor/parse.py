from datetime import date

def parse(data: dict[str, any], now: date):
    loans: list[dict[str, any]] = []
    for loan in data["normalList"]:
        loans.append({
            "name": loan["name"],
            "bank_name": loan["bank"]["name"],
            "available_at": now.strftime("%Y-%m-%d"),
            "apr": loan["apr"] * 100,
            "monthly_installment": loan["installmentStart"],
            "full_payable_amount": loan["fullPayableAmount"],
        })
    return loans