#!/usr/bin/env bash

# Run next test hourly

git pull
./funk run --next --plot -r 3
./funk commit
