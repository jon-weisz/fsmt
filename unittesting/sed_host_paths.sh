#!/bin/bash

for i in `ls |grep ssh`; do sed -i "s/<execution_host val=\"localhost\" \/>/<execution_host val=\"$HOSTNAME\" \/>/" $i; done
for i in `ls |grep ssh`; do sed -i "s/<path val=\"\/homes\/flier\/dev\/fsmt\/fsmt-0.18\/bin\/\" \/>/<path val=\"\$WORKSPACE\/bin\/\" \/>/" $i; done
