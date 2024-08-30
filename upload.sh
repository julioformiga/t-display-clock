#!/bin/bash

mpremote mkdir :/lib
mpremote mkdir :/lib/primitives
mpremote cp src/*.py :
mpremote cp src/lib/*.py :lib/
mpremote cp src/lib/primitives/*.py :lib/primitives/
mpremote soft-reset
