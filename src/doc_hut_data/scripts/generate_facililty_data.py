import json
from datetime import datetime
from typing import Optional

import typer
from doc_hut_data.hut_scraper import HutScraper
from doc_hut_data.schema import FacilitySearchParams, UnitAvailabilityParams
from loguru import logger
from tqdm.auto import tqdm

app = typer.Typer()


def setup_logger():
    """Configure logger to write below the progress bar"""
    logger.remove()  # Remove default logger
    # Format includes padding to move below progress bar
    format_str = "\n<level>{level: <8}</level> | {message}"
    logger.add(
        lambda msg: tqdm.write(msg, end=""),
        format=format_str,
        level="INFO",
        colorize=True,
    )


@app.command()
def fetch_all_facilities():
    """
    Load places from places.json and fetch facility data for each place ID
    """
    setup_logger()
    scraper = HutScraper()
    scraper.fetch_all_facilities()


@app.command()
def get_single_facility(
    place_id: int,
    start_date: Optional[str] = typer.Option(
        None, help="Start date in MM/DD/YYYY format. Defaults to today"
    ),
    nights: Optional[int] = typer.Option(
        2, help="Number of nights to check availability for"
    ),
):
    """
    Fetch facility data for a single place ID from DOC bookings API
    """
    if start_date is None:
        start_date = datetime.now().strftime("%m/%d/%Y")

    scraper = HutScraper()
    try:
        params = FacilitySearchParams(
            place_id=place_id, start_date=start_date, nights=nights
        )
        data = scraper.get_facility_data(params)
        print(json.dumps(data, indent=4))
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")


@app.command()
def get_single_unit_availability(
    place_id: int,
    facility_id: int,
    maximum_dates: Optional[int] = typer.Option(
        100, help="Number of dates to show in availability grid"
    ),
):
    """
    Fetch unit availability data for a single facility from DOC bookings API
    """
    scraper = HutScraper()
    try:
        params = UnitAvailabilityParams(
            place_id=place_id, facility_id=facility_id, maximum_dates=maximum_dates
        )
        data = scraper.get_unit_availability(params)
        print(json.dumps(data, indent=4))
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")


if __name__ == "__main__":
    app()
