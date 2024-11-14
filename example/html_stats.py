from geojson_stats.stats import Stats, Config
from geojson_stats.html import Html

config = Config(
  clean = True,
  length = True,
  keys=["waterway"],
  value_keys=["waterway"]
)

stats = Stats(config)
stats.process_file("./tkm_waterways.geojson")

html = Html("./waterway_stats_tpl.html", stats)
html.dump()
