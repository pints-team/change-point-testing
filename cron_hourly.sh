#!/usr/bin/env bash

# Run next test and update the report.

git pull
./funk run --next --plot -r 3
./funk report
./funk commit
