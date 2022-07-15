#!/bin/bash

# until next 10:00
wait-morning() {
  while [ "$(date "+%H:%M")" != "10:00" ]; do
    sleep 10
  done
}

post() {
  USERNAME=$1
  ICON=$2
  COLOR=$3
  shift 3
  TEXT=$(echo "$@" | tr '\n' '\t' | tr -d '"' | sed 's/[\t ]*$//g; s/\t/\\n/g')
  PAYLOAD=$(mktemp)
  cat <<EOM >$PAYLOAD
{
  "username": "${USERNAME}",
  "icon_emoji": ":${ICON}:",
  "channel": "#timeline",
  "fallback": "Hi",
  "color": "${COLOR}",
  "fields": [
    {
      "title": "",
      "value": "${TEXT}",
      "short": false
    }
  ]
}
EOM
  cat $PAYLOAD
  curl "$URL" --data @$PAYLOAD
  rm $PAYLOAD
}

post-tenki() {
  post tenki partly_sunny "#ff6060" "$(tenki)"
  post tenki partly_sunny "#ff6060" "$(tenki -f)"
}

post-anime() {
  post anical tv "#44aa88" "$(anical)"
}

work() {
  post-tenki
  # post-anime
}

work
while :; do
  wait-morning
  work
  date
  sleep 3000
done
