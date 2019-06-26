FROM jandigarte/requirements:latest

RUN mkdir -p /ARte
WORKDIR /ARte
COPY docs/ /ARte/docs/
COPY ./src/ARte /ARte/src/ARte/
COPY ./locale/ /ARte/locale/

COPY ./tasks.py /ARte/tasks.py
COPY ./etc/babel.cfg /ARte/etc/babel.cfg
RUN find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
