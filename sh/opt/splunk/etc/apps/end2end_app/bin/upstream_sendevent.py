#!/usr/bin/env python

import csv, json, sys
import usercount as spl
import upstream as u

def main(argv):
    stdin_wrapper = spl.Reader(sys.stdin)
    buf, settings = spl.read_input(stdin_wrapper, has_header = True)
    up = u.Upstream()

    data = []
    routing_region = ""
    for row in csv.DictReader(buf):
	routing_region = row['region']
        data.append(row)

    spl.output_results(data)

    dest = up.getDestinations(up.getRouting(routing_region))
    up.sendData(json.dumps(data), len(data), dest)

if __name__ == "__main__":
    try: 
        main(sys.argv)
    except Exception:
        import traceback
        traceback.print_exc(file=sys.stdout)
