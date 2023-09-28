#!/bin/sh

set -e

cd /home/luko/bf2-www
docker-compose start certbot
sleep 30s
docker-compose exec nginx nginx -s reload