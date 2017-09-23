#!/bin/bash
virtualenv env -p python3
env/bin/pip install -r requirements/test.txt

env/bin/isort --recursive --check-only --diff --quiet .
