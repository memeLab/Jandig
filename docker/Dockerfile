FROM pablodiegoss/jandig:requirements

RUN mkdir /ARte

COPY ./src/ARte /ARte/
COPY ./tasks.py /tasks.py
RUN ls
ENTRYPOINT ["inv"]