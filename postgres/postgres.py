try:
	import psycopg2
except ImportError:
	raise ImportError("psycopg2 library cannot be imported. Please check the installation instruction at https://github.com/amonapp/amon-plugins/tree/master/postgres.")

from amonagent.modules.plugins import AmonPlugin


class PostgresPlugin(AmonPlugin):


	VERSION = '1.0'

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
		"tup_updated": 'rows.updated',
		"tup_deleted": 'rows.deleted'

	}

	DESCRIPTORS =  [('datname', 'db') ],

	
	DATABASE_STATS_QUERY =  """
	SELECT datname,
		   %s
	  FROM pg_stat_database
	 WHERE datname not ilike 'template%%'
	   AND datname not ilike 'postgres'
"""

		
	SLOW_QUERIES = """
		SELECT
		calls,
		round(total_time :: NUMERIC, 1) AS total,
		round(
			(total_time / calls) :: NUMERIC,
			3
		) AS per_call,
		regexp_replace(query, '[ \t\n]+', ' ', 'g') AS query
	FROM
		pg_stat_statements
	WHERE
		calls > % s
	ORDER BY
		total_time / calls DESC
	LIMIT 15;
"""

	SLOW_QUERIES_ROWS = ['calls','total','per_call','query']

	MISSING_INDEXES_QUERY = """
	SELECT
		  relname AS table,
		  CASE idx_scan
			WHEN 0 THEN 'Insufficient data'
			ELSE (100 * idx_scan / (seq_scan + idx_scan))::text
		  END percent_of_times_index_used,
		  n_live_tup rows_in_table
		FROM
		  pg_stat_user_tables
		WHERE
		  idx_scan > 0
		  AND (100 * idx_scan / (seq_scan + idx_scan)) < 95
		  AND n_live_tup >= 10000
		ORDER BY
		  n_live_tup DESC,
		  relname ASC
"""
	MISSING_INDEXES_ROWS = ['table', 'percent_of_times_index_used', 'rows_in_table']


	TABLES_SIZE_QUERY = """
		SELECT
			C .relname AS NAME,
			CASE
		WHEN C .relkind = 'r' THEN
			'table'
		ELSE
			'index'
		END AS TYPE,
		 pg_table_size(C .oid) AS SIZE
		FROM
			pg_class C
		LEFT JOIN pg_namespace n ON (n.oid = C .relnamespace)
		WHERE
			n.nspname NOT IN (
				'pg_catalog',
				'information_schema'
			)
		AND n.nspname !~ '^pg_toast'
		AND C .relkind IN ('r', 'i')
		ORDER BY
			pg_table_size (C .oid) DESC,
			NAME ASC
"""

	TABLES_SIZE_ROWS = ['name','type','size']

	INDEX_CACHE_HIT_RATE = """
			-- Index hit rate
		WITH idx_hit_rate as (
		SELECT 
		  relname as table_name, 
		  n_live_tup,
		  round(100.0 * idx_scan / (seq_scan + idx_scan),2) as idx_hit_rate
		FROM pg_stat_user_tables
		ORDER BY n_live_tup DESC
		),
		 
		-- Cache hit rate
		cache_hit_rate as (
		SELECT
		 relname as table_name,
		 heap_blks_read + heap_blks_hit as reads,
		 round(100.0 * sum (heap_blks_read + heap_blks_hit) over (ORDER BY heap_blks_read + heap_blks_hit DESC) / 
		 	sum(heap_blks_read + heap_blks_hit) over (),4) as cumulative_pct_reads,
		 round(100.0 * heap_blks_hit / (heap_blks_hit + heap_blks_read),2) as cache_hit_rate
		FROM  pg_statio_user_tables
		WHERE heap_blks_hit + heap_blks_read > 0
		ORDER BY 2 DESC
		)
		 
		SELECT 
		  idx_hit_rate.table_name,
		  idx_hit_rate.n_live_tup as size,
		  cache_hit_rate.reads,
		cache_hit_rate.cumulative_pct_reads,

		  idx_hit_rate.idx_hit_rate as index_hit_rate,
		  cache_hit_rate.cache_hit_rate
		FROM idx_hit_rate, cache_hit_rate
		WHERE idx_hit_rate.table_name = cache_hit_rate.table_name
		  AND cumulative_pct_reads < 100.0
		ORDER BY reads DESC;
"""

	def _get_connection(self):
		
			
		host = self.config.get('host', 'localhost')
		port = self.config.get('port', 5432)
		user = self.config.get('user')
		password = self.config.get('password')

		# Used in collect
		self.database = self.config.get("database")


		self.connection = psycopg2.connect(host=host, user=user, password=password, database=self.database)

		
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
		
		query = self.DATABASE_STATS_QUERY % (", ".join(cols))
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
		


		cursor.execute("SELECT version();")
		result = cursor.fetchone()

		cursor.execute("SELECT pg_database_size(current_database())")
		result = cursor.fetchone()
		
		try:
			db_size = result[0]
		except:
			db_size = False
		if db_size: 
			self.gauge('dbsize', db_size)

		# SLOW QUERIES -- BEGIN 
		query = self.SLOW_QUERIES % 10
		self.log.debug("Running query: %s" % query)
		

		try:
			cursor.execute(query)
			slow_queries_cursor = cursor.fetchall()
		except:
			slow_queries_cursor = False # Can't  fetch

		
		if slow_queries_cursor:
			slow_queries_result = {
				'headers': self.SLOW_QUERIES_ROWS, 
				'data': []
			}
			for r in slow_queries_cursor:
				normalized_row = map(self.normalize_row_value, r)
				slow_queries_result['data'].append(normalized_row)
				
			self.result['slow_queries'] = slow_queries_result
		
		# SLOW QUERIES -- END	


		# TABLES SIZE -- BEGIN

		try:
			cursor.execute(self.TABLES_SIZE_QUERY)
			tables_sizes_cursor = cursor.fetchall()
		except:
			tables_sizes_cursor = False # Can't  fetch

		if tables_sizes_cursor:
			tables_sizes_result = {
				'headers': self.TABLES_SIZE_ROWS, 
				'data': []
			}
			for r in tables_sizes_cursor:
				normalized_row = map(self.normalize_row_value, r)
				tables_sizes_result['data'].append(normalized_row)
				
			self.result['tables_size'] = tables_sizes_result
		# TABLES SIZE -- END

		if result:
			self.version(psycopg2=psycopg2.__version__,
				postgres=result,
				plugin=self.VERSION)

		cursor.close()
		self.connection.close()