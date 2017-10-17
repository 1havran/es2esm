#!/usr/bin/env python

import socket
import upstream_submit

_destinations = ["emea:127.0.0.1:19997","apac:127.0.0.1:19998"]
_index = "main"
_source = "iface-sh2esm"
_sourcetype = "audit"
_tcp_timeout = 0.1

class Upstream:
	def __init__(self):
		self.destinations = _destinations
		self.timeout = _tcp_timeout
		self.index = _index
		self.source = _source
		self.sourcetype = _sourcetype

	def _get_timeout(self):
		return float(self.timeout)

	def _send_data(self, data, data_length, dhost, dport, tag):
		status = "n/a"
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			#s.settimeout(self._get_timeout) float error
			s.settimeout(0.1)
			s.connect((dhost, int(dport)))
			s.send(data)
			status = "ok"
			data = s.recv(1024)
			s.close()
		except socket.error, ex:
			status = ex
		except Exception, ex:
			print ex
        		import traceback
		        traceback.print_exc(file=sys.stdout)
		finally:
        		status_msg = "type=\"summary\" tag=\"%s\" host=\"%s\" port=\"%s\" connection_status=\"%s\" notable_event_count=%s\n" % (dhost, dport, status, data_length, tag)
        		return status_msg

	def sendData(self, data, length, destinations):
		for d in destinations:
			tag, dhost, dport = d.split(":")			
			status_msg = self._send_data(data, length, dhost, dport, tag)
                        submit.main(status_msg, tag, self.source, self.sourcetype, self.index)


	def getDestinations(self, i):
		# logic how to select destinations
		# currenly just per id
		if type(i) != int:
			return self.destinations
		if i >-1 and i < len(self.destinations):
			return [self.destinations[i]]
		else:
			return self.destinations
	

	def getRouting(self, region):
		result = -1
		for i in range(0, len(self.destinations)):
			if self.destinations[i].split(":")[0] == region:
				result = i
				break
		return result
