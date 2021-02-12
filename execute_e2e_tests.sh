#!/usr/bin/env bash
docker-compose -f docker-compose.test.yml run sut &&
docker-compose -f docker-compose.test.yml down

