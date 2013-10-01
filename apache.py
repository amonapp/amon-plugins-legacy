import requests

from amonagent.utils import unix_utc_now, slugify
from amonagent.settings import settings
from amonagent.log import log


class AmonApachePlugin(object):

	def __init__(self):
		apache_config = settings.PLUGINS.get("apache", None)
		status_url = "http://127.0.0.1/server-status?auto" # Provide default
		if apache_config:
			status_url = apache_config.get("status_url", None)

		self.url = status_url

	def build_report(self):

		status_dict = {}
		response = requests.get(self.url)

		if response.status_code == 200:		
			lines = response.text.splitlines()
			for line in lines:
				key, value = line.split(":")
				if not key.startswith('Score'):
					status_dict[slugify(key)] = "{0:.2f}".format(float(value))
		
		return status_dict
		
plugin = AmonApachePlugin()
