import json
from datetime import datetime
from pathlib import Path
from typing import Dict

import requests
import tqdm
from loguru import logger
from requests.sessions import Session

from doc_hut_data.schema import FacilitySearchParams, UnitAvailabilityParams


class HutScraper:
    def __init__(self):
        self.session = self._get_session()
        self.facility_dir = Path("data/facility")
        self.facility_dir.mkdir(parents=True, exist_ok=True)

    def _get_session(self) -> Session:
        """Create and return a session with proper headers and cookies initialized"""
        session = requests.Session()

        session.headers.update(
            {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                "Content-Type": "application/json; charset=UTF-8",
                "Origin": "https://bookings.doc.govt.nz",
                "Referer": "https://bookings.doc.govt.nz/Web/Facilities/SearchViewUnitAvailabity.aspx",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest",
            }
        )

        response = session.get(
            "https://bookings.doc.govt.nz/Web/Facilities/SearchViewUnitAvailabity.aspx"
        )

        anti_csrf_cookie = session.cookies.get("__AntiXsrfToken")
        if anti_csrf_cookie:
            session.headers.update({"RequestVerificationToken": anti_csrf_cookie})

        return session

    def get_facility_data(self, params: FacilitySearchParams) -> Dict:
        """Fetch facility data for a given place ID"""
        url = "https://bookings.doc.govt.nz/Web/Facilities/SearchViewUnitAvailabity.aspx/GetFacilityData"

        payload = {
            "UnitAvailabilitySearchParams": {
                "RegionId": params.region_id,
                "PlaceId": params.place_id,
                "FacilityId": params.facility_id,
                "StartDate": params.start_date,
                "Nights": str(params.nights),
                "CategoryId": params.category_id,
                "UnitTypeIds": params.unit_type_ids,
                "UnitTypesCategory": params.unit_types_category,
                "ShowOnlyAdaUnits": params.show_only_ada_units,
                "ShowOnlyTentSiteUnits": params.show_only_tent_site_units,
                "ShowOnlyRvSiteUnits": params.show_only_rv_site_units,
                "MinimumVehicleLength": params.minimum_vehicle_length,
                "FacilityTypes_new": params.facility_types_new,
                "AccessTypes": params.access_types,
                "ShowIsPremiumUnits": params.show_is_premium_units,
                "ParkFinder": params.park_finder,
                "UnitTypeCategoryId": params.unit_type_category_id,
                "ShowSiteUnitsName": params.show_site_units_name,
                "AmenitySearchParameters": params.amenity_search_parameters,
            }
        }

        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def get_unit_availability(self, params: UnitAvailabilityParams) -> Dict:
        """Fetch unit availability grid data for a specific facility"""
        url = "https://bookings.doc.govt.nz/Web/Facilities/SearchViewUnitAvailabity.aspx/GetSearchUnitGridDataHtmlString"

        payload = {
            "FacilityId": str(params.facility_id),
            "PlaceId": str(params.place_id),
            "MaximumDates": str(params.maximum_dates),
            "IsTablet": "false",
            "MaximumStayforGrid": params.maximum_stay,
        }

        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def fetch_all_facilities(self) -> None:
        """Load places from places.json and fetch facility data for each place ID"""
        logger.info("Starting facility data collection")

        try:
            with open("data/places.json", "r") as f:
                places = json.load(f)
        except FileNotFoundError:
            logger.error("places.json not found in data directory")
            raise FileNotFoundError("places.json not found")

        start_date = datetime.now().strftime("%m/%d/%Y")
        processed_count = 0
        error_count = 0

        try:
            progress = tqdm(
                places["places"],
                desc="Processing places",
                position=0,
                leave=True,
            )

            for place in progress:
                place_id = place.get("PlaceId")
                place_name = place.get("Name", "Unknown")

                if not place_id:
                    logger.warning(f"Skipping place '{place_name}' - no PlaceId found")
                    continue

                logger.info(f"Processing PlaceId {place_id} ({place_name})")

                try:
                    params = FacilitySearchParams(
                        place_id=place_id,
                        start_date=start_date,
                    )
                    facility_data = self.get_facility_data(params)

                    facilities = facility_data.get("d", {})

                    if not facilities:
                        logger.warning(f"No facilities found for PlaceId {place_id}")
                        continue

                    for facility in facilities:
                        facility_id = facility.get("FacilityId")
                        if facility_id:
                            output_file = (
                                self.facility_dir / f"facility_{facility_id}.json"
                            )
                            with open(output_file, "w") as f:
                                json.dump(facility, f, indent=2)
                            logger.success(
                                f"Saved facility {facility_id} data to {output_file}"
                            )

                    processed_count += 1

                except requests.exceptions.RequestException as e:
                    logger.error(
                        f"Error fetching data for PlaceId {place_id}: {str(e)}"
                    )
                    error_count += 1
                    continue

        finally:
            self.session.close()

        logger.info(
            f"Completed processing {processed_count} places with {error_count} errors"
        )
