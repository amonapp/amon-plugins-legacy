Amon Plugins Library
=====================

[Amon](https://amon.cx) is a hosted monitoring solution. Amon uses open-source plugins (written in Python)
to monitor a wide variety of application metrics.

Each folder in this repository represents one Amon plugin.


How to Install a plugin on your server
---------------------------------

First you need to make sure that the amonagent is already installed and running. The required version is 0.8+

	$ /etc/init.d/amon-agent status


The plugins for Amon are in a git repository located in `/etc/amonagent/plugins`
To enable a plugin you have to do the following. I am going to use the Apache plugin as an example:
	
	$ cp /etc/amonagent/plugins/apache/apache.example.conf /etc/amonagent/plugins-enabled/apache.conf
	$ python install /etc/amonagent/plugins/apache/requirements.txt
	$ /etc/init.d/amon-agent plugins
	

How to Make your own Amon plugin
---------------------------------

Anyone can create a Amon plugin. Get started by:

1. looking at the examples in this Repository
2. reading the development guide at https://amon.cx/docs/plugins/custom-plugin

When you have something working you'd like to share, drop us a note at <martin@amon.cx>.

Or, send us a pull request here on github. Also don't hesitate to contact us before or during
plugin development if you need guidance.