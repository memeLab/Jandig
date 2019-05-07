#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

# Build base image
docker build ../ -f base.Dockerfile -t jandigarte/requirements:latest

# Check if user wants to publish
if [ $# -eq 1 ]; then
    if [ "$1" = "publish" ]; then
        echo; echo; echo "PUBLISHING IMAGES"
        docker push jandigarte/requirements:latest;
    fi
else
    echo "Execute 'sh build.sh publish' to publish images"
fi
