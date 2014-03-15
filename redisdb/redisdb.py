import redis

from amonagent.plugin import AmonPlugin

class RedisPlugin(AmonPlugin):

	VERSION = '1.0'

	GAUGES = {
		# Append-only metrics
		'aof_last_rewrite_time_sec':    'aof.last_rewrite_time',
		'aof_rewrite_in_progress':      'aof.rewrite',
		'aof_current_size':             'aof.size',
		'aof_buffer_length':            'aof.buffer_length',

		# Network
		'connected_clients':            'net.clients',
		'connected_slaves':             'net.slaves',
		'rejected_connections':         'net.rejected',

		# clients
		'blocked_clients':              'clients.blocked',
		'client_biggest_input_buf':     'clients.biggest_input_buf',
		'client_longest_output_list':   'clients.longest_output_list',

		# Keys
		'evicted_keys':                 'keys.evicted',
		'expired_keys':                 'keys.expired',

		# stats
		'keyspace_hits':                'stats.keyspace_hits',
		'keyspace_misses':              'stats.keyspace_misses',
		'latest_fork_usec':             'perf.latest_fork_usec',

		# pubsub
		'pubsub_channels':              'pubsub.channels',
		'pubsub_patterns':              'pubsub.patterns',

		# rdb
		'rdb_bgsave_in_progress':       'rdb.bgsave',
		'rdb_changes_since_last_save':  'rdb.changes_since_last',
		'rdb_last_bgsave_time_sec':     'rdb.last_bgsave_time',

		# memory
		'mem_fragmentation_ratio':      'mem.fragmentation_ratio',
		'used_memory':                  'mem.used',
		'used_memory_lua':              'mem.lua',
		'used_memory_peak':             'mem.peak',
		'used_memory_rss':              'mem.rss',

		# replication
		'master_last_io_seconds_ago':   'replication.last_io_seconds_ago',
		'master_sync_in_progress':      'replication.sync',
		'master_sync_left_bytes':       'replication.sync_left_bytes',

	}


	def collect(self):
		host = self.config.get('host', 'localhost')
		port = self.config.get('port', 6379)
		password = self.config.get('password')
		db = self.config.get('db', 0)

		self.conn = redis.StrictRedis(host=host, port=port, db=db, password=password)


		try:
			info = self.conn.info()
		except ValueError, e:
			raise Exception("""Unable to run the info command. This is probably an issue with your version of the python-redis library.
				Minimum required version: 2.4.11
				Your current version: %s 
				Please upgrade to a newer version by running sudo easy_install redis""" % redis.__version__)


		for k in self.GAUGES:
			if k in info:
				self.gauge(self.GAUGES[k], info[k])


		redis_version =  info.get('redis_version')
		self.version(plugin=self.VERSION, redispy=redis.__version__,
			redis=redis_version)