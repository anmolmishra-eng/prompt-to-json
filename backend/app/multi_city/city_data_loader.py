"""
Multi-city dataset loader
Supports: Mumbai, Pune, Ahmedabad, Nashik
"""

import logging
from enum import Enum
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class City(str, Enum):
    """Supported cities"""

    MUMBAI = "Mumbai"
    PUNE = "Pune"
    AHMEDABAD = "Ahmedabad"
    NASHIK = "Nashik"


class CityRules(BaseModel):
    """City-specific compliance rules"""

    city: City
    dcr_version: str
    fsi_base: float
    setback_front: float
    setback_rear: float
    parking_ratio: str
    max_height: Optional[float] = None
    source_documents: List[str] = []


class CityDataLoader:
    """Load and manage multi-city datasets"""

    CITY_RULES = {
        City.MUMBAI: CityRules(
            city=City.MUMBAI,
            dcr_version="DCPR 2034",
            fsi_base=1.33,
            setback_front=3.0,
            setback_rear=3.0,
            parking_ratio="1 ECS per 100 sqm",
            max_height=None,
            source_documents=["DCPR_2034.pdf", "MCGM_Amendments.pdf", "MHADA_Guidelines.pdf"],
        ),
        City.PUNE: CityRules(
            city=City.PUNE,
            dcr_version="Pune DCR 2017",
            fsi_base=1.5,
            setback_front=4.0,
            setback_rear=3.0,
            parking_ratio="1 ECS per 80 sqm",
            max_height=70.0,
            source_documents=["Pune_DCR_2017.pdf"],
        ),
        City.AHMEDABAD: CityRules(
            city=City.AHMEDABAD,
            dcr_version="AUDA DCR 2020",
            fsi_base=1.8,
            setback_front=5.0,
            setback_rear=4.0,
            parking_ratio="1 ECS per 70 sqm",
            max_height=None,
            source_documents=["AUDA_DCR_2020.pdf"],
        ),
        City.NASHIK: CityRules(
            city=City.NASHIK,
            dcr_version="NMC DCR 2015",
            fsi_base=1.2,
            setback_front=3.5,
            setback_rear=2.5,
            parking_ratio="1 ECS per 90 sqm",
            max_height=60.0,
            source_documents=["NMC_DCR_2015.pdf"],
        ),
    }

    def get_city_rules(self, city: City) -> CityRules:
        """Get compliance rules for a city"""
        return self.CITY_RULES.get(city)

    def get_all_cities(self) -> List[City]:
        """Get list of all supported cities"""
        return list(City)

    def validate_city(self, city_name: str) -> Optional[City]:
        """Validate and normalize city name"""
        try:
            return City(city_name)
        except ValueError:
            logger.warning(f"Unknown city: {city_name}")
            return None

    def get_city_context(self, city: City) -> Dict:
        """Get full city context for design generation"""
        rules = self.get_city_rules(city)

        return {
            "city": rules.city.value,
            "dcr_version": rules.dcr_version,
            "constraints": {
                "fsi_base": rules.fsi_base,
                "setback_front_m": rules.setback_front,
                "setback_rear_m": rules.setback_rear,
                "parking_ratio": rules.parking_ratio,
                "max_height_m": rules.max_height,
            },
            "source_documents": rules.source_documents,
            "typical_use_cases": self._get_typical_use_cases(city),
        }

    def _get_typical_use_cases(self, city: City) -> List[str]:
        """Get typical building types for city"""
        common = ["residential", "commercial", "mixed_use"]

        city_specific = {
            City.MUMBAI: ["high_rise_residential", "slum_rehabilitation"],
            City.PUNE: ["it_park", "educational_institution"],
            City.AHMEDABAD: ["industrial", "textile_mill_redevelopment"],
            City.NASHIK: ["agricultural_warehouse", "wine_tourism"],
        }

        return common + city_specific.get(city, [])


# API Router
city_router = APIRouter(prefix="/cities", tags=["🏙️ Multi-City"])
loader = CityDataLoader()


@city_router.get("/")
async def list_cities():
    """List all supported cities"""
    cities = loader.get_all_cities()
    return {"cities": [city.value for city in cities], "count": len(cities)}


@city_router.get("/{city_name}/rules")
async def get_city_rules(city_name: str):
    """Get compliance rules for a city"""
    city = loader.validate_city(city_name)

    if not city:
        raise HTTPException(status_code=404, detail=f"City '{city_name}' not supported")

    rules = loader.get_city_rules(city)
    return rules.model_dump()


@city_router.get("/{city_name}/context")
async def get_city_context(city_name: str):
    """Get full city context for design"""
    city = loader.validate_city(city_name)

    if not city:
        raise HTTPException(status_code=404, detail=f"City '{city_name}' not supported")

    context = loader.get_city_context(city)
    return context
