from amonagent.plugin import AmonPlugin



class PostgreSqlPlugin(AmonPlugin):
	"""Collects per-database, and optionally per-relation metrics
	"""


	GAUGES = {
		'numbackends': 'connections'
	}

	COUNTERS = {
		"xact_commit": "xact.commits",
		"xact_rollback": "xact.rollbacks",
		"blks_read": 'performance.disk_read',
		"blks_hit": "performance.buffer_hit",
		"tup_returned": 'rows.returned',
		"tup_fetched": 'rows.fetched',
		"tup_inserted": 'rows.inserted',
		"tup_updated": 'row.updated',
		"tup_deleted": 'rows.deleted'

	}

	DESCRIPTORS =  [('datname', 'db') ],

	
	QUERY =  """
SELECT datname,
	   %s
  FROM pg_stat_database
 WHERE datname not ilike 'template%%'
   AND datname not ilike 'postgres'
"""
		

	def _get_connection(self):
		try:
			import psycopg2 as pg
		except ImportError:
			raise ImportError("psycopg2 library cannot be imported. Please check the installation instruction on the Amon Website.")
			
		host = self.config.get('host', 'localhost')
		port = self.config.get('port', 5432)
		user = self.config.get('user')
		password = self.config.get('password')

		# Used in collect
		self.database = self.config.get("database")


		self.connection = pg.connect(host=host, user=user, password=password, database=self.database)

		
		try:
			self.connection.autocommit = True
		except AttributeError:
			# connection.autocommit was added in version 2.4.2
			from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
			self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
		
	
	def collect(self):
		self._get_connection()

		cursor = self.connection.cursor()
		cols = self.GAUGES.keys() + self.COUNTERS.keys()
		
		query = self.QUERY % (", ".join(cols))
		self.log.debug("Running query: %s" % query)
		cursor.execute(query)

		result = cursor.fetchall()

		field_names =[f[0] for f in cursor.description]
		
	 	for row in result:
	 		assert len(row) == len(field_names)


	 		values = dict(zip(field_names, list(row)))
			
	 		# Save the values only for the database defined in the config file 
	 		datname = values.get('datname')
	 
	 		if datname == self.database:
	 			for k,v in values.items():
	 				
	 				if k in self.GAUGES:
	 					key = self.GAUGES[k] 
	 					self.gauge(key, v)
	 
	 				if k in self.COUNTERS:
	 					key = self.COUNTERS[k] 

	 					self.counter(key, v)
		
		cursor.close()
		
