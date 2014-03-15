
Monitors Redis parsing the output from the `INFO` command - http://redis.io/commands/INFO. Sends to Amon the the following metrics:  


## Installing

The Redis plugin requires Amon agent version 0.8+. To check your agent version: `$ /etc/init.d/amon-agent status`

To install the plugin:


    $ cp /etc/amonagent/plugins/redisdb/redisdb.conf.example /etc/amonagent/plugins-enabled/redisdb.conf
    $ sudo pip install -r /etc/amonagent/plugins/redisdb/requirements.txt


## Configuration

* **host** -  Your Redis host, defaults to localhost
* **port** - Your Redis port, defaults to 6379

* **user** - Your Redis username
* **password** - Your Redis password
* **database** - Optional, defaults to 0.

## Testing

To test the installation, run the following:


    $ /etc/init.d/amon-agent plugins 
    
    
If everything works as expected, restart the agent and in a couple of minutes you will see the metrics in Amon 
