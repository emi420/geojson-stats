# geojson-stats

Stats for GeoJSON data 

(total / per property / per value)

- Features count
- Length for lines 
- Area for polygons

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
from geojson_stats.stats import Stats, Config

config = Config(
  clean = True,
  length = True,
  keys=["waterway"]
  value_keys=["waterway"]
)

stats = Stats(config)
stats.process_file("example/tkm_waterways.geojson")

print("Count:", stats.results.count)
stats.dump()
```

### Example

Getting stats from Turkmenistan Waterways (OpenStreetMap Export)
downloaded from [HDX](https://data.humdata.org/dataset/hotosm_tkm_waterways)

```bash
python geojson_stats/cli.py -f example/tkm_waterways.geojson --keys waterway --value-keys waterway --length --verbose
```

```json
{
  "count": 4447,
  "length": 23318.876036089594,
  "key": {
    "waterway": {
      "count": 4447,
      "length": 23318.876036089594,
      "value": {
        "canal": {
          "count": 2164
        },
        "drain": {
          "count": 370
        },
        "river": {
          "count": 435
        },
        "ditch": {
          "count": 1125
        },
        "wadi": {
          "count": 26
        },
        "stream": {
          "count": 281
        },
        "dam": {
          "count": 42
        },
        "weir": {
          "count": 2
        },
        "derelict_canal": {
          "count": 2
        }
      }
    },
    "source": {
      "count": 173
    },
    "osm_id": {
      "count": 4447
    },
    "osm_type": {
      "count": 4447
    },
    "layer": {
      "count": 821
    },
    "tunnel": {
      "count": 883
    },
    "name": {
      "count": 535
    },
    "name:en": {
      "count": 223
    },
    "name:tk": {
      "count": 99
    },
    "width": {
      "count": 94
    }
  }
}
```

## License

GNU Affero General Public License

(c) Emilio Mariscal 2024
