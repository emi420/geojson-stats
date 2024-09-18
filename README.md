# geojson-stats

Stats for GeoJSON data

- Total features count
- Properties count
- Distance for lines (total / per property)
- Area for polygons (total / per property)

## Quick start

### Install requirements

```bash
pip install pyproj shapely 
```

### Run

```bash
python geojson-stats.py -f <GEOJSON FILE>
```

### Example

Getting stats from Turkmenistan Waterways (OpenStreetMap Export)
downloaded from [HDX](https://data.humdata.org/dataset/hotosm_tkm_waterways)

```bash
python geojson-stats.py -f example/tkm_waterways.geojson
```

```json
{
  "count": 4447,
  "stats": {
    "waterway": 4447,
    "source": 173,
    "osm_id": 4447,
    "osm_type": 4447,
    "km": 23318.87603608974,
    "layer": 821,
    "tunnel": 883,
    "name": 535,
    "name:en": 223,
    "name:tk": 99,
    "width": 94
  }
}
```

## Usage

```bash
geojson-stats.py [-h] [--file FILE] [--url URL] [--silent] [--stream] [--distance-keys DISTANCE_KEYS] [--area-keys AREA_KEYS]
                        [--distance] [--area] [--projected] [--proj PROJ]

options:
  -h, --help            show this help message and exit
  --file FILE, -f FILE  GeoJSON file to analyze
  --url URL, -u URL     URL of GeoJSON file to analyze
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
