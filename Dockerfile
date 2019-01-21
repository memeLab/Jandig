FROM pablodiegoss/jandig:requirements

WORKDIR /app

COPY /ARte /app/
COPY ./tasks.py /tasks.py

ENTRYPOINT ["inv"]