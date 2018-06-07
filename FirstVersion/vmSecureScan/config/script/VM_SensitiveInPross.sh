#!/bin/bash -x

key_words='pass|password|passwd|pswd|mima|key|pwd|PINNUMBER|secret|X-Auth-Token|Authorization|sessionID|token|email'
ps -ef | egrep -i "$key_words" |grep -v grep
