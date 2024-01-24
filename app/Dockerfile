FROM python:3.10.12-slim-bookworm
RUN mkdir /bot && chmod 777 /bot
WORKDIR /bot
ENV DEBIAN_FRONTEND=noninteractive
RUN apt -qq update && apt-get -y upgrade && apt -qq install -y python3-dev
COPY . .
RUN pip3 install -r requirements.txt
CMD python main.py