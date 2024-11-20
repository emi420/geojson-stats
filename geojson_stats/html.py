from .models import TotalStats
from string import Template
import re

TPL_VAR_PATTERN = r'\$\{([a-zA-Z0-9_]+(?:\_[a-zA-Z0-9_]+)*)\}'

def get_val(d, k):
    keys = k.split('_')
    for key in keys:
        if key.isdigit():
            if key == keys[-1]:
                try:
                    return list(d.keys())[int(key)]
                except:
                    return "-"
            else:
                try:
                    d = d[list(d.keys())[int(key)]]
                except:
                    return "-"
        elif isinstance(d, dict) and key in d:
            d = d[key]
        else:
            return None
    if key == "percent":
        return "{d}%".format(d=d)
    return d

# Create HTML reports with stats
class Html:

    tpl: str = ""
    stats: TotalStats

    def __init__(self, tpl_file: str, stats: TotalStats):
        self.tpl_file = tpl_file
        self.stats = stats.dict()

        with open(tpl_file, 'r') as tpl_html:
            self.tpl = tpl_html.read()

    def build(self):
        matches = re.findall(TPL_VAR_PATTERN, self.tpl)
        replacements = {}
        for match in matches:
            value = get_val(self.stats, match)
            if isinstance(value, float):
                value = round(value, 2)
            replacements[match] = value
        
        template = Template(self.tpl)
        return template.substitute(replacements)

    def dump(self):
        print(self.build())