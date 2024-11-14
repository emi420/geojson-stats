# geojson-stats

Stats for GeoJSON data 

(total / per property / per value)

- Features count
- Length for lines 
- Area for polygons

## Quick start

### Install

Directly from the main branch:

```bash
pip install geojson-stats
```

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
  keys=["waterway"],
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
geojsonstats -f example/tkm_waterways.geojson --keys waterway --value-keys waterway --length --verbose
```

```json
{
  "count": 4447,
  "length": 23318.876036089594,
  "languages": {
    "list": [
      "name",
      "name:en",
      "name:tk"
    ],
    "count": 3
  },
  "key": {
    "waterway": {
      "count": 4447,
      "percent": 100.0,
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
    "osm_id": {
      "count": 4447,
      "percent": 100.0
    },
    "osm_type": {
      "count": 4447,
      "percent": 100.0
    },
    "tunnel": {
      "count": 883,
      "percent": 19.86
    },
    "layer": {
      "count": 821,
      "percent": 18.46
    },
    "name": {
      "count": 535,
      "percent": 12.03
    },
    "name:en": {
      "count": 223,
      "percent": 5.01
    },
    "source": {
      "count": 173,
      "percent": 3.89
    },
    "name:tk": {
      "count": 99,
      "percent": 2.23
    },
    "width": {
      "count": 94,
      "percent": 2.11
    }
  }
}
```

### HTML

You can also generate stats in HTML format, using a template.

For example:

```bash
geojsonstats -f example/tkm_waterways.geojson --keys waterway --value-keys waterway --length --html example/waterway_stats_tpl.html > stats.htm
```
<img width="906" alt="Screenshot 2024-11-14 at 00 01 26" src="https://github.com/user-attachments/assets/b50a1c26-0126-4f57-8516-7d02343d6a6e">

## License

GNU Affero General Public License

(c) Emilio Mariscal 2024
