#!/usr/bin/env python
#
# Copyright 2011-2015 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""A command line utility that submits event data to Splunk from stdin."""

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

