# docker image creation for slimta/debian
FROM debian:latest
MAINTAINER David G.R.C. Furminieux

# configure which ports will be exposed
EXPOSE 25
EXPOSE 587


# update and upgrade the system!
RUN apt-get update && apt-get upgrade -y

# install dependencies
# RUN apt-get install -y apt-utils
RUN apt-get install -y \
    git \
    python-pip \
    python-setuptools-git \
    python-redis \
    libpython-dev \
    supervisor \
    jed
    
RUN pip install -e \
    git+https://github.com/abusix/python-slimta.git@develop#egg=slimta


# add supervisor configs
ADD /extras/docker/supervisor.conf /etc/supervisor/conf.d/slimta.conf

CMD ["/usr/bin/supervisord","-n", "-c","/etc/supervisor/supervisord.conf"]
