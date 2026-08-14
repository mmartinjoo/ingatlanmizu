FROM python:3.12
WORKDIR /usr/src/app
RUN pip install uv
COPY uv.lock uv.lock
COPY pyproject.toml pyproject.toml
RUN uv sync
COPY . .