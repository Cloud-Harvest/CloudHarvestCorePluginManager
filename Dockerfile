FROM python:3.12-bookworm as python

WORKDIR /src

ENV PIP_ROOT_USER_ACTION=ignore
ENV PIP_CACHE_DIR=/src/pip/cache

COPY . .

RUN pip install setuptools \
    && python -m pip install . \
    && pytest -rP tests/

ENTRYPOINT /bin/bash
