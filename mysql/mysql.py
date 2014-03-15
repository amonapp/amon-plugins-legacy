try:
	import MySQLdb
except ImportError:
	raise Exception("Cannot import MySQLdb module.")

from amonagent.plugin import AmonPlugin


class MySQLPLugin(AmonPlugin):

	VERSION = '1.0'

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


	def _connect(self):
		host = self.config.get('host', 'localhost')
		port = self.config.get('port', 3306)
		user = self.config.get('user')
		password = self.config.get('password')

		socket = self.config.get('socket')


		if socket:
			self.connection = MySQLdb.connect(unix_socket=mysql_sock, user=user, passwd=password)
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
		

		cursor.close()
		del cursor