FROM phusion/baseimage:latest
MAINTAINER Martin Rusev

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv AD53961F

RUN echo 'deb http://bg.archive.ubuntu.com/ubuntu trusty main universe' > /etc/apt/sources.list && \
    echo 'deb http://bg.archive.ubuntu.com/ubuntu trusty-updates main restricted' >> /etc/apt/sources.list && \
    echo 'deb http://bg.archive.ubuntu.com/ubuntu trusty-security main' >> /etc/apt/sources.list

RUN echo 'deb http://packages.amon.cx/repo amon contrib' >> /etc/apt/sources.list
RUN apt-get update

RUN apt-get install -y --force-yes amon-agent libpq-dev postgresql


RUN /etc/init.d/amon-agent status

ADD hosts /etc/amonagent/hosts
ADD postgres/postgres.yml /etc/amonagent/plugins/postgres/postgres.yml
ADD postgres/postgres.conf.example /etc/amonagent/plugins/postgres/postgres.conf.example


RUN apt-get install software-properties-common
RUN apt-add-repository ppa:ansible/ansible
RUN apt-get update
RUN apt-get install ansible -y --force-yes

RUN ansible-playbook /etc/amonagent/plugins/postgres/postgres.yml -i /etc/amonagent/hosts -v

CMD ["/bin/bash"]