#!/usr/bin/env bash

# Commit a change to the azure-ci branch of this repo on pints@skip to trigger the next test.
# This will become unnecessary once azure-pipelines yaml config supports scheduled triggers.
# This script is called from a crontab on pints@skip and runs from a local version of this repo.

# Get next test name
NEXT="$(./funk list --next)"

git checkout azure-ci
git pull
date >> poke-azure.log
git add poke-azure.log
git commit -m "Preparing to run ${NEXT}"
git push
