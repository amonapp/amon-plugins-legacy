import requests

from amonagent.plugin import AmonPlugin

class ApachePlugin(AmonPlugin):
	
	VERSION = '1.0'

	GAUGES = {
		'IdleWorkers': 'performance.idle_workers',
		'BusyWorkers': 'performance.busy_workers',
		'ReqPerSec': 'net.requests.per.second', 
		'Total kBytes': 'net.bytes',
		'Total Accesses': 'net.hits',
	}


	def collect(self):
		status_url =  self.config.get('status_url')

		response = requests.get(status_url)
		
		status = response.text.splitlines()
		for line in status:
			key, value = line.split(':')
	
			if key in self.GAUGES.keys():
				normalized_key = self.GAUGES[key]
				value = int(value)
				self.gauge(normalized_key, value)
