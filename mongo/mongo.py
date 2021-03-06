import types

try:
	import pymongo		
except ImportError:
	raise Exception('Python PyMongo Module can not be imported. Please check the installation instruction on https://github.com/amonapp/amon-plugins/tree/master/mongo')

from pymongo import uri_parser

from amonagent.modules.plugins import AmonPlugin

class MongoPlugin(AmonPlugin):
	
	VERSION = '1.0'


	GAUGES = [
		"indexCounters.btree.missRatio",
		"globalLock.ratio",
		"connections.current",
		"connections.available",
		"mem.resident",
		"mem.virtual",
		"mem.mapped",
		"cursors.totalOpen",
		"cursors.timedOut",

		"stats.indexes",
		"stats.indexSize",
		"stats.objects",
		"stats.dataSize",
		"stats.storageSize",

		"replSet.health",
		"replSet.state",
		"replSet.replicationLag",

	]

	COUNTERS = [
		"indexCounters.btree.accesses",
		"indexCounters.btree.hits",
		"indexCounters.btree.misses",
		"opcounters.insert",
		"opcounters.query",
		"opcounters.update",
		"opcounters.delete",
		"opcounters.getmore",
		"opcounters.command",
		"asserts.regular",
		"asserts.warning",
		"asserts.msg",
		"asserts.user",
		"asserts.rollovers",
		"metrics.document.deleted",
		"metrics.document.inserted",
		"metrics.document.returned",
		"metrics.document.updated",
		"metrics.getLastError.wtime.num",
		"metrics.getLastError.wtime.totalMillis",
		"metrics.getLastError.wtimeouts",
		"metrics.operation.fastmod",
		"metrics.operation.idhack",
		"metrics.operation.scanAndOrder",
		"metrics.queryExecutor.scanned",
		"metrics.record.moves",
	]

	METRICS = GAUGES + COUNTERS

	DEFAULT_TIMEOUT = 10

	SLOW_QUERIES_ROWS = ['millis', 'ns', 'op', 'query', 'ts']
	COLLECTION_ROWS = ['count','ns','avgObjSize', 'totalIndexSize', 'indexSizes', 'size']

	def get_versions(self):
		mongodb_version = self.conn.server_info()['version']


		self.version(mongo=mongodb_version, plugin=self.VERSION, pymongo=pymongo.version)


	def collect(self):
		server =  self.config.get('server')

		if server == None:
			self.error("Missing 'server' in mongo config")
			return
		
		
		parsed = uri_parser.parse_uri(server)

		username = parsed.get('username')
		password = parsed.get('password')
		db_name = parsed.get('database')
		slowms = self.config.get('slowms', 25)

		if not db_name:
			self.log.info('No MongoDB database found in URI. Defaulting to admin.')
			db_name = 'admin'

		do_auth = True
		if username is None or password is None:
			self.log.debug("Mongo: cannot extract username and password from config %s" % server)
			
			do_auth = False

		try:
			self.conn = pymongo.Connection(server, network_timeout=self.DEFAULT_TIMEOUT)
		except Exception, e:
			self.error(e)
			return

		if self.conn == None:
			return
		
		db = self.conn[db_name]

		if do_auth:
			if not db.authenticate(username, password):
				self.error("Mongo: cannot connect with config %s" % server)

		status = db["$cmd"].find_one({"serverStatus": 1})
		status['stats'] = db.command('dbstats')

		# Handle replica data, if any
		# See http://www.mongodb.org/display/DOCS/Replica+Set+Commands#ReplicaSetCommands-replSetGetStatus
		try:
			data = {}

			replSet = db.command('replSetGetStatus')
			if replSet:
				primary = None
				current = None

				# find nodes: master and current node (ourself)
				for member in replSet.get('members'):
					if member.get('self'):
						current = member
					if int(member.get('state')) == 1:
						primary = member

				# If we have both we can compute a lag time
				if current is not None and primary is not None:
					lag = current['optimeDate'] - primary['optimeDate']
					# Python 2.7 has this built in, python < 2.7 don't...
					if hasattr(lag,'total_seconds'):
						data['replicationLag'] = lag.total_seconds()
					else:
						data['replicationLag'] = (lag.microseconds + \
			(lag.seconds + lag.days * 24 * 3600) * 10**6) / 10.0**6

				if current is not None:
					data['health'] = current['health']

				data['state'] = replSet['myState']
				status['replSet'] = data
		except Exception, e:
			if "OperationFailure" in repr(e) and "replSetGetStatus" in str(e):
				pass
			else:
				raise e

		# If these keys exist, remove them for now as they cannot be serialized
		try:
			status['backgroundFlushing'].pop('last_finished')
		except KeyError:
			pass
		try:
			status.pop('localTime')
		except KeyError:
			pass

		# Go through the metrics and save the values
		for m in self.METRICS:

			# each metric is of the form: x.y.z with z optional
			# and can be found at status[x][y][z]

			value = status
			try:
				for c in m.split("."):
					value = value[c]
			except KeyError:
				continue

			# value is now status[x][y][z]
			assert type(value) in (types.IntType, types.LongType, types.FloatType)

			# Check if metric is a gauge or rate
			if m in self.GAUGES:
				self.gauge(m, value)
				

			if m in self.COUNTERS:
				self.counter(m, value)


		# Performance 
		params = {"millis": { "$gt" : slowms }}
		performance = db['system.profile']\
		.find(params)\
		.sort("ts", pymongo.DESCENDING)\
		.limit(10)

		if performance.clone().count() > 0:
			
			slow_queries_result = {
				'headers': self.SLOW_QUERIES_ROWS, 
				'data': []
			}
			
			for r in performance: 
				row_list = [r.get(key) for key in self.SLOW_QUERIES_ROWS]
				normalized_row = map(self.normalize_row_value, row_list)

				slow_queries_result['data'].append(normalized_row)

			self.result['slow_queries'] = slow_queries_result

		# Collection sizes
		collections = db.collection_names(include_system_collections=False)
		if len(collections) > 0:

			collection_size_results = {
				'headers': self.COLLECTION_ROWS, 
				'data': []
			}


			for col in collections:
				collection_stats = db.command("collstats", col)
				col_list = [collection_stats.get(key) for key in self.COLLECTION_ROWS]
				normalized_row = map(self.normalize_row_value, col_list)

				collection_size_results['data'].append(normalized_row)

			self.result['tables_size'] = collection_size_results

		self.get_versions()
		self.conn.close()