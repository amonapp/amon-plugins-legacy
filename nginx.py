from __future__ import division
import requests
import math
import re
import shelve
from amonagent.utils import unix_utc_now
from amonagent.settings import settings
from amonagent.log import log

class AmonNginxPlugin(object):

	def __init__(self):
		nginx_config = settings.PLUGINS.get("nginx", None)
		nginx_status_url = "http://127.0.0.1/nginx_status" # Provide default
		if nginx_config:
			nginx_status_url = nginx_config.get("status_url", None)

		self.url = nginx_status_url


	def build_report(self):
		
		try:
			self.db = shelve.open(settings.CACHE)
		except Exception, error:
			log.exception("Can't open cache file")

		response = requests.get(self.url)

		if response.status_code == 200:
			status_dict = {}
			for line in response.text.splitlines():
				data = re.match('\s*(\d+)\s+(\d+)\s+(\d+)\s*$', line)
				if data:
					for key, value in enumerate(('accepts','handled','requests')):
						status_dict[value] = int(data.group(key+1))
				else:
					for (key,val) in re.findall('(\w+):\s*(\d+)', line):
						status_dict[key.lower()] = int(val)

		nginx_last_check = self.db.get("nginx:last_check", None)
		nginx_last_request_value = self.db.get("nginx:last_request_value", None)

		if nginx_last_check and nginx_last_request_value:
			time_difference = unix_utc_now()-nginx_last_check
			request_diff = status_dict["requests"]-nginx_last_request_value
			if request_diff > 0 and time_difference > 0: # Avoid division by zero errors
				requests_per_second = request_diff/time_difference
				status_dict["requests_per_second"] = math.ceil(requests_per_second)

		self.db["nginx:last_check"] = unix_utc_now()
		self.db["nginx:last_request_value"] = status_dict["requests"]

		self.db.close()

		return status_dict


plugin = AmonNginxPlugin()
