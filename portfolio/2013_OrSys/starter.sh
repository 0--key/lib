#!/bin/bash
#cd /home/antony/Desktop/projects/OrSys/orsys
cd "$(dirname "$0")"
DATE=`date +%Y-%m-%d`

python detector.py

echo $DATE
echo "!?"