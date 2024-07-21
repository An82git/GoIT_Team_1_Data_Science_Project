FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

ENV APP_HOME=/project \
    POETRY_VERSION=1.7.1 

ENV PYTHONPATH=${APP_HOME}:$PYTHONPATH

WORKDIR $APP_HOME

COPY . .

RUN apt-get update && apt-get install -y \
    software-properties-common

RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime \
    && apt-get install -y tzdata \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && apt-get install -y python3.11 python3.11-dev python3.11-venv python3-pip \
    && apt-get install -y postgresql-client libpq-dev \
    && apt-get install -y gcc g++ \
    && rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==$POETRY_VERSION"

RUN pip config set global.timeout 1000 && \
    pip config set global.retries 10

RUN pip install nvidia-curand-cu12==10.3.2.106 --timeout=300 --retries=10
RUN pip install nvidia-cufft-cu12==11.0.2.54 --timeout=300 --retries=10
RUN pip install triton==2.3.1 --timeout=300 --retries=10

RUN poetry env use python3.11 && poetry cache clear . --all && poetry install --no-root

CMD \
    sleep 10 && \
    cd ./app && \
    poetry run alembic upgrade head && \
    cd .. && \
    poetry run python ./app/cli.py seed && \
    poetry run python ./app/main.py