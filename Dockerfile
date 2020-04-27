FROM python:3.8.2

# 配置镜像，并安装 Linux 软件
COPY sources.list /etc/apt/
RUN apt-get update && \
    apt-get install -y vim && \
    rm -rf /var/lib/apt/lists/*

# 设置工作路径，并把上下文拷贝到工作路径
ENV WORK_PATH /usr/src/app/
WORKDIR $WORK_PATH
COPY . .

# 配置 pip 镜像，并安装 Python 包
COPY pip.conf /root/.pip/
RUN pip3 install -r $WORK_PATH/requirements.txt

# 开放端口，并设置启动程序
EXPOSE 8000
ENTRYPOINT ["python3"]
CMD ["manage.py", "runserver", "0:8000"]
