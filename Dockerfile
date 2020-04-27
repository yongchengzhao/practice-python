FROM python:3.8.2

COPY sources.list /etc/apt/
RUN apt-get update && \
    apt-get install -y vim && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app/
COPY . .

COPY pip.conf /root/.pip/
RUN pip3 install -r requirements.txt

# ENTRYPOINT ["pipdeptree"]
CMD ["python3 -V"]
