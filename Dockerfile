FROM python:3.8.2

COPY sources.list /etc/apt/
RUN apt-get update && \
    apt-get install -y vim && \
    rm -rf /var/lib/apt/lists/*

ENV WORK_PATH /usr/src/app/
WORKDIR $WORK_PATH
COPY . .

COPY pip.conf /root/.pip/
RUN pip3 install -r $WORK_PATH/requirements.txt

EXPOSE 8000
ENTRYPOINT ["python3"]
CMD ["manage.py", "runserver", "0:8000"]
