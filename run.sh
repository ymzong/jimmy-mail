#!/bin/bash

# run.sh
# Yiming Zong - Carnegie Mellon University '16
# yzong (at) cmu.edu
# -----------------------------------------------------------
#     This is the executable shell script for running Jimmy-Mail.
#     You can change this file for your own needs. For example, you can
# change the "$*" below to "your@emailaddress.com" so that everytime the
# default email will be "your@emailaddress.com" for Jimmy-Mail and thus
# you do not need to enter again.

python main.py $*

