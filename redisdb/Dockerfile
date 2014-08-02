FROM phusion/baseimage:latest
MAINTAINER Martin Rusev

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv AD53961F

RUN echo 'deb http://bg.archive.ubuntu.com/ubuntu trusty main universe' > /etc/apt/sources.list && \
    echo 'deb http://bg.archive.ubuntu.com/ubuntu trusty-updates main restricted' >> /etc/apt/sources.list && \
    echo 'deb http://bg.archive.ubuntu.com/ubuntu trusty-security main' >> /etc/apt/sources.list



RUN echo 'deb http://packages.amon.cx/repo amon contrib' >> /etc/apt/sources.list
RUN apt-get update

RUN apt-get install -y --force-yes python python-dev

RUN apt-get install -y --force-yes amon-agent redis-server


RUN /etc/init.d/amon-agent status

ADD hosts /etc/amonagent/hosts
ADD redisdb/redisdb.yml /etc/amonagent/plugins/redisdb/redisdb.yml


RUN pip install ansible
RUN ansible-playbook /etc/amonagent/plugins/redisdb/redisdb.yml -i /etc/amonagent/hosts -v

CMD ["/bin/bash"]