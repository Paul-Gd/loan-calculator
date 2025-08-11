import argparse
import json
import os
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
        "https://www.bnr.ro/Indicele-de-referin%C8%9Ba-pentru-creditele-consumatorilor--19492-Mobile.aspx"
    )
    if response.status_code != 200:
        raise Exception(
            "Failed to load block content",
            {"status_code": response.status_code, "text": response.text},
        )
    
    logging.info("Block content loaded successfully")
    
    # Parse the response
    soup = BeautifulSoup(response.text, "html.parser")
    result = []
    

    
    # Look for tables in the block content
    tables = soup.find_all("table")
    logging.info("Found %d tables in the block content", len(tables))
    
    if len(tables) == 0:
        logging.error("No tables found in block content")
        raise Exception("Could not find any tables in the block content.")
    
    # Look for the daily data table - should be the second table based on the user's HTML
    daily_table = None
    for i, table in enumerate(tables):
        table_text = table.get_text(strip=True)
        logging.info("Table %d preview: %s", i, table_text[:300])
        
        # Look for patterns that indicate daily data (recent dates)
        if "2025" in table_text and any(pattern in table_text for pattern in ["07.08", "06.08", "05.08", "04.08"]):
            daily_table = table
            logging.info("Found daily table at index %d", i)
            break
    
    if daily_table is None:
        if len(tables) >= 2:
            daily_table = tables[1]  # Use second table as fallback
            logging.info("Using fallback: table 1 for daily data")
        else:
            daily_table = tables[0]  # Use first table if only one exists
            logging.info("Using fallback: table 0 for daily data")
    
    for row in daily_table.find_all("tr")[1:]:  # Skip header row
        cells = row.find_all("td")
        if len(cells) >= 2:
            date_str = cells[0].get_text(strip=True)
            rate_str = cells[1].get_text(strip=True)
            
            try:
                # Parse date in DD.MM.YYYY format
                parsed_date = datetime.strptime(date_str, "%d.%m.%Y").date()
                # Parse rate, replace comma with dot for float conversion
                rate_parsed = float(rate_str.replace(",", "."))
                result.append(DailyIrccRate(parsed_date, rate_parsed))
            except Exception as e:
                logging.warning("Failed to parse row: date=%s, rate=%s, error=%s", date_str, rate_str, e)
    
    return result


def load_existing_data(file_path):
    """Load existing IRCC data from JSON file."""
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            return [
                DailyIrccRate(datetime.fromisoformat(entry["date"]).date(), entry["rate"])
                for entry in data
            ]
    except Exception as e:
        logging.warning("Failed to load existing data: %s", e)
        return []


def merge_data(existing_data, new_data):
    """Merge new data with existing data, avoiding duplicates."""
    # Create a set of existing dates for fast lookup
    existing_dates = {entry.date for entry in existing_data}
    
    # Add only new entries that don't already exist
    merged_data = existing_data.copy()
    new_entries_count = 0
    
    for entry in new_data:
        if entry.date not in existing_dates:
            merged_data.append(entry)
            existing_dates.add(entry.date)
            new_entries_count += 1
    
    # Sort by date (newest first)
    merged_data.sort(key=lambda x: x.date, reverse=True)
    
    logging.info("Added %d new entries", new_entries_count)
    return merged_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download daily ircc rate from BNR and merges with existing data in JSON format"
    )
    parser.add_argument(
        "-f", "--file", default="./ircc.json", help="output file location"
    )
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Load existing data
    existing_data = load_existing_data(args.file)
    logging.info("Loaded %d existing entries", len(existing_data))
    
    # Scrape new data
    new_data = scrape_ircc()
    logging.info("Scraped %d new entries", len(new_data))
    
    # Merge data
    merged_data = merge_data(existing_data, new_data)
    
    # Save merged data
    with open(args.file, "w") as f:
        json.dump(
            [
                {"date": daily_ircc.date.isoformat(), "rate": daily_ircc.ircc_rate}
                for daily_ircc in merged_data
            ],
            f,
            indent=2
        )
    
    logging.info("Saved %d total entries to %s", len(merged_data), args.file)
