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
    "name": {
      "count": 4447
    },
    "name:en": {
      "count": 4447
    },
    "waterway": {
      "count": 4447,
      "length": 23318.876036089594,
      "value": {
        "canal": {
          "count": 2164,
          "length": 11890.79586499543
        },
        "drain": {
          "count": 370,
          "length": 636.8213551633588
        },
        "river": {
          "count": 435,
          "length": 8353.148822879351
        },
        "ditch": {
          "count": 1125,
          "length": 1251.067586054797
        },
        "wadi": {
          "count": 26,
          "length": 133.95910280981897
        },
        "stream": {
          "count": 281,
          "length": 982.3192418240153
        },
        "dam": {
          "count": 42,
          "length": 68.91994831893784
        },
        "weir": {
          "count": 2,
          "length": 0.03208190453249057
        },
        "derelict_canal": {
          "count": 2,
          "length": 1.812032139385983
        }
      }
    },
    "covered": {
      "count": 4447
    },
    "width": {
      "count": 4447
    },
    "depth": {
      "count": 4447
    },
    "layer": {
      "count": 4447
    },
    "blockage": {
      "count": 4447
    },
    "tunnel": {
      "count": 4447
    },
    "natural": {
      "count": 4447
    },
    "water": {
      "count": 4447,
      "length": 23318.876036089594,
      "value": {
        "null": {
          "count": 4447,
          "length": 23318.876036089594
        }
      }
    },
    "source": {
      "count": 4447
    },
    "name:tk": {
      "count": 4447
    },
    "osm_id": {
      "count": 4447
    },
    "osm_type": {
      "count": 4447
    }
  }
}
```

## License

GNU Affero General Public License

(c) Emilio Mariscal 2024
