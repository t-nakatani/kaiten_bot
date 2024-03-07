#!/bin/bash

CURRENT_DIR=$(pwd)
docker run -it -v "$CURRENT_DIR":/work --rm pybotters:310 python3 scripts/main.py
