#!/usr/bin/python
import sys
from steamiebot import tryPost


if len(sys.argv) > 1:
    configFile = sys.argv[1]
else:
    configFile = "steamietest.ini"

tryPost(configFile)
