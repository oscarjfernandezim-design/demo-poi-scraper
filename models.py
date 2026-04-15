"""
Data models for POI extraction
"""

from dataclasses import dataclass, asdict
from typing import Optional
import json


@dataclass
class Address:
    """Minimal address data model - optimized for low payload"""
    street: Optional[str] = None
    house_number: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None

    def to_dict(self):
        """Convert to dict, excluding None values"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def size_kb(self) -> float:
        """Estimate size in KB"""
        return len(json.dumps(self.to_dict())) / 1024


@dataclass
class Building:
    """Building metadata - minimal payload"""
    name: Optional[str] = None
    building_type: Optional[str] = None

    def to_dict(self):
        """Convert to dict, excluding None values"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def size_kb(self) -> float:
        """Estimate size in KB"""
        return len(json.dumps(self.to_dict())) / 1024


@dataclass
class POI:
    """Point of Interest - core entity"""
    name: str
    poi_type: str
    latitude: float
    longitude: float
    address: Optional[Address] = None
    building: Optional[Building] = None
    confidence: float = 1.0

    def to_dict(self):
        """Convert to optimized dict for output"""
        return {
            "name": self.name,
            "type": self.poi_type,
            "lat": round(self.latitude, 6),
            "lon": round(self.longitude, 6),
            "address": self.address.to_dict() if self.address else None,
            "building": self.building.to_dict() if self.building else None,
            "confidence": self.confidence
        }

    def size_kb(self) -> float:
        """Calculate total record size in KB"""
        total_size = len(json.dumps(self.to_dict())) / 1024
        return round(total_size, 4)

    def __repr__(self):
        return f"POI({self.name}, {self.poi_type}, {self.latitude:.4f}, {self.longitude:.4f})"
