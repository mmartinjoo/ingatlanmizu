import requests
from datetime import datetime
from ingatlanmizu.indicators.storage import write_bankmonitor_json

def fetch() -> dict[str, any]:
    resp = requests.post(
        url="https://api.bankmonitor.hu/api/public/mortgages",
        json={
            "loanGoal": "HASZNALT_LAKAS",
            "loanAmount": 40000000,
            "maturity": 20,
            "onePerBank": True,
            "age": 29,
            "currentInstallment": 0,
            "currentCreditLine": 0,
            "receiptOfIncome": True,
            "definedInsuranceUsage": True,
            "activeAccountPackageUsage": True,
            "loanCoverageInsurance": False,
            "activeCreditCardUsage": True,
            "definedAccountPackageUsage": False,
            "wantsFirstHouse": False,
            "eligibleForFalusiCsok": True,
            "eligibleForCsokPlus": True,
            "onlyCsokPlus": False,
            "socialDiscount": False,
            "csok": False,
            "onlyFbl": False,
            "onlyOfk": False,
            "publicSectorToo": False,
            "qualifiesForHigherLtv": False,
            "qualifiesForVoluntaryInterestRateCap": False,
            "bankCodes": [
                "cib",
                "duna",
                "erste",
                "granit",
                "kh",
                "mbh",
                "magnet",
                "otp",
                "raiffeisen",
                "unicredit"
            ],
            "eligibleForHomeStart": False,
            "onlyHomeStart": False,
            "comparator": "THM",
            "roleCode": "BM",
            "interestPeriods": [
                "FULL"
            ],
            "realEstateValue": 60000000,
            "incomeList": [
            {
                "incomeType": "SALARY-H",
                "incomeTypeName": "Magyar alkalmazotti jövedelem",
                "amount": 1000000,
                "receiptAmount": 1000000
            }
            ],
            "withCoupon": True,
            "mortgagedPropertyAcceptableTypes": [
                "LAKAS"
            ],
            "mortgagedPropertyAcceptableWallings": [
                "TEGLA_YTONG"
            ],
            "targetPropertyAcceptableTypes": [
                "LAKAS"
            ],
            "targetPropertyType": "LAKAS",
            "targetPropertyAcceptableWallings": [
                "TEGLA_YTONG"
            ],
            "income": 1000000,
            "calculationDate": "2026-08-17",
            "onlyGreen": False,
            "ecoFriendly": False,
            "withEnergyEfficient": False,
            "numberOfChildren": 0,
            "numberOfChildrenCurrent": 0,
            "numberOfChildrenCommitment": 0
        }
    )
    
    resp.raise_for_status()
    json_dict = resp.json()
    
    write_bankmonitor_json(data=json_dict, now=datetime.now())
    return json_dict