# Proof-of-Concept - Splunk SH Alert Upstream Interface with end to end delivery assurance
The goal of the POC is to demonstrate the end-to-end delivery of the
alerts generated on the Splunk Search Head towards upstream
platform.

The alerts are scheduled on the Search Head as scheduled searches.
Once the alert is generated, it is forwarded to the Upstream platform.
Realtime searches are not supported during the POC. Also, alerts
must be configured to generate one liner of the results.

Upstream platform will generate a report of received alerts and
will send the report back to the Splunk Indexers using Universal
Forwarder.

Search Head will perform the gap analysis and forwards the alerts
that are not received by the upstream platform.

## Architecture

	+-------------------------------------------------------------------------------+
	|                                                                 /--> Receiver 1|
	|Splunk Search Head -> Scheduled Search ->  upstream_sendevent   ----> Receiver 2|
	|       |                                    /                      |            |
	|       |--  Missing Events Replay      --> /                       |            |
	|       |                                                           |            |
	|Splunk Indexer                                                 log files        |
	|        \                                                          |            |
	|         \ <--------------------------------------------       Splunk UFs       |
	|                                                                                |
	+--------------------------------------------------------------------------------+
	
## Design
1. There is an app called *end2end_app* that should be installed on the 
Search Head. 
2. There is scheduled search executed each minute that generates the alert on
invalid searches. Alerts contain sid - unique identifier of the search.
3. Alerts are piped to "| upstream\_sendevent" command.
4. upstream\_sendevent command will display the events in the GUI and forwards
the events to multiple destinations sequentially.
5. Receiver is simple TCP receiver that records the events in three files
- /tmp/all\_logs.log contains all events
- /tmp/received\_logs.log contains all received events
- /tmp/missed\_logs.log contains missed events.
6. Receiver is mimicking the delivery hickups. When it receives new event,
it decides with 25% probability that it will be missed events. Missed event
is recorded in separate file.
7. All files are taken by Splunk Universal Forwarder and are indexed by Indexer.
8. Event replay is performed by the 'eventreplay.py'
9. It searches through the received\_logs.log and compares it with existing
alerts via REST API.
10. There should be two unique identifier, one from Search Head, one from
upstream provider.
11. If there is no identifier from the upstream provider, then replay is
executed.
12. Alerts contain all data and it is not needed to reschedule search again.
13. The data is received over REST API and replayed towards the Receiver.
14. Receiver may choose to accept it or missed it (see 6.)

## Howto
- see also INSTALL.md
- simplified setup: run splunk in standalone mode in localhost,
the receiver on the localhost, Universal Forwarder on the localhost
- copy splunk configs to the respective folders
- execute: python upstream\_receiver.py
- put end2end\_app to the /opt/splunk/etc/apps
- login to splunk, change context to end2end\_app and type invalid search
such as ||x ||c
- there are four sources in Splunk:
1. source=iface-sh2esm
2. source=esm\_event\_report\_all
3. source=esm\_event\_report\_success
4. source=esm\_event\_report\_failed
- sent events are audited in source=iface-sh2esm
- if events are not captured in success log, they can be replayed
- to replay events, manually execute python eventreplay.py


## Known issues
- Realtime searches are not supported since the sid is not generated in 
the same way as scheduled search
- Multiple results in the alert are not supported. The POC would need to
be extended by partial alert replay.


