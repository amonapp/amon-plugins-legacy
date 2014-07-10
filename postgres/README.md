# PostgreSQL Plugin


Monitors PostgreSQL. Parses the output from the `pg_stats_database` query http://www.postgresql.org/docs/9.2/static/monitoring-stats.html#PG-STAT-DATABASE-VIEW


## Installing

The PostgreSQL plugin requires Amon agent version 0.8+. To check your agent version: `$ /etc/init.d/amon-agent status`.

To install the plugin:


    $ cp /etc/amonagent/plugins/postgres/postgres.conf.example /etc/amonagent/plugins-enabled/postgres.conf
    $ sudo pip install -r /etc/amonagent/plugins/postgres/requirements.txt

## Configuration

* **host** -  Your PostgreSQL host, defaults to localhost
* **port** - Your PostgreSQL port, defaults to 5432
* **password** - Your PostgreSQL password, defined when creating the amon user
* **user** - Your PostgreSQL user, defaults to amon
* **database** - The database you want to monitor


Create a read-only amon user with proper access to your PostgreSQL Server. 

	$ psql
	$ create user amon with password 'your-desired-password';
	$ grant SELECT ON pg_stat_database to amon;


## Testing

To test the installation, run the following:


    $ /etc/init.d/amon-agent plugins 
    
    
If everything works as expected, restart the agent and in a couple of minutes you will see the metrics in Amon 
