#!/bin/bash

URL="http://0.0.0.0:80/api/ud/"

DATA='{"subtitles": ["Barack Obama was born in Hawaii.", "Donald Trump is the current US president.", "It is a conservative world."], "lang": "en"}'

curl --header "Content-Type: application/json" --request POST --data "$DATA" $URL
