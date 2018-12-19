FROM python:3.6.5

WORKDIR /app

COPY requirements.txt /

RUN pip install -r /requirements.txt

COPY /ARte /app/

COPY runserver.sh /
CMD ["/runserver.sh"]