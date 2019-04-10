FROM jandigarte/requirements:latest

RUN mkdir -p /src/ARte

COPY ./src/ARte /src/ARte

COPY ./tasks.py /tasks.py

RUN find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

ENTRYPOINT ["inv"]