#!/usr/bin/env python

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import splunklib.client as client

try:
    from utils import *
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")

def main(message, host, source, sourcetype, index):
    opts = parse(None, None, ".splunkrc", usage=None)
    kwargs_splunk = dslice(opts.kwargs, FLAGS_SPLUNK)
    service = client.connect(**kwargs_splunk)
    service.indexes[index].submit(message, host, source, sourcetype)


if __name__ == "__main__":
    main(sys.argv[1:])

