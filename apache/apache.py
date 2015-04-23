import requests
import tempfile
import json
import subprocess

from amonagent.modules.plugins import AmonPlugin

class ApachePlugin(AmonPlugin):
	
	VERSION = '1.0.3'

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
		log_file = self.config.get('log_file')
		response = None


		try:
			self.get_versions(status_url)
		except Exception, e: 
			self.error(e)
			

		try:
			response = requests.get(status_url, timeout=5)
		except Exception, e:
			self.error(e)
			


		try:
			status_code = response.status_code
		except:
			status_code = None
		
		if status_code == 200:
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

		# Get detailed stats with goaccess
		configfile = tempfile.NamedTemporaryFile()
		# Default log format - with vhosts
		log_content = """
date_format %d/%b/%Y
log_format  %^:%^ %h %^[%d:%t %^] "%r" %s %b
time_format  %H:%M:%S
"""
		configfile.write(log_content)
		configfile.flush()

		command = ["goaccess", "-f", log_file, "-p", configfile.name, "-o", "json"]

		server_data = subprocess.Popen(command, stdout=subprocess.PIPE if format else None)
		out, err = server_data.communicate()

		print out

		try:
			json_result = json.loads(out)
		except:
			json_result = None

		if json_result:
			general =  json_result.get('general')
			requests_result = json_result.get('requests')
			not_found_result = json_result.get('not_found')

			ignored_general_keys = ['date_time', 'log_path']
			for key, value in general.items():
				if key not in ignored_general_keys:
					name = self.normalize(key)
					self.counter(name, value)
			
			loop_over = {'requests': requests_result, 'not_found': not_found_result}
			for key, data in loop_over.items():
				if data:
					result = {'data': []}

				try:
					headers = data[0].keys()
				except:
					headers = None

				if headers:
					result['headers'] = headers

					for r in data:
						result['data'].append(r.values())

				self.result[key] = result