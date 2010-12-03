#!/bin/bash

for TRY in {1..1000}
do
    curl http://192.168.0.100:12345/ > /dev/null 2>/dev/null
done

