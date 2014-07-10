# Mongo Plugin


Monitors MongoDB parsing the output from the `db.serverStatus()` command. Sends to Amon the the following metrics:  

- Connections - http://docs.mongodb.org/manual/reference/command/serverStatus/#connections
- Opcounters - http://docs.mongodb.org/manual/reference/command/serverStatus/#opcounters
- Cursors - http://docs.mongodb.org/manual/reference/command/serverStatus/#cursors
- IndexCounters - http://docs.mongodb.org/manual/reference/command/serverStatus/#indexcounters
- Asserts - http://docs.mongodb.org/manual/reference/command/serverStatus/#asserts
- Metrics - http://docs.mongodb.org/manual/reference/command/serverStatus/#metrics

## Installing

The Mongo plugin requires Amon agent version 0.8+. To check your agent version: `$ /etc/init.d/amon-agent status`

To install the plugin:

    $ apt-get install python-dev # pymongo requirements on Debian/Ubuntu
    $ yum install python-devel # pymongo requirements on CentOS/Amazon AMI/Fedora
        
    $ cp /etc/amonagent/plugins/mongo/mongo.conf.example /etc/amonagent/plugins-enabled/mongo.conf
    $ sudo pip install -r /etc/amonagent/plugins/mongo/requirements.txt


## Configuration

* **server** - Mongo URI connection string http://docs.mongodb.org/manual/reference/connection-string/.


If you have enabled authentication for your Mongo database, you have to create a read only admin user for Amon:


    $ mongo
    $ use admin
    $ db.auth("admin", "admin-password")
    $ db.addUser("amon", "your-desired-password", true)


## Testing

To test the installation, run the following:


    $ /etc/init.d/amon-agent plugins 
    
    
If everything works as expected, restart the agent and in a couple of minutes you will see the metrics in Amon 
