FROM python:alpine

COPY rootfs /

WORKDIR /ddns
COPY requirements.py .
COPY cloudflare_ddns .
COPY run.py .

CMD python run.py && crond -f