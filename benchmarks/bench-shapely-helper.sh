#!/usr/bin/env bash

if [ "$1" == "disabled" ]
then
    export DISABLE_SHAPELY=true
fi
python -m benchmarks.collisions.bench