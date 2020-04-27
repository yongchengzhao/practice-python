FROM python:3.8.2

COPY source.list /etc/apt/source.list
RUN apt-get update && \
    apt-get install -y vim && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY requirements.txt $WORKDIR/requirements.txt
COPY pip.conf $HOME/.pip/pip.conf
RUN pip3 install -r $WORKDIR/requirements.txt

ENTRYPOINT ["pipdeptree"]
CMD ["-f"]
