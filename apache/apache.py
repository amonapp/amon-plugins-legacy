import requests

from amonagent.plugin import AmonPlugin

class ApachePlugin(AmonPlugin):
	
	VERSION = '1.0'

	GAUGES = {
		'IdleWorkers': 'performance.idle_workers',
		'BusyWorkers': 'performance.busy_workers',
		'CPULoad': 'performance.cpu_load',
		'ReqPerSec': 'requests.per.second', 
		'Total kBytes': 'net.bytes',
		'Total Accesses': 'net.hits',
	}

	def get_versions(self, status_url):

		response = requests.head(status_url)
		library = response.headers.get('server')

		self.version(apache=library, plugin=self.VERSION)


	def collect(self):
		status_url = self.config.get('status_url')


		self.get_versions(status_url)

		response = requests.get(status_url)
		
		status = response.text.splitlines()
		for line in status:
			key, value = line.split(':')
	
			if key in self.GAUGES.keys():
				normalized_key = self.GAUGES[key]
				

				try:
					value = float(value)
				except ValueError:
					continue

			
				self.gauge(normalized_key, value)