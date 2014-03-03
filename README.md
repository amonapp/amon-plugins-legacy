Amon Plugins Library
=====================

[Amon](https://amon.cx) is a hosted monitoring solution. Amon uses open-source plugins (written in Python)
to monitor a wide variety of application metrics.

Each folder in this repository represents one Amon plugin.


How to Install a plugin on your server
---------------------------------

First you need to make sure that the amonagent is already installed and running. 

	$ /etc/init.d/amon-agent status

If you have the agent installed, you can install any plugin in this repository by running the following commmand:

	$ curl https://amon.cx/install-plugin/foldername | bash


For example if you want to install the apache plugin: [https://github.com/amonapp/amon-plugins/tree/master/apache](https://github.com/amonapp/amon-plugins/tree/master/apache)

	$ curl https://amon.cx/install-plugin/apache | bash
	

How to Make your own Amon plugin
---------------------------------

Anyone can create a Amon plugin. Get started by:

1. looking at the examples in this Repository
2. reading the development guide at https://amon.cx/docs/plugins/custom-plugin

When you have something working you'd like to share, drop us a note at <martin@amon.cx>.

Or, send us a pull request here on github. Also don't hesitate to contact us before or during
plugin development if you need guidance.