#!/bin/bash

find ./webgui/ -iname '*.py' | xargs pylint --load-plugins pylint_django --disable=R,C
