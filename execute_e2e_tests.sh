#!/usr/bin/env bash
docker-compose run e2e_tests &&
docker-compose down
