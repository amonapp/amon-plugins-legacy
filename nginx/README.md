# Nginx Plugin


Monitors Nginx. Sends to Amon the the following metrics:  

- Connections - reading, writing, waiting
- Requests per second

## Installing

The Nginx plugin requires Amon agent version 0.8+. To check your agent version: `$ /etc/init.d/amon-agent status`.
You also need to enable the `HttpStubStatusModule` - http://wiki.nginx.org/HttpStubStatusModule in your Nginx configuration files

To install the plugin:


    $ cp /etc/amonagent/plugins/nginx/nginx.conf.example /etc/amonagent/plugins-enabled/nginx.conf


## Configuration

* **status_url** - Your Nginx status url.


## Testing

To test the installation, run the following:


    $ /etc/init.d/amon-agent plugins 
    
    
If everything works as expected, restart the agent and in a couple of minutes you will see the metrics in Amon 
