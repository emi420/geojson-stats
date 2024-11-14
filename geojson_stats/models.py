from dataclasses import dataclass, field

@dataclass
class Config:
    # Be verbose
    verbose: bool = False
    # Keys for measure length or area
    keys: list = field(default_factory=lambda: [])
    # Enable/disable length calculation
    length: bool = False
    # Enable/disable area calculation
    area: bool = False
    # Keys for collecting value stats
    value_keys: list = field(default_factory=lambda: [])
    # Use projected coordinates
    projected: bool = False
    # Remove zero and empty results
    clean: bool = False
    # Coordinates system
    proj: str = "WGS84"
    # Properties to analyze (ex: "properties" or "properties.tags")
    properties_prop: str = "properties"


# Base stats class
@dataclass
class BaseStats:
    count: int = 0
    length: float = 0
    area: float = 0

    def sum(self, key = None):
        self.count += 1

    def sum_length(self, length: float = 0):
        self.length += length

    def sum_area(self, area: float = 0):
        self.area += area

    def to_dict(self, clean = False):
        res = {
            "count": self.count,
            "area": self.area,
            "length": self.length
        }
        if clean:
            if res["count"] == 0:
                del res["count"]
            if res["area"] == 0:
                del res["area"]
            if res["length"] == 0:
                del res["length"]
        return res

# Stats by value
@dataclass
class ValueStats(BaseStats):
    pass

# Stats by key
@dataclass
class KeyStats(BaseStats):
    value: dict = field(default_factory=lambda: {})

    def to_dict(self, clean = False, total = 1):
        res = {
            "count": self.count,
            "percent": round(self.count * 100 / total, 2),
            "area": self.area,
            "length": self.length,
            "value": {k:v.to_dict(clean) for k, v in self.value.items()}
        }
        if clean:
            if res["count"] == 0:
                del res["count"]
            if res["area"] == 0:
                del res["area"]
            if res["length"] == 0:
                del res["length"]
            if res["value"] == {}:
                del res["value"]
        return res

# Total stats
@dataclass
class TotalStats(BaseStats):
    key: dict = field(default_factory=lambda: {})
    languages: list = field(default_factory=lambda: [])

    def bykey(self, key: str):
        if key not in self.key:
            self.key[key] = KeyStats()
        return self.key[key]

    def bykeyvalue(self, key: str, value: str):
        key_object = self.bykey(key)
        if not value in key_object.value:
            key_object.value[value] = ValueStats()
        return self.key[key].value[value]

    def to_dict(self, clean = False):
        res = {
            "count": self.count,
            "area": self.area,
            "length": self.length,
            "languages": {
                "list": self.languages,
                "count": len(self.languages),
            },
            "key": {k:v.to_dict(clean, self.count) for k, v in self.key.items()}
        }
        if clean:
            if res["count"] == 0:
                del res["count"]
            if res["area"] == 0:
                del res["area"]
            if res["length"] == 0:
                del res["length"]
        res["key"] = dict(sorted(res["key"].items(), key=lambda x: x[1]["count"], reverse=True))
        return res


# Cache for storing calculations
@dataclass
class CalcCache:
    way_length: float = None
    way_area: float = None