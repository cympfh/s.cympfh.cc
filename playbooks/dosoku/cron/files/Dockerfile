FROM alpine:3.11

# install packages
RUN apk add --update bash curl jq coreutils

# locale
RUN apk --update add tzdata \
 && cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
 && apk del tzdata

# cleaning
RUN rm -rf /var/cache/apk/*

WORKDIR /
ADD https://github.com/cympfh/bin/archive/master.zip master.zip
RUN unzip master.zip && rm master.zip
ENV PATH $PATH:/bin-master

WORKDIR /app
COPY . .
CMD bash cron.sh
