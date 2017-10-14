# Proof-of-Concept - Splunk SH Alert Upstream Interface with end to end delivery assurance
The goal of the POC is to demonstrate end-to-end delivery of the
alerts generated on the Splunk Search Head towards upstream
platform.

The alerts are scheduled on the Search Head as scheduled searches.
Once the alert is generated, it is forwarded to the Upstream platform.
Realtime searches are not supported during the POC. Also, alerts
must be configured to generate one line of the results.

Upstream platform will generate a report of received alerts and
will send the report back to the Splunk Indexers using Universal
Forwarders.

Search Head will perform the gap analysis and forwards the alerts
that are not received by the upstream platform.

## Architecture
                                                           /--> Reciever 1
Splunk Search Head -> Scheduled Search -> "| sendevent cmd" --> Reciever 2
       |                                    /                |
       |--- eventreplay.py --------------> /                 |
       |                                                     |
Splunk Indexer                                           log files
        \                                                    |
         \ <-------------------------------------------- Splunk UFs

## Design
1. There is an app called *end2end_app* that should be installed on the 
Search Head. 
2. There is scheduled search each minute that generates the alert on
invalid searches. Alerts contain sid, unique identifier of the search.
3. Alerts are piped to "| sendevent" command.
4. sendevent command will display the events in the GUI and forwards
the events to multiple destinations sequentially.
5. Reciever is simple TCP reciever that records the events in three files
5.1 /tmp/all_logs.log contains all events
5.2 /tmp/received_logs.log contains all received events
5.3 /tmp/missed_logs.log contains missed events.
6. Reciever is mimicking the delivery hickups. When it receives new event,
it decides with 25% probability that it will be missed events. Missed event
is recorded in separate file.
7. All files are taken by Splunk Universal Forwarder and are indexed by Indexer.
8. Event replay is performed by the 'eventreplay.py'
9. It searches through the received_logs.log and compares it with existing
alerts via REST API.
10. There should be two unique identifier, one from Search Head, one from
upstream provider.
11. If there is no identifier from the upstream provider, then replay is
executed.
12. Alerts contain all data and it is not needed to reschedule search again.
13. The data is received over REST API and replayed towards the Receiver.
14. Since Receiver may choose to accept it or missed it (see 6.)

## Installation
- simplified setup: run splunk in standalone mode in localhost,
the receiver on the localhost, Universal Forwarder on the localhost
- copy splunk configs to the respective folders
- execute: python reciever.py
- put end2end_app to the /opt/splunk/etc/apps
- login to splunk, change context to end2end_app and type invalid search
such as ||x ||c


## Known issues
- Realtime searches are not supported since the sid is not generated in 
the same way as scheduled search
- Multiple results in the alert are not supported. The POC would need to
be extended by partial alert replay.


