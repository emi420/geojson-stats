'''
    Stats for GeoJSON data
'''

import argparse
import resource
import os
import json
from dataclasses import dataclass, field
from pyproj import Geod
from shapely.geometry import MultiLineString, shape

@dataclass
class Config:
    silent: bool = False
    distance_keys: list = field(default_factory=lambda: [])
    all_distances: bool = False
    projected: bool = False

class GeoUtils:
    def __init__(self, projected: bool):
        self.projected = projected

    def way_length(self, way):
        geo: dict = way['geometry']
        line: MultiLineString = shape(geo)
        if self.projected:
            length = line.length / 1000
        else:
            geod = Geod(ellps="WGS84")
            length = geod.geometry_length(line) / 1000
        return length 
    
class DataUtils:
    def key_km(key):
        return "{0}_km".format(key)

class GeoJSONStats:

    def __init__(self, config: Config):
        self.config = config
        self.results = {
            "count": 0,
            "stats" : {}
        }
        self.geo_utils = GeoUtils(
            projected=self.config.projected
        )
        for key in config.distance_keys:
            self.results["stats"]["{0}_km".format(key)] = 0

    def process_file_line(self, line):
        if line[-2:-1] == ",":
            json_string = line[:-2]
        else:
            json_string = line
        json_object = json.loads(json_string)
        self.get_object_stats(json_object)

    def get_object_stats(self, json_object):
        way_length = None
        for prop in json_object["properties"].items():
            if prop[1]:
                key = prop[0]
                if key in self.results["stats"]:
                    self.results["stats"][key] += 1
                else:
                    self.results["stats"][key] = 1
                if key in self.config.distance_keys:
                    if not way_length:
                        way_length = self.geo_utils.way_length(json_object)
                    self.results["stats"][DataUtils.key_km(key)] += way_length
            
        if self.config.all_distances and\
            (json_object["geometry"]["type"] == "LineString" \
             or json_object["geometry"]["type"] == "MultiLineString"):
            if not "km" in self.results["stats"]:
                self.results["stats"]["km"] = self.geo_utils.way_length(json_object)
            else:
                self.results["stats"]["km"] += self.geo_utils.way_length(json_object)

        self.results["count"] += 1

    def process_geojson(self, geojson_object):
        for feature in geojson_object["features"]:
            self.get_object_stats(feature)

    def process_file_stream(self, filename):
        file = open(filename)
        bytes_total = os.stat(filename).st_size
        bytes_processed = 0
        for line in file:
            bytes_processed += len(line)
            if line.startswith('{ "type": "Feature"'):
                self.process_file_line(line)
                percent = round((bytes_processed * 100) / bytes_total, 2)
                if not self.config.silent:
                    print("Processed: {0}% ({1})".format(percent, self.results["count"]), end='\r', flush=True)
        for distance_key in self.config.distance_keys:
            key = DataUtils.key_km(distance_key)
            self.results["stats"][key] = round(self.results["stats"][DataUtils.key_km(distance_key)], 2)

    def process_file(self, filename):
        with open(filename, 'r') as json_data:
            json_data = json.load(json_data)
            self.process_geojson(json_data)

def main():
    args = argparse.ArgumentParser()
    args.add_argument("--file", "-f", help="GeoJSON file to analyze", type=str, default=None)
    args.add_argument("--silent", "-s", help="Silent", default=False, action='store_true')
    args.add_argument("--stream", help="Stream a file", default=False, action='store_true')
    args.add_argument("--distance-keys", help="Keys for calculating distance in km", default = None)
    args.add_argument("--all-distances", help="Calculate distance for all linestrings", \
                    default=False, action='store_true')
    args.add_argument("--projected", help="Use projected coordinated in meters instead of", \
                    default=False, action='store_true')
    args = args.parse_args()

    if args.file:
        if not args.silent:
            print("\nFile size is {0} MB\n".format(round(os.stat(args.file).st_size / (1024 * 1024), 2)))
        config = Config(
            silent=args.silent,
            distance_keys = args.distance_keys.split(",") if args.distance_keys else [],
            all_distances = args.all_distances,
            projected = args.projected
        )
        stats = GeoJSONStats(config)
        if args.stream:
            stats.process_file_stream(args.file)
        else:
            stats.process_file(args.file)

        print(stats.results)

        if not args.silent:
            print('\nPeak Memory Usage =', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
            print('User Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_utime)
            print('System Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_stime)

if __name__ == "__main__":
    main()
