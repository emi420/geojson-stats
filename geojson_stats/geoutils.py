from pyproj import Geod
from shapely.geometry import MultiLineString, Polygon, shape

# Utilities
class GeoUtils:
    def __init__(self, projected: bool, proj: str = "WGS84"):
        self.projected = projected
        self.proj = proj

    # Calculate way's length in km
    def way_length(self, way: object):
        geo: dict = way["geometry"]
        line: MultiLineString = shape(geo)
        if self.projected:
            length = line.length / 1000
        else:
            geod = Geod(ellps=self.proj)
            length = geod.geometry_length(line) / 1000
        return length 

    # Calculate way's area in km2
    def way_area(self, way: object):
        geo: dict = way["geometry"]
        polygon: Polygon = shape(geo)
        if self.projected:
            area = polygon.area / 1000000
        else:
            geod = Geod(ellps=self.proj)
            area = abs(geod.geometry_area_perimeter(polygon)[0]) / 1000000
        return area 
