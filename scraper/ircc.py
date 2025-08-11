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
    session = requests.Session()
    
    # First, make a request to the main page to establish session cookies
    main_page_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
    }
    
    # Get the main page first to establish session
    main_response = session.get(
        "https://www.bnr.ro/1974-indicele-de-referinta-pentru-creditele-consumatorilor",
        headers=main_page_headers
    )
    
    if main_response.status_code != 200:
        raise Exception(
            "Failed to load main page",
            {"status_code": main_response.status_code, "text": main_response.text},
        )
    
    logging.info("Main page loaded successfully, session cookies established")
    
    # Parse the main page to extract the block ID dynamically
    main_soup = BeautifulSoup(main_response.text, "html.parser")
    block_wrappers = main_soup.find_all("div", class_="block-wrapper")
    
    # Prepare AJAX headers for testing blocks
    ajax_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0',
        'Accept': 'text/html, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://www.bnr.ro/1974-indicele-de-referinta-pentru-creditele-consumatorilor',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://www.bnr.ro',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }
    
    # Find the block that contains "Indicele de referință zilnic"
    block_id = None
    for wrapper in block_wrappers:
        wrapper_id = wrapper.get("id")
        if wrapper_id:
            logging.info("Testing block wrapper with ID: %s", wrapper_id)
            
            # Test this block to see if it contains the daily IRCC section
            test_post_data = {
                'bid': wrapper_id,
                'currentSlug': '1974-indicele-de-referinta-pentru-creditele-consumatorilor',
                'cat_id': ''
            }
            
            try:
                test_response = session.post(
                    "https://www.bnr.ro/blocks",
                    headers=ajax_headers,
                    data=test_post_data
                )
                
                if test_response.status_code == 200:
                    content = test_response.text
                    # Look for the specific section title "Indicele de referință zilnic"
                    if "Indicele de referință zilnic" in content or "Indicele de referinta zilnic" in content:
                        block_id = wrapper_id
                        logging.info("Found block containing 'Indicele de referință zilnic': %s", block_id)
                        break
                    else:
                        logging.info("Block %s does not contain daily IRCC section", wrapper_id)
                else:
                    logging.warning("Block %s returned status %d", wrapper_id, test_response.status_code)
            except Exception as e:
                logging.warning("Error testing block %s: %s", wrapper_id, e)
    
    if not block_id:
        # Fallback to hardcoded value if we can't find it dynamically
        block_id = "14114"
        logging.warning("Could not find block with 'Indicele de referință zilnic', using fallback: %s", block_id)
    
    # Now make the AJAX request to get the final block content
    post_data = {
        'bid': block_id,
        'currentSlug': '1974-indicele-de-referinta-pentru-creditele-consumatorilor',
        'cat_id': ''
    }
    
    ajax_response = session.post(
        "https://www.bnr.ro/blocks",
        headers=ajax_headers,
        data=post_data
    )
    
    if ajax_response.status_code != 200:
        raise Exception(
            "Failed to load block content",
            {"status_code": ajax_response.status_code, "text": ajax_response.text},
        )
    
    logging.info("Block content loaded successfully")
    
    # Parse the AJAX response
    soup = BeautifulSoup(ajax_response.text, "html.parser")
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
