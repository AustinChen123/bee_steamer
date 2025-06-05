FROM python:3.9-slim

ENV PYTHONPATH=/app
WORKDIR /app
COPY pyproject.toml ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install

COPY . /app
RUN apt-get update && apt-get install -y ffmpeg

CMD ["poetry", "run", "python", "app/bee_server.py"]
