FROM pablodiegoss/requirements:latest

WORKDIR /app

COPY /ARte /app/
COPY ./tasks.py /tasks.py

ENTRYPOINT ["inv"]