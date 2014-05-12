#!/bin/bash

echo "Recording ARTV Angles"
rostopic echo /atrv/pose > $1.log
