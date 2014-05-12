#!/bin/bash

echo "Sending Data to ATRV"
rostopic pub -1 /atrv/motion geometry_msgs/Twist "{linear: {x: .5}, angular: {z: .5}}"
sleep 3
rostopic pub -1 /atrv/motion geometry_msgs/Twist "{linear: {x: 5.5}, angular: {z: 2.0}}"
