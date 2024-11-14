import os
import json
from urllib.request import Request, urlopen
from .geoutils import GeoUtils
from .models import *

# Stats generator
class Stats:

    def __init__(self, config: Config = None):
        if config is None:
            config = Config()
        self.config = config
        self.cache = CalcCache()
        self.results = TotalStats()
        self.geo_utils = GeoUtils(
            projected=self.config.projected
        )

    # Get property from tag
    def getProperty(self, path: str, obj: dict):
        keys = path.split('.')
        value = obj
        
        for key in keys:
            value = value.get(key)
            if value is None:
                return None
        
        return value

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

    # Count value by key
    def count_value_bykey(self, json_object: object, key: str, value: str):
        if value and key in self.config.value_keys:
            self.results.bykeyvalue(key, value).sum()

    # Calculate total area in km2
    def calculate_area(self, json_object: object): 
        if json_object["geometry"] and (json_object["geometry"]["type"] == "Polygon" \
            or json_object["geometry"]["type"] == "MultiPolygon"):
                self.results.sum_area(self.geo_utils.way_area(json_object))

    # Calculate length in km by key
    def calculate_length_bykey(self, json_object: object, key: str):
        if key in self.config.keys:
            if not self.cache.way_length:
                self.cache.way_length = self.geo_utils.way_length(json_object)
            self.results.bykey(key).sum_length(self.cache.way_length)

    # Calculate length in km by key value
    def calculate_length_bykeyval(self, json_object: object, key: str, val: str):
        if val and key in self.config.value_keys:
            self.results.bykeyvalue(key, val).sum_length(self.geo_utils.way_length(json_object))

    # Calculate area in km2 by key
    def calculate_area_bykey(self, json_object: object, key: str):
        if key in self.config.keys:
            if not self.cache.way_area:
                self.cache.way_area = self.geo_utils.way_area(json_object)
            self.results.bykey(key).sum_area(self.cache.way_area)

    # Calculate area in km2 by key value
    def calculate_area_bykeyval(self, json_object: object, key: str, val: str):
        if val and key in self.config.value_keys:
            self.results.bykeyvalue(key, val).sum_area(self.geo_utils.way_area(json_object))

    # Calculate total length in km
    def calculate_length(self, json_object: object):
        if (json_object["geometry"]["type"] == "LineString" \
             or json_object["geometry"]["type"] == "MultiLineString"):
                self.results.sum_length(self.geo_utils.way_length(json_object))

    # Total count by key
    def total_keys(self, key: str):
        self.results.bykey(key).sum()

    # Get stats for a Feature object
    def get_object_stats(self, json_object: object):
        for prop in self.getProperty(self.config.properties_prop, json_object).items():
            key = prop[0]
            value = prop[1]

            if value:
                self.total_keys(key)

            if self.config.keys and prop[0] in self.config.keys:
                if self.config.length:
                    self.calculate_length_bykey(json_object,key)
                if self.config.area:
                    self.calculate_area_bykey(json_object, key)

            if self.config.value_keys and key in self.config.value_keys:
                self.count_value_bykey(json_object, key, value)
                if self.config.length:
                    self.calculate_length_bykeyval(json_object, key, value)
                if self.config.area:
                    self.calculate_area_bykeyval(json_object, key, value)

            if key == "name" and not "name" in self.results.languages:
                self.results.languages.append("name")

            if len(key) == 7 and "name:" in key and key.index("name:") == 0:
                if not key in self.results.languages:
                    self.results.languages.append(key)

        if self.config.length:
            self.calculate_length(json_object)

        if self.config.area:
            self.calculate_area(json_object)

        self.results.sum()

        self.clean_cache()

    # Process a GeoJSON object
    def process_geojson(self, geojson_object: object):
        features_total = len(geojson_object["features"])
        for feature in geojson_object["features"]:
            self.get_object_stats(feature)
            if self.config.verbose:
                percent = round((self.results.count * 100) / features_total, 2)
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
        return json.dumps(self.dict())

    # Dumps results
    def dump(self):
        print(self.json())

    def dict(self):
        return self.results.to_dict(clean=self.config.clean)
