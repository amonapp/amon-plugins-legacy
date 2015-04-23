try:
	import MySQLdb
except ImportError:
	raise Exception("Cannot import MySQLdb module.")

from amonagent.modules.plugins import AmonPlugin


class MySQLPLugin(AmonPlugin):

	VERSION = '1.1'

	GAUGES = {
		'Max_used_connections': 'net.max_connections', 
		'Open_files': 'performance.open_files', 
		'Table_locks_waited': 'performance.table_locks_waited', 
		'Threads_connected': 'performance.threads_connected', 
		'Innodb_current_row_locks': 'innodb.current_row_locks', 
	}


	COUNTERS = {
		'Connections': 'net.connections',
		'Innodb_data_reads': 'innodb.data_reads',
		'Innodb_data_writes': 'innodb.data_writes',
		'Innodb_os_log_fsyncs': 'innodb.os_log_fsyncs',
		'Innodb_row_lock_waits': 'innodb.row_lock_waits',
		'Innodb_row_lock_time': 'innodb.row_lock_time',
		'Innodb_mutex_spin_waits': 'innodb.mutex_spin_waits',
		'Innodb_mutex_spin_rounds': 'innodb.mutex_spin_rounds',
		'Innodb_mutex_os_waits': 'innodb.mutex_os_waits',
		'Slow_queries': 'performance.slow_queries',
		'Questions': 'performance.questions',
		'Queries': 'performance.queries',
		'Com_select': 'performance.com_select',
		'Com_insert': 'performance.com_insert',
		'Com_update': 'performance.com_update',
		'Com_delete': 'performance.com_delete',
		'Com_insert_select': 'performance.com_insert_select',
		'Com_update_multi': 'performance.com_update_multi',
		'Com_delete_multi': 'performance.com_delete_multi',
		'Com_replace_select': 'performance.com_replace_select',
		'Qcache_hits': 'performance.qcache_hits',
		'Created_tmp_tables': 'performance.created_tmp_tables',
		'Created_tmp_disk_tables': 'performance.created_tmp_disk_tables',
		'Created_tmp_files': 'performance.created_tmp_files',
	}

	SLOW_QUERIES = """
		SELECT
	mysql.slow_log.query_time,
	mysql.slow_log.rows_sent,
	mysql.slow_log.rows_examined,
	mysql.slow_log.lock_time,
	mysql.slow_log.db,
	mysql.slow_log.sql_text AS query,
	mysql.slow_log.start_time
FROM
	mysql.slow_log
WHERE
	mysql.slow_log.query_time > 1
ORDER BY
	start_time DESC
LIMIT 30
"""

	SLOW_QUERIES_ROWS = ['query_time','rows_sent',
				'rows_examined','lock_time', 'db',
				'query', 'start_time']


	TABLES_SIZE = """
		SELECT table_name as 'table',
			 table_schema as 'database',
			 table_rows as rows,
			 data_length as size,
			 index_length as indexes,
		CONCAT(ROUND(data_length + index_length )) total,
		ROUND(index_length / data_length, 2) as index_fraction
		FROM   information_schema.TABLES
		WHERE table_schema NOT IN ('information_schema', 'performance_schema', 'mysql')
		ORDER  BY data_length + index_length DESC;
"""

	TABLES_SIZE_ROWS = ['table', 'database', 'rows','size', 'indexes', 'total', 'index_fraction']


	def _connect(self):
		host = self.config.get('host', 'localhost')
		port = self.config.get('port', 3306)
		user = self.config.get('user')
		password = self.config.get('password')

		socket = self.config.get('socket')


		if socket:
			self.connection = MySQLdb.connect(unix_socket=socket, user=user, passwd=password)
		else:
			self.connection = MySQLdb.connect(host=host,port=port,user=user, passwd=password)

		self.log.debug("Connected to MySQL")
	

	def collect(self):
		self._connect()

		cursor = self.connection.cursor()
		cursor.execute("SHOW /*!50002 GLOBAL */ STATUS;")
		results = dict(cursor.fetchall())
		
		for k, v in results.items():

			if k in self.COUNTERS:
				key = self.COUNTERS[k] 
				self.counter(key, v)

			if k in self.GAUGES:
				key = self.GAUGES[k]
				self.gauge(key, v)
		

		cursor.execute("SELECT VERSION();")

		try:
			mysql_version = cursor.fetchone()[0]
		except:
			mysql_version = None
		
		self.version(mysql=mysql_version, 
			plugin=self.VERSION,
			mysqldb=MySQLdb.__version__)

		additional_checks = {
			'slow_queries': 
			{
				'query': self.SLOW_QUERIES,
				'headers': self.SLOW_QUERIES_ROWS
			}, 
			'tables_size': {
				'query': self.TABLES_SIZE,
				'headers': self.TABLES_SIZE_ROWS
			}

		}

		for check, values in additional_checks.items():
			query = values.get('query')
			headers = values.get('headers')

			try:
				cursor.execute(query)
				result_cursor = cursor.fetchall()
			except:
				result_cursor = False # Can't  fetch

			if result_cursor:
				result_dict = {
					'headers': headers, 
					'data': []
				}
				for r in result_cursor:
					normalized_row = map(self.normalize_row_value, r)
					result_dict['data'].append(normalized_row)
					
				self.result[check] = result_dict
		
		cursor.close()
		self.connection.close()
		del cursor