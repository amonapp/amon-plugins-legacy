import requests
import json

from amonagent.settings import settings

class AmonElasticsearchPlugin(object):

	def __init__(self):
		elasticsearch_config = settings.PLUGINS.get("elasticsearch", None)
		status_url = "http://127.0.0.1:9200/_status" # Provide default
		if elasticsearch_config:
			status_url = elasticsearch_config.get("status_url", None)

		self.url = status_url

	def build_report(self):

		status_dict = {}
		response = requests.get(self.url)

		if response.status_code == 200:		
			status_dict = json.loads(response.text)
		
		return status_dict
		
plugin = AmonElasticsearchPlugin()