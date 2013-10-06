import requests

from amonagent.settings import settings

class AmonMongodbPlugin(object):

	def __init__(self):
		mongodb_config = settings.PLUGINS.get("mongodb", None)
		status_url = "http://127.0.0.1/_status" # Provide default
		if mongodb_config:
			status_url = mongodb_config.get("status_url", None)

		self.url = status_url

	def build_report(self):

		status_dict = {}
		response = requests.get(self.url)

		if response.status_code == 200:
			print 'ok'
		
		return status_dict
		
plugin = AmonMongodbPlugin()