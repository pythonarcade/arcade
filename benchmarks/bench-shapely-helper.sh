#!/usr/bin/env bash

if [ "$2" == "disabled" ]
then
    export DISABLE_SHAPELY=true
fi
python -m benchmarks.$1.bench