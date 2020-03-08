FROM sunnywalden/centos7-python3.7:latest

# env
ENV ENV_TYPE=prod \
    EXTERNAL=false

RUN mkdir -p /opt/service_static/

# add project to the image
ADD . /opt/service_static/

WORKDIR /opt/service_static/

RUN mkdir -p ~/.pip/ && \
    echo "[global]" > ~/.pip/pip.conf && \
    echo "index-url = http://mirrors.aliyun.com/pypi/simple" >> ~/.pip/pip.conf && \
    echo "[install]" >> ~/.pip/pip.conf && \
    echo "trusted-host = mirrors.aliyun.com" >> ~/.pip/pip.conf && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir requests && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /tmp/*


# RUN server after docker is up
ENTRYPOINT python main/service_healthcheck.py

EXPOSE 8000