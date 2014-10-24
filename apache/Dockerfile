FROM amonbase:latest

RUN apt-get install -y --force-yes amon-agent apache2


RUN /etc/init.d/amon-agent status

ADD hosts /etc/amonagent/hosts
ADD apache/apache.yml /etc/amonagent/plugins/apache/apache.yml
ADD apache/apache.conf.example /etc/amonagent/plugins/apache/apache.conf.example
ADD apache/status_template /etc/amonagent/plugins/apache/status_template

RUN ansible-playbook /etc/amonagent/plugins/apache/apache.yml -i /etc/amonagent/hosts -v

CMD ["/bin/bash"]