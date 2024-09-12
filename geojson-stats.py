'''
    Extracts metadata from OSM data
'''

import argparse
import resource
import os
import json

def processFile(filename):
    file = open(filename)
    results = {
        "count": 0,
        "stats" : {}
    }
    bytes_total = os.stat(filename).st_size
    bytes_processed = 0
    for line in file:
        bytes_processed += len(line)
        if line.startswith('{ "type": "Feature"'):
            if line[-2:-1] == ",":
                json_string = line[:-2]
            json_object = json.loads(json_string)
            for prop in json_object["properties"].items():
                if prop[1]:
                    key = prop[0]
                    if key in results["stats"]:
                        results["stats"][key] += 1
                    else:
                        results["stats"][key] = 1
            results["count"] += 1
            percent = round((bytes_processed * 100) / bytes_total, 2)
            print("Processed: {0}% ({1})".format(percent, results["count"]), end='\r', flush=True)

    return results

def main():
    args = argparse.ArgumentParser()
    args.add_argument("--file", "-f", help="GeoJSON file to analyze", type=str, default=None)
    args = args.parse_args()

    if args.file:
        print("File size is {0} MB".format(round(os.stat(args.file).st_size / (1024 * 1024), 2)))
        result = processFile(args.file)
        print("\n", result, "\n")
        print('Peak Memory Usage =', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        print('User Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_utime)
        print('System Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_stime)


if __name__ == "__main__":
    main()
