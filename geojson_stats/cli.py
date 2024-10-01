#!/usr/bin/python3

import argparse
import resource
import os

from stats import Config, Stats

# Entrypoint for command line
def main():
    args = argparse.ArgumentParser()
    args.add_argument("--file", "-f", help="GeoJSON file to analyze", type=str, default=None)
    args.add_argument("--url", "-u", help="URL of GeoJSON file to analyze", type=str, default=None)
    args.add_argument("--verbose", "-v", help="Verbose", default=False, action='store_true')
    args.add_argument("--stream", help="Stream a file (use less memory)", default=False, action='store_true')
    args.add_argument("--distance-keys", help="Keys for calculating distance in km", default = None)
    args.add_argument("--area-keys", help="Keys for calculating area in km2", default = None)
    args.add_argument("--distance", help="Calculate total distance of all linestrings", \
                    default=False, action='store_true')
    args.add_argument("--area", help="Calculate total area of all polygons", \
                    default=False, action='store_true')
    args.add_argument("--projected", help="Use projected coordinated in meters", \
                    default=False, action='store_true')
    args.add_argument("--proj", help="Data projection system", default = "WGS84")
    args = args.parse_args()

    config = Config(
        verbose=args.verbose,
        distance_keys = args.distance_keys.split(",") if args.distance_keys else [],
        area_keys = args.area_keys.split(",") if args.area_keys else [],
        distance = args.distance,
        area = args.area,
        projected = args.projected,
        proj = args.proj
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

        stats.dump()

        if args.verbose:
            print('\nPeak Memory Usage =', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
            print('User Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_utime)
            print('System Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_stime)

if __name__ == "__main__":
    main()
