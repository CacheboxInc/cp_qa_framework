#!/bin/bash
#we keep churning stats into this file continuously as long as the run/test keeps progressing
MY_LOG=/piodb/tmp/container_stats.log

echolog(){
    if [ $# -eq 0 ]
    then cat - | while read -r message
        do
                echo "$(date +"[%F %T %Z] -") $message" | tee -a $MY_LOG
            done
    else
        echo -n "$(date +'[%F %T %Z]') - " | tee -a $MY_LOG
        echo $* | tee -a $MY_LOG
    fi
}
docker stats | echolog
