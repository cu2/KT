FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python2-dev \
    python-pip \
    libmysqlclient-dev \
    libjpeg-dev

# Client programs should only need to #include the <mysql.h> header file.
# In particular, <my_config.h> should not be needed, and is no longer installed.
# https://stackoverflow.com/a/69382475
RUN ln -s /usr/include/mysql/mysql.h /usr/include/mysql/my_config.h

COPY requirements.txt /tmp/
RUN python2 -m pip install -r /tmp/requirements.txt

WORKDIR /app

CMD ["python2", "manage.py", "runserver", "0.0.0.0:8000"]
