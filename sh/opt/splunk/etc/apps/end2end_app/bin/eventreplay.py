#!/usr/bin/env python

import search
import sendevent
import json, sys, subprocess
from cStringIO import StringIO


verbose = 0
sids = []
gapSearch = "| rest /servicesNS/admin/end2end_app/alerts/fired_alerts/Invalid%20Search%20Alert | fields sid | rex field=sid \"(?<info_sid>^.*)$\" | fields info_sid | dedup info_sid | append [ search index=main source=\"esm_event_report_success\" | table info_sid | dedup info_sid] | stats count by info_sid | search count<2"
jobSearch = "/services/search/jobs/%s/results"
splunkCredentials = "admin:asdfasdf"

def runSearch(params):
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    search.main(params)
    sys.stdout = old_stdout
    return mystdout.getvalue()

def getJobQuery(sid):
    return jobSearch % (sid)

def getSearchResults(sid):
    result = ""
    spl = "https://localhost:8089" + getJobQuery(sid)
    result = subprocess.Popen(['curl', '-sk', '-u', splunkCredentials, spl, '--get', '-d', 'output_mode=json'], stdout=subprocess.PIPE).communicate()[0]
    return result
        
def main():
    results = runSearch(['--output_mode', 'json', gapSearch])

    alerts = json.loads(results)
    for alert in alerts['results']:
        sids.append(alert['info_sid'])

    for sid in sids:
        print sid
        results = getSearchResults(sid)
        if results:
            results = json.loads(results)
            try:
                for result in results['results']:
                    if verbose: 
                        print result
                    status_msg = sendevent.send_data(json.dumps(result), len(result))
                    sendevent.index_data(status_msg)
            except:
                pass

if __name__ == "__main__":
    main()

