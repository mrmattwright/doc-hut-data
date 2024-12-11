from typing import List

from pydantic import BaseModel


class FacilitySearchParams(BaseModel):
    region_id: int = 0
    place_id: int
    facility_id: int = 0
    start_date: str
    nights: int = 2
    category_id: str = "0"
    unit_type_ids: List[str] = []
    unit_types_category: List[str] = []
    show_only_ada_units: bool = False
    show_only_tent_site_units: bool = False
    show_only_rv_site_units: bool = False
    minimum_vehicle_length: str = "0"
    facility_types_new: int = 0
    access_types: List[str] = []
    show_is_premium_units: bool = False
    park_finder: List[str] = []
    unit_type_category_id: str = "0"
    show_site_units_name: str = "0"
    amenity_search_parameters: List[str] = []


class UnitAvailabilityParams(BaseModel):
    facility_id: int
    place_id: int
    maximum_dates: int = 20
    maximum_stay: int = 180


class FacilityData(BaseModel):
    __type: str
    place_id: int
    region_name: str
    facility_id: int
    place_name: str
    facility_name: str
    unit_type_id: int
    unit_type_name: str
    count: int
    category_id: int
    tentsite: int
    rcsite: int
    vehiclelength: int
    searchlevel: int
    unit_is_filter: bool
    filtered_applied: int
    enterprise_short_name: str
    facility_alert: bool
    site_url: str
    facility_type_new: int
    facility_season_info: str
    is_ada: bool
    include_ada_waitlist_notification: bool
    facility_allow_web_booking: bool
