############################################################
# Dockerfile to run a Django-based web application
############################################################

# Set the base image to use to Ubuntu
FROM jfloff/alpine-python:latest-slim

# Set the file maintainer (your name - the file's author)
MAINTAINER BP Greyling

# Set env variables used in this Dockerfile (add a unique prefix, such as DOCKYARD)
# Local directory with project source
ENV DOCKYARD_SRC=code
# Directory in container for all project files
ENV DOCKYARD_SRVHOME=/srv
# Directory in container for project source files
ENV DOCKYARD_SRVPROJ=$DOCKYARD_SRVHOME/$DOCKYARD_SRC

RUN pip3 install --upgrade pip

RUN /entrypoint.sh \
	-a git \
	-a mariadb-client-libs \
	-a vim \
	-a musl-dev \
	-a libxml2-dev \
	-a libxslt-dev \
	-a jpeg-dev \
  -a zlib-dev \
	-a supervisor \
	-a py-setuptools \
	-a libffi \
	-a libffi-dev \
	-a openssl \
	-a openssl-dev \
	-p uwsgi \
	-p django \
	-p pymysql \
	-p pillow \
	-p wagtail

# setup all the configfiles
COPY docker/django/supervisor-app.conf	/etc/supervisor/conf.d/
COPY docker/django/uwsgi.ini 						/srv/code/configs/uwsgi.ini

# Create application subdirectories
WORKDIR $DOCKYARD_SRVPROJ/django_app
RUN mkdir media static logs secrets
#read
VOLUME ["$DOCKYARD_SRVPROJ/media/", "$DOCKYARD_SRVPROJ/logs/"]

# Copy application source code to SRCDIR
COPY $DOCKYARD_SRC $DOCKYARD_SRVPROJ

EXPOSE 8081
CMD ["supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisor-app.conf"]
