FROM pablodiegoss/jandig:requirements

RUN mkdir -p /src/ARte

COPY ./src/ARte /src/ARte

COPY ./tasks.py /tasks.py
ENTRYPOINT ["inv"]