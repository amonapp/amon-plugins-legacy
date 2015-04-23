import requests
import re
import sys
import subprocess
import tempfile
import json

from amonagent.modules.plugins import AmonPlugin

class NginxPlugin(AmonPlugin):

	VERSION = '1.0.2'

	"""Tracks basic nginx metrics via the status module
	* number of connections
	* number of requets per second

	Requires nginx to have the status option compiled.
	See http://wiki.nginx.org/HttpStubStatusModule for more details

	$ curl http://localhost/nginx_status/
	Active connections: 8
	server accepts handled requests
	 1156958 1156958 4491319
	Reading: 0 Writing: 2 Waiting: 6

	"""


	def collect(self):
		status_url =  self.config.get('status_url')
		log_file = self.config.get('log_file')


		try:
			response = requests.get(status_url, timeout=5)
		except Exception, e:
			self.error(e)
	

		whitelist = ['accepts','handled','requests']
		

		try:
			status_code = response.status_code
		except:
			status_code = None

		if status_code == 200:
			status = response.text.splitlines()
			for line in status:
				stats_line = re.match('\s*(\d+)\s+(\d+)\s+(\d+)\s*$', line)
				if stats_line:
					result = {}
					for i, key in enumerate(whitelist):
						key = self.normalize(key)
						value = int(stats_line.group(i+1))
						result[key] = value
						
					if len(result) > 0:
						requests_per_second = 0
						total_requests = result.get('requests', 0)
						handled = result.get('handled', 0)
			
						if total_requests > 0 and handled > 0:
							requests_per_second = total_requests/handled

							self.gauge('requests.per.second', requests_per_second)

				else:
					for (key,val) in re.findall('(\w+):\s*(\d+)', line):
						key = self.normalize(key, prefix='connections')
						self.gauge(key, int(val))


		# Get detailed stats with goaccess
		configfile = tempfile.NamedTemporaryFile()
		log_content = """
date_format %d/%b/%Y
log_format %h %^[%d:%t %^] "%r" %s %b
time_format  %H:%M:%S
"""
		configfile.write(log_content)
		configfile.flush()

		command = ["goaccess", "-f", log_file, "-p", configfile.name, "-o", "json"]

		server_data = subprocess.Popen(command, stdout=subprocess.PIPE if format else None)
		out, err = server_data.communicate()

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

		