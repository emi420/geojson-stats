from geojson_stats.stats import Stats, Config
from geojson_stats.html import Html

config = Config(
  clean = True,
  length = True,
  keys=["waterway"],
  value_keys=["waterway"]
)

stats = Stats(config)
stats.process_file("example/tkm_waterways.geojson")

# stats.dump()

html = Html("example/waterway_stats_tpl.html", stats)
html.dump()
