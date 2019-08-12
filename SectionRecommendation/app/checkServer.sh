#!/bin/bash
ps aux | grep [t]est.[py] 
if [ $? -eq 0 ]; then
  echo "Process is running." 
else
	cd /home/dsaez/wmf-interlanguage/SectionRecommendation/app/; sudo ./runServer.sh
fi
