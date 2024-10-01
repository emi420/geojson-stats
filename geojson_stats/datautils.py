
# Utils for labelling
class DataUtils:
    KM_LABEL = "km"
    KM2_LABEL = "area_km2"

    def key_km(key: str):
        return "{0}_{1}".format(key, DataUtils.KM_LABEL)

    def key_area_km2(key):
        return "{0}_{1}".format(key, DataUtils.KM2_LABEL)
