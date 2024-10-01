#!/usr/bin/python3

import argparse
import resource
import os
import json
from dataclasses import dataclass, field
from pyproj import Geod
from shapely.geometry import MultiLineString, Polygon, shape
from urllib.request import Request, urlopen

@dataclass
class Config:
    # Be verbose
    verbose: bool = False
    # Keys used for calculate distance
    distance_keys: list = field(default_factory=lambda: [])
    # Keys used for calculate area
    area_keys: list = field(default_factory=lambda: [])
    # Enable/disable distance calculation
    distance: bool = False
    # Enable/disable area calculation
    area: bool = False
    # Use projected coordinates
    projected: bool = False
    # Coordinates system
    proj: str = "WGS84"

# Statistics results
@dataclass
class StatsResults:
    # Total features count
    count: int = 0
    # Stats for features
    stats: dict = field(default_factory=lambda: {})

# Cache for storing calculations
@dataclass
class CalcCache:
    way_length: float = None
    way_area: float = None

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

# Utils for labelling
class DataUtils:
    KM_LABEL = "km"
    KM2_LABEL = "area_km2"

    def key_km(key: str):
        return "{0}_{1}".format(key, DataUtils.KM_LABEL)

    def key_area_km2(key):
        return "{0}_{1}".format(key, DataUtils.KM2_LABEL)

# Stats generator
class Stats:

    def __init__(self, config: Config = None):
        if config is None:
            config = Config()
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

    # Clean calculation cache
    def clean_cache(self):
        self.cache = self.cache = CalcCache()

    # Process a line of a file
    def process_file_line(self, line: str):
        if line[-2:-1] == ",":
            json_string = line[:-2]
        else:
            json_string = line
        json_object = json.loads(json_string)
        self.get_object_stats(json_object)

    # Calculate area in km2 by key
    def calculate_area_bykey(self, json_object: object, key: str):
        if key in self.config.area_keys:
            if not self.cache.way_area:
                self.cache.way_area = self.geo_utils.way_area(json_object)
            self.results.stats[DataUtils.key_area_km2(key)] += self.cache.way_area

    # Calculate total area in km2
    def calculate_area(self, json_object: object): 
        if json_object["geometry"] and (json_object["geometry"]["type"] == "Polygon" \
            or json_object["geometry"]["type"] == "MultiPolygon"):
            if not DataUtils.KM2_LABEL in self.results.stats:
                self.results.stats[DataUtils.KM2_LABEL] = self.geo_utils.way_area(json_object)
            else:
                self.results.stats[DataUtils.KM2_LABEL] += self.geo_utils.way_area(json_object)

    # Calculate distance in km by key
    def calculate_distance_bykey(self, json_object: object, key: str):
        if key in self.config.distance_keys:
            if not self.cache.way_length:
                self.cache.way_length = self.geo_utils.way_length(json_object)
            self.results.stats[DataUtils.key_km(key)] += self.cache.way_length

    # Calculate total distance in km
    def calculate_distance(self, json_object: object):
        if (json_object["geometry"]["type"] == "LineString" \
             or json_object["geometry"]["type"] == "MultiLineString"):
            if not DataUtils.KM_LABEL in self.results.stats:
                self.results.stats[DataUtils.KM_LABEL] = self.geo_utils.way_length(json_object)
            else:
                self.results.stats[DataUtils.KM_LABEL] += self.geo_utils.way_length(json_object)

    # Count property keys
    def count_keys(self, key: str):
        if key in self.results.stats:
            self.results.stats[key] += 1
        else:
            self.results.stats[key] = 1

    # Get stats for a Feature object
    def get_object_stats(self, json_object: object):
        for prop in json_object["properties"].items():
            if prop[1]:
                key = prop[0]

                self.count_keys(key)

                if self.config.distance_keys:
                    self.calculate_distance_bykey(json_object, key)

                if self.config.area_keys:
                    self.calculate_area_bykey(json_object, key)

        if self.config.distance:
            self.calculate_distance(json_object)

        if self.config.area:
            self.calculate_area(json_object)

        self.results.count += 1

        self.clean_cache()

    # Process a GeoJSON object
    def process_geojson(self, geojson_object: object):
        features_count = len(geojson_object["features"])
        for feature in geojson_object["features"]:
            self.get_object_stats(feature)
            if self.config.verbose:
                percent = round((self.results.count * 100) / features_count, 2)
                print("Processed: {0}% ({1})".format(percent, self.results.count),\
                        end='\r', flush=True)

    # Process a GeoJSON file line by line
    def process_file_stream(self, filename: str):
        file = open(filename)
        bytes_total = os.stat(filename).st_size
        bytes_processed = 0
        for line in file:
            bytes_processed += len(line)
            if line.startswith('{ "type": "Feature"'):
                self.process_file_line(line)
                percent = round((bytes_processed * 100) / bytes_total, 2)
                if self.config.verbose:
                    print("Processed: {0}% ({1})".format(percent, self.results.count),\
                          end='\r', flush=True)

    # Process a GeoJSON file
    def process_file(self, filename: str):
        if self.config.verbose:
            print("Opening file ...\n")
        with open(filename, 'r') as json_data:
            json_data = json.load(json_data)
            self.process_geojson(json_data)

    # Process an URL
    def process_url(self, url: str):
        if self.config.verbose:
            print("Downloading file from URL ...\n")

        req = Request(
            url=url,
            headers={'User-Agent': 'Mozilla/5.0'})

        json_data = urlopen(req).read().decode('utf-8')
        self.process_geojson(json.loads(json_data))

    # Returns a JSON string with the results
    def json(self):
        return json.dumps({
            "count": self.results.count,
            "stats": self.results.stats
        })

    # Dumps results
    def dump(self):
        print(self.json())

# Entrypoint for command line
def main():
    args = argparse.ArgumentParser()
    args.add_argument("--file", "-f", help="GeoJSON file to analyze", type=str, default=None)
    args.add_argument("--url", "-u", help="URL of GeoJSON file to analyze", type=str, default=None)
    args.add_argument("--verbose", "-v", help="Verbose", default=False, action='store_true')
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

    config = Config(
        verbose=args.verbose,
        distance_keys = args.distance_keys.split(",") if args.distance_keys else [],
        area_keys = args.area_keys.split(",") if args.area_keys else [],
        distance = args.distance,
        area = args.area,
        projected = args.projected,
        proj = args.proj
    )
    stats = Stats(config)

    if args.url or args.file:

        if args.url:
            stats.process_url(args.url)

        elif args.file:
            if args.verbose:
                print("\nFile size is {0} MB\n".format(round(os.stat(args.file).st_size / (1024 * 1024), 2)))
            if args.stream:
                stats.process_file_stream(args.file)
            else:
                stats.process_file(args.file)

        print(json.dumps({
            "count": stats.results.count,
            "stats": stats.results.stats
        }))

        if args.verbose:
            print('\nPeak Memory Usage =', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
            print('User Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_utime)
            print('System Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_stime)

if __name__ == "__main__":
    main()
