#!/usr/bin/env bash

until cd /home/dsaez/wmf-interlanguage/SectionRecommendation/app; sudo python3 test.py >> myserver.log 2>> myserver.error.log; do
    echo "$(date -u) - Server crashed with exit code $?.  Respawning..." >> runner.log
    sleep 1
done

echo "$(date -u) - Server manually killed" >> runner.log

