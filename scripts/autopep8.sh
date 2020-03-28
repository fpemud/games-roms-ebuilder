#!/bin/bash

FILES="$(find ./src | tr '\n' ' ')"

autopep8 -ia --ignore=E408,E501 ${FILES}
