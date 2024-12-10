import argparse
import json
from dataclasses import dataclass
from datetime import date, datetime
import string
import logging

import requests
from bs4 import BeautifulSoup


@dataclass
class DailyIrccRate:
    date: date
    ircc_rate: float


def scrape_ircc():
    response = requests.get(
        "https://www.bnro.ro/Indicele-de-referin%C8%9Ba-pentru-creditele-consumatorilor--19492-Mobile.aspx"
    )
    if response.status_code != 200:
        raise Exception(
            "Response status code is not 200",
            {"status_code": response.status_code, "text": response.text},
        )

    soup = BeautifulSoup(response.text, "html.parser")
    result = []
    for row in soup.find(id="alldata").find("table").find_all("tr")[1:]:
        date = datetime.strptime(row.find_all("td")[0].string, "%d.%m.%Y").date()
        ircc_rate = row.find_all("td")[1].string.replace(",", ".")
        try:
            ircc_rate_parsed = float(ircc_rate)
            result.append(DailyIrccRate(date, ircc_rate_parsed))
        except Exception as e:
            logging.warning("Failed to parse %s", ircc_rate)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download daily ircc rate from BNR and saves is in JSON format"
    )
    parser.add_argument(
        "-f", "--file", default="./ircc.json", help="output file location"
    )
    args = parser.parse_args()

    ircc_data = scrape_ircc()
    with open(args.file, "w") as f:
        json.dump(
            [
                {"date": daily_ircc.date.isoformat(), "rate": daily_ircc.ircc_rate}
                for daily_ircc in ircc_data
            ],
            f,
        )
