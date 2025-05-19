FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y software-properties-common curl git && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.12 python3.12-venv && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1 && \
    ln -sf /usr/local/bin/pip3 /usr/bin/pip3

WORKDIR /app

COPY requirements.txt ./
RUN if [ -f requirements.txt ]; then pip3 install --upgrade pip && pip3 install -r requirements.txt; fi

COPY . .

CMD [ "bash" ]