#!/bin/bash

CURRENT_DIR=$(pwd)
docker run -it -v "$CURRENT_DIR":/work --rm -p 8080:8080 pybotters:310 jupyter-lab --port=8080 --ip=0.0.0.0 --allow-root --no-browser
