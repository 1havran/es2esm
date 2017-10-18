# get splunk enterprise
	wget -O splunk-7.0.0-c8a78efdd40f-linux-2.6-x86_64.rpm 'https://www.splunk.com/bin/splunk/DownloadActivityServlet?architecture=x86_64&platform=linux&version=7.0.0&product=splunk&filename=splunk-7.0.0-c8a78efdd40f-linux-2.6-x86_64.rpm&wget=true'

# get splunk uf
	wget -O splunkforwarder-7.0.0-c8a78efdd40f-linux-2.6-x86_64.rpm 'https://www.splunk.com/bin/splunk/DownloadActivityServlet?architecture=x86_64&platform=linux&version=7.0.0&product=universalforwarder&filename=splunkforwarder-7.0.0-c8a78efdd40f-linux-2.6-x86_64.rpm&wget=true'

# install
	rpm -Uvh splunk-7.0.0-c8a78efdd40f-linux-2.6-x86_64.rpm
	rpm -Uvh splunkforwarder-7.0.0-c8a78efdd40f-linux-2.6-x86_64.rpm
	cp /opt/splunk
	wget http://download.splunk.com/misc/sdk/python/splunk-sdk-python-1.6.2.zip
	unzip splunk-sdk-python-1.6.2.zip
	ln -sf splunk-sdk-python-1.6.2 splunk-sdk-python

# git
	git clone https://github.com/1havran/es2esm.git
	cd es2esm

# poc
	cp sh/opt/splunk/.splunkrc ~
	#change credentials for the REST API access 
	#vim ~/.splunkrc
	#change credentials in sh/opt/splunk/etc/apps/end2end_app/bin/upstream_eventreplay.py
	cp -r sh/opt/splunk/etc/apps/end2end_app /opt/splunk/etc/apps
	cp -r sh/opt/splunk/etc/system/local/inputs.conf /opt/splunk/etc/system/local
	cp -r esm/opt/splunkforwarder/etc/system/local/{inputs,outputs}.conf /opt/splunkforwarder/etc/system/local
	export PYTHONPATH=/opt/splunk/splunk-sdk-python

# start receiver in separate console
	python esm/upstream_receiver.py
![](https://github.com/1havran/es2esm/blob/master/screenshots/receiver.png)

# start splunk
	${sh/opt/splunk/.bash_profile | grep PYTHONPATH}
	cp sh/opt/splunk/.bash_profile /opt/splunk
	/opt/splunk/bin/splunk start --accept-license
	/opt/splunkforwarder/bin/splunk start --accept-license

# log to splunk
	chromium http://localhost:8000/en-US/app/end2end_app/search
![](https://github.com/1havran/es2esm/blob/master/screenshots/splunkapp.png)

# upstream random event using  "| upstream"
	index=_audit user=admin action="login attempt" info=succeeded | stats count by user,action | eval region="emea" | upstream
	# check on the console where receiver.py is running if the event has been received
![](https://github.com/1havran/es2esm/blob/master/screenshots/upstream_sendevent.png)
	
![](https://github.com/1havran/es2esm/blob/master/screenshots/sendevent_receiver.png)

# ingest failed login events manually
	logout from splunk
	login to splunk with invalid credentials
![](https://github.com/1havran/es2esm/blob/master/screenshots/failedlogin.png)

# check alerts
	# The alert will be triggered in a minute in the Splunk GUI -> Activity -> Triggered Alerts
	log to splunk, wait a minute
![](https://github.com/1havran/es2esm/blob/master/screenshots/alert.png)

	# Click on the alert to see the results
![](https://github.com/1havran/es2esm/blob/master/screenshots/alertdetail.png)

	# Examine the region of the event
	Event might be "emea" or "apac". The region is randomly selected by the alert logic. If it is "apac", then it has not been received by the Receiver as we started EMEA Receiver only. See first screenshot.
![](https://github.com/1havran/es2esm/blob/master/screenshots/apacregion.png)

![](https://github.com/1havran/es2esm/blob/master/screenshots/apacreceiverdown.png)

# start apac receiver
	python upstream_receiver.py 1
![](https://github.com/1havran/es2esm/blob/master/screenshots/apacreceiver.png)

# eventreplay
	python upstream_eventreplay.py
![](https://github.com/1havran/es2esm/blob/master/screenshots/upstream_eventreplay.png)

	# receiver will display the events on the stdout
![](https://github.com/1havran/es2esm/blob/master/screenshots/apacreceiverok.png)

	# sometimes events must be replayed multiple times as receiver moves events to missed with 25% probability.
![](https://github.com/1havran/es2esm/blob/master/screenshots/eventreplay2.png)

# to schedule event replay
	cp es2esm/sh/etc/crontab /etc/cron.d/upstream_eventreplay
