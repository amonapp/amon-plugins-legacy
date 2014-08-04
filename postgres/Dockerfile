FROM amonbase:latest
MAINTAINER Martin Rusev

RUN apt-get install -y --force-yes amon-agent postgresql

ADD hosts /etc/amonagent/hosts
ADD postgres/postgres.yml /etc/amonagent/plugins/postgres/postgres.yml
ADD postgres/postgres.conf.example /etc/amonagent/plugins/postgres/postgres.conf.example


RUN ansible-playbook /etc/amonagent/plugins/postgres/postgres.yml -i /etc/amonagent/hosts -v

CMD ["/bin/bash"]