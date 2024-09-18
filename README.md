# geojson-stats

Stats for GeoJSON data

- Total features count
- Properties count
- Distance for lines (total / per property)
- Area for polygons (total / per property)

## Quick start

### Install requirements

```
pip install pyproj shapely 
```

### Run

```
python geojson-stats.py -f <GEOJSON FILE>
```

## Usage
```
geojson-stats.py [-h] [--file FILE] [--silent] [--stream] [--distance-keys DISTANCE_KEYS]
                        [--area-keys AREA_KEYS] [--distance] [--area] [--projected] [--proj PROJ]

options:
  -h, --help            show this help message and exit
  --file FILE, -f FILE  GeoJSON file to analyze
  --silent, -s          Silent
  --stream              Stream a file (use less memory)
  --distance-keys DISTANCE_KEYS
                        Keys for calculating distance in km
  --area-keys AREA_KEYS
                        Keys for calculating area in km2
  --distance            Calculate total distance of all linestrings
  --area                Calculate total area of all polygons
  --projected           Use projected coordinated in meters
  --proj PROJ           Data projection system
  ```

## License

GNU Affero General Public License

(c) Emilio Mariscal 2024
