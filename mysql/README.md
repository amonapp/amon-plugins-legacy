# MySQL Plugin


Monitors MySQL. Parses the output from the `SHOW STATUS` command https://dev.mysql.com/doc/refman/5.0/en/show-status.html.


## Installing

The MySQL plugin requires Amon agent version 0.8+. To check your agent version: `$ /etc/init.d/amon-agent status`.

To install the plugin:


    $ cp /etc/amonagent/plugins/mysql/mysql.conf.example /etc/amonagent/plugins-enabled/mysql.conf
    $ sudo pip install -r /etc/amonagent/plugins/mysql/requirements.txt

## Configuration

* **host** -  Your MySQL host, defaults to localhost
* **port** - Your MySQL port, defaults to 5432
* **password** - Your MySQL password, defined when creating the amon user
* **user** - Your MySQL user, defaults to amon

* **socket** - (Optional), If you connect to your MySQL instance through an Unix socket.


You have to create an Amon user with replication rights:

	$ sudo mysql -e "create user 'amon'@'localhost' identified by 'desired-password';"
	$ sudo mysql -e "grant replication client on *.* to 'amon'@'localhost';"

## Testing

To test the installation, run the following:


    $ /etc/init.d/amon-agent plugins 
    
    
If everything works as expected, restart the agent and in a couple of minutes you will see the metrics in Amon 
