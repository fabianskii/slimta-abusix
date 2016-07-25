# docker image for slimta on alpine
FROM alpine:3.4
MAINTAINER David G.R.C. Furminieux

# configure which ports will be exposed
EXPOSE 25
EXPOSE 587

# define environment variables
ENV REDIS_URL redis://localhost/
ENV REDIS_TARGET mails-topic
ENV REDIS_TARGET_TYPE -t
ENV MTA_PORTS="25 587"

# update and upgrade the system!
RUN apk update && apk upgrade

# install slimta dependencies
RUN apk add python
RUN apk add py-redis
RUN apk add py-hiredis
RUN apk add py-setuptools


# install deployment dependencies
RUN apk add aports-build
RUN apk add python-dev
RUN apk add py-pip

# build the package
RUN pip install \
    git+https://github.com/abusix/python-slimta.git@develop#egg=slimta

# delete deployment dependencies
RUN apk del aports-build
RUN apk del python-dev
RUN apk del py-pip


# add supervisor configs
ADD supervisor.conf /etc/supervisor/conf.d/slimta.conf
    
CMD ["/usr/bin/supervisord","-n", "-c","/etc/supervisor/supervisord.conf"]
