FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
    python-minimal \
    python-pip \
    libmysqlclient-dev

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

WORKDIR /app

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
