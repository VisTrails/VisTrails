FROM debian:8
MAINTAINER Remi Rampin <remirampin@gmail.com>

# http.debian.net seems to contain bad mirrors, use something else
RUN \
  sh -c 'echo "deb http://ftp.us.debian.org/debian jessie main" > /etc/apt/sources.list' && \
  sh -c 'echo "deb http://ftp.us.debian.org/debian jessie-updates main" >> /etc/apt/sources.list' && \
  sh -c 'echo "deb http://security.debian.org jessie/updates main" >> /etc/apt/sources.list'
# Install VisTrails deps from distrib
RUN \
  apt-get update && \
  apt-get install -y python python-dateutil python-dev python-docutils \
    python-mako python-matplotlib python-mysqldb python-numpy python-paramiko \
    python-pip python-scipy python-setuptools python-sphinx python-sqlalchemy \
    python-suds python-tz python-unittest2 python-virtualenv \
    python-xlrd python-xlwt
RUN \
  apt-get install -y python-qt4 python-qt4-gl python-qt4-sql python-vtk \
    imagemagick graphviz xvfb
# Install IPython deps. python-tornado is too old, so we'll get it from pip
RUN \
  apt-get install -y python-zmq

# Makes virtualenv
RUN \
  cd /root && \
  virtualenv --system-site-packages venv

# These are the only files we need, but `docker build` will still upload
# everything; .dockerignore format is very broken
ADD vistrails /root/vistrails
ADD requirements.txt MANIFEST.in setup.py /root/

# Install missing requirements from pip
RUN \
  cd /root && \
  . venv/bin/activate && \
  pip install -r requirements.txt jupyter

# Warning: using 'setup.py develop' will make setuptools add dist-packages to
# sys.path, which will break everything; don't do it

ADD examples /root/examples

EXPOSE 8888

# VTK needs GL rendering
RUN apt-get install -y libosmesa6 libglapi-mesa libgl1-mesa-swx11 libgl1-mesa-dri

ENTRYPOINT \
  cd /root && \
  . venv/bin/activate && \
  xvfb-run -s "-screen 0 640x480x24" jupyter notebook --ip=0.0.0.0 --port=8888
