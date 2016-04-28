# docker image creation for slimta/debian
FROM debian:latest
MAINTAINER David G.R.C. Furminieux

# update and upgrade the system!
RUN apt-get update && apt-get upgrade -y

# install dependencies
# RUN apt-get install -y apt-utils
RUN apt-get install -y \
    git \
    python-pip \
    python-setuptools-git \
    python-redis \
    libpython-dev
    
RUN pip install -e \
    git+https://github.com/abusix/python-slimta.git@develop#egg=slimta
    
CMD ["/bin/bash"]
