# geojson-stats

Stats for GeoJSON data

- Total features count
- Properties count
- Distance for lines (total / per property)
- Area for polygons (total / per property)

## Quick start

### Install

Directly from the main branch:

`pip install git+https://github.com/emi420/geojson-stats`

~Latest on PyPi: pip install geojson-stats~

### Usage

```bash
geojsonstats -f <GEOJSON FILE>
```

Help and options:

```bash
geojsonstats -h
```

#### Python

```py
from geojson_stats.stats import Stats
stats = Stats()
stats.config.distance = True
stats.process_file("example/tkm_waterways.geojson")
print("Count:", stats.results.count)
print("Stats:", stats.results.stats)
```

### Example

Getting stats from Turkmenistan Waterways (OpenStreetMap Export)
downloaded from [HDX](https://data.humdata.org/dataset/hotosm_tkm_waterways)

```bash
geojsonstats -f example/tkm_waterways.geojson --distance
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

## License

GNU Affero General Public License

(c) Emilio Mariscal 2024
