#!/bin/bash

echo "Recording ARTV Angles"
rostopic echo /atrv/pose > $FSMDAT/$FSMTRA.log
