FROM alpine:3.11

RUN apk add bash curl jq

WORKDIR /
RUN wget https://github.com/cympfh/bin/archive/master.zip && unzip master.zip && rm master.zip
ENV PATH $PATH:/bin-master

WORKDIR /app
COPY . .
CMD bash cron.sh
