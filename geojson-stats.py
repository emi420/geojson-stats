'''
    Stats for GeoJSON data

    - Total features count
    - Properties count
    - Distance for lines (total / per property)
    - Area for polygons (total / per property)
'''

import argparse
import resource
import os
import json
from dataclasses import dataclass, field
from pyproj import Geod
from shapely.geometry import MultiLineString, Polygon, shape

@dataclass
class Config:
    silent: bool = False
    distance_keys: list = field(default_factory=lambda: [])
    area_keys: list = field(default_factory=lambda: [])
    distance: bool = False
    area: bool = False
    projected: bool = False
    proj: str = "WGS84"

@dataclass
class StatsResults:
    count: int = 0
    stats: dict = field(default_factory=lambda: {})

@dataclass
class CalcCache:
    way_length: float = None
    way_area: float = None

class GeoUtils:
    def __init__(self, projected: bool, proj: str = "WGS84"):
        self.projected = projected
        self.proj = proj

    def way_length(self, way: object):
        geo: dict = way["geometry"]
        line: MultiLineString = shape(geo)
        if self.projected:
            length = line.length / 1000
        else:
            geod = Geod(ellps=self.proj)
            length = geod.geometry_length(line) / 1000
        return length 

    def way_area(self, way: object):
        geo: dict = way["geometry"]
        polygon: Polygon = shape(geo)
        if self.projected:
            area = polygon.area / 1000000
        else:
            geod = Geod(ellps=self.proj)
            area = abs(geod.geometry_area_perimeter(polygon)[0]) / 1000000
        return area 

class DataUtils:
    def key_km(key: str):
        return "{0}_km".format(key)

    def key_area_km2(key):
        return "{0}_area_km2".format(key)

class GeoJSONStats:

    def __init__(self, config: Config):
        self.config = config
        self.cache = CalcCache()
        self.results = StatsResults()
        self.geo_utils = GeoUtils(
            projected=self.config.projected
        )
        for key in config.distance_keys:
            self.results.stats[DataUtils.key_km(key)] = 0

        for key in config.area_keys:
            self.results.stats[DataUtils.key_area_km2(key)] = 0

    def clean_cache(self):
        self.cache = self.cache = CalcCache()

    def process_file_line(self, line: str):
        if line[-2:-1] == ",":
            json_string = line[:-2]
        else:
            json_string = line
        json_object = json.loads(json_string)
        self.get_object_stats(json_object)

    def calculate_area_bykey(self, json_object: object, key: str):
        if key in self.config.area_keys:
            if not self.cache.way_area:
                self.cache.way_area = self.geo_utils.way_area(json_object)
            self.results.stats[DataUtils.key_area_km2(key)] += self.cache.way_area

    def calculate_area(self, json_object: object): 
        if (json_object["geometry"]["type"] == "Polygon" \
             or json_object["geometry"]["type"] == "MultiPolygon"):
            if not "area_km2" in self.results.stats:
                self.results.stats["area_km2"] = self.geo_utils.way_area(json_object)
            else:
                self.results.stats["area_km2"] += self.geo_utils.way_area(json_object)

    def calculate_distance_bykey(self, json_object: object, key: str):
        if key in self.config.distance_keys:
            if not self.cache.way_length:
                self.cache.way_length = self.geo_utils.way_length(json_object)
            self.results.stats[DataUtils.key_km(key)] += self.cache.way_length

    def calculate_distance(self, json_object: object):
        if (json_object["geometry"]["type"] == "LineString" \
             or json_object["geometry"]["type"] == "MultiLineString"):
            if not "km" in self.results.stats:
                self.results.stats["km"] = self.geo_utils.way_length(json_object)
            else:
                self.results.stats["km"] += self.geo_utils.way_length(json_object)

    def count_keys(self, key: str):
        if key in self.results.stats:
            self.results.stats[key] += 1
        else:
            self.results.stats[key] = 1

    def get_object_stats(self, json_object: object):
        for prop in json_object["properties"].items():
            if prop[1]:
                key = prop[0]

                # Count keys
                self.count_keys(key)

                # Calculate distance per key
                if self.config.distance_keys:
                    self.calculate_distance_bykey(json_object, key)

                # Calculate area per key
                if self.config.area_keys:
                    self.calculate_area_bykey(json_object, key)

        # Calculate distance
        if self.config.distance:
            self.calculate_distance(json_object)

        # Calculate area
        if self.config.area:
            self.calculate_area(json_object)

        # Count features
        self.results.count += 1

        self.clean_cache()

    def process_geojson(self, geojson_object: object):
        features_count = len(geojson_object["features"])
        for feature in geojson_object["features"]:
            self.get_object_stats(feature)
            if not self.config.silent:
                percent = round((self.results.count * 100) / features_count, 2)
                print("Processed: {0}% ({1})".format(percent, self.results.count),\
                        end='\r', flush=True)

    def process_file_stream(self, filename: str):
        file = open(filename)
        bytes_total = os.stat(filename).st_size
        bytes_processed = 0
        for line in file:
            bytes_processed += len(line)
            if line.startswith('{ "type": "Feature"'):
                self.process_file_line(line)
                percent = round((bytes_processed * 100) / bytes_total, 2)
                if not self.config.silent:
                    print("Processed: {0}% ({1})".format(percent, self.results.count),\
                          end='\r', flush=True)

    def process_file(self, filename: str):
        if not self.config.silent:
            print("Opening file ...\n")
        with open(filename, 'r') as json_data:
            json_data = json.load(json_data)
            self.process_geojson(json_data)

def main():
    args = argparse.ArgumentParser()
    args.add_argument("--file", "-f", help="GeoJSON file to analyze", type=str, default=None)
    args.add_argument("--silent", "-s", help="Silent", default=False, action='store_true')
    args.add_argument("--stream", help="Stream a file (use less memory)", default=False, action='store_true')
    args.add_argument("--distance-keys", help="Keys for calculating distance in km", default = None)
    args.add_argument("--area-keys", help="Keys for calculating area in km2", default = None)
    args.add_argument("--distance", help="Calculate total distance of all linestrings", \
                    default=False, action='store_true')
    args.add_argument("--area", help="Calculate total area of all polygons", \
                    default=False, action='store_true')
    args.add_argument("--projected", help="Use projected coordinated in meters", \
                    default=False, action='store_true')
    args.add_argument("--proj", help="Data projection system", default = "WGS84")
    args = args.parse_args()

    if args.file:
        if not args.silent:
            print("\nFile size is {0} MB\n".format(round(os.stat(args.file).st_size / (1024 * 1024), 2)))
        config = Config(
            silent=args.silent,
            distance_keys = args.distance_keys.split(",") if args.distance_keys else [],
            area_keys = args.area_keys.split(",") if args.area_keys else [],
            distance = args.distance,
            area = args.area,
            projected = args.projected,
            proj = args.proj
        )
        stats = GeoJSONStats(config)
        if args.stream:
            stats.process_file_stream(args.file)
        else:
            stats.process_file(args.file)

        print(json.dumps({
            "count": stats.results.count,
            "stats": stats.results.stats
        }))

        if not args.silent:
            print('\nPeak Memory Usage =', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
            print('User Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_utime)
            print('System Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_stime)

if __name__ == "__main__":
    main()
