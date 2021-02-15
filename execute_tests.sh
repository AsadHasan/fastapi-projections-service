#!/usr/bin/env bash
docker-compose --file docker-compose.test.yml build &&
docker-compose -f docker-compose.test.yml run sut &&
docker-compose -f docker-compose.test.yml down
