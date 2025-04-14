FROM python:3.12

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
libpq-dev \
libjpeg-dev \
libcairo2 \
gcc \
&& rm -rf /var/lib/apt/lists/*

RUN mkdir -p /code

WORKDIR /code

EXPOSE 8000

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

COPY ./src /code
 
COPY ./boot/docker-run.sh /opt/run.sh

RUN chmod +x /opt/run.sh

CMD ["/opt/run.sh"]

