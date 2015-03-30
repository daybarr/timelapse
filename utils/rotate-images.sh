#!/bin/sh

# sudo apt-get install libjpeg-turbo-progs
for i in *.jpg; do
    echo $i
    jpegtran -copy none -rotate 90 -outfile $i $i
done
