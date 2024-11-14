#!/usr/bin/python3

import argparse
import resource
import os

from .stats import Config, Stats
from .html import Html

# Entrypoint for command line
def main():
    args = argparse.ArgumentParser()
    args.add_argument("--file", "-f", help="GeoJSON file to analyze", type=str, default=None)
    args.add_argument("--url", "-u", help="URL of GeoJSON file to analyze", type=str, default=None)
    args.add_argument("--verbose", "-v", help="Verbose", default=False, action='store_true')
    args.add_argument("--stream", help="Stream a file (use less memory)", default=False, action='store_true')
    args.add_argument("--keys", help="Keys for calculating length or area", type=str, default = None)
    args.add_argument("--value-keys", help="Keys for counting values", type=str, default = None)
    args.add_argument("--length", help="Calculate total length of all linestrings", \
                    default=False, action='store_true')
    args.add_argument("--area", help="Calculate total area of all polygons", \
                    default=False, action='store_true')
    args.add_argument("--projected", help="Use projected coordinated in meters", \
                    default=False, action='store_true')
    args.add_argument("--proj", help="Data projection system", type=str, default = "WGS84")
    args.add_argument("--no-clean", help="Keep zero and empty results", default=False, action='store_true')
    args.add_argument("--properties-prop", help="Properties to analyze (ex: properties or properties.tags)", type=str, default="properties")
    args.add_argument("--html", help="HTML template", type=str, default=None)
    args = args.parse_args()

    config = Config(
        verbose=args.verbose,
        keys = args.keys.split(",") if args.keys else [],
        length = args.length,
        area = args.area,
        value_keys = args.value_keys,
        projected = args.projected,
        clean = not args.no_clean,
        proj = args.proj,
        properties_prop = args.properties_prop
    )
    stats = Stats(config)

    if args.url or args.file:

        if args.url:
            stats.process_url(args.url)

        elif args.file:
            if args.verbose:
                print("\nFile size is {0} MB\n".format(round(os.stat(args.file).st_size / (1024 * 1024), 2)))
            if args.stream:
                stats.process_file_stream(args.file)
            else:
                stats.process_file(args.file)

        if args.html:
            html = Html(args.html, stats)
            html.dump()
        else:
            stats.dump()

        if args.verbose:
            print('\nPeak Memory Usage =', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
            print('User Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_utime)
            print('System Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_stime)

if __name__ == "__main__":
    main()
