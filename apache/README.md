# Apache Plugin


Monitors Apache, reporting:

- Idle, Busy workers
- Requests per second
- Total accesses/bytes

## Installing

The Apache plugin requires Amon agent version 0.8+. To check your agent version: `$ /etc/init.d/amon-agent status`
You also need to enable `mod_status` in your apache configuration. You can see a tutorial [http://www.cyberciti.biz/faq/apache-server-status/](http://www.cyberciti.biz/faq/apache-server-status/)

To install the plugin:


    $ cp /etc/amonagent/plugins/apache/apache.conf/example /etc/amonagent/plugins-enabled/apache.conf


## Configuration

* **status_url** - Your apache status url.

Example: If you have the following in your apache configuration file `<Location /server-status>`, the url will be
`http://yourserver/server-status?auto`

## Testing

To test the installation, run the following:


    $ /etc/init.d/amon-agent plugins 
    
    
If everything works as expected, restart the agent and in a couple of minutes you will see the metrics in Amon 
