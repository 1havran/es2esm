#!/usr/bin/env python

import search
import upstream as u
import json, sys, subprocess
from cStringIO import StringIO


splunkCredentials = "admin:changeme"
alertName = "Failed%20Splunk%20Logins"
verbose = 1

splSearchAlertSids = "| rest /servicesNS/admin/end2end_app/alerts/fired_alerts/%s | fields sid | rex field=sid \"(?<info_sid>^.*)$\" | fields info_sid | dedup info_sid" % (alertName)
splSearchDeliveredAlerts = "search earliest=-1d@d latest=-1m@m index=main source=\"esm_event_report_success\" | dedup info_sid, upstream_id | table info_sid, upstream_id"
jobSearch = "/services/search/jobs/%s/results"

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
    up = u.Upstream()

    # get sids from available alerts
    sids = []
    results = runSearch(['--output_mode', 'json', splSearchAlertSids])
    data = json.loads(results)
    for d in data['results']:
        sids.append(d['info_sid'])

    # get sids from delivered alerts and create a dict with received sids and results within the sids
    received = {}
    results = runSearch(['--output_mode', 'json', splSearchDeliveredAlerts])
    data = json.loads(results)
    for d in data['results']:
        info_sid = d['info_sid']
        upstream_id = d['upstream_id']
        if info_sid not in received:
            received[info_sid] = []
        received[info_sid].append(upstream_id)

    # compare results from alerts against received sids and resend missing results
    for sid in sids:
        results = getSearchResults(sid)
        if results:
            results = json.loads(results)
            try:
                for result in results['results']:

                    alert_replay = False
                    info_sid = result['info_sid']
                    upstream_id = result['upstream_id']

                    if info_sid not in received:
                        alert_replay = True
                    else:
                        alert_replay = upstream_id not in received[info_sid]
                        
                    if alert_replay:
                        if verbose:
                            print result
                        dest = up.getDestinations(up.getRouting(result['region']))
                        json_data = json.dumps(result)
                        up.sendData(json_data, len(result), dest)
            except Exception as ex:
                print ex
                pass

if __name__ == "__main__":
    main()

