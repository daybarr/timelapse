#!/bin/sh

ffmpeg -f image2 -r 10 -pattern_type glob -i '*.jpg' -s 720x540 -vf 'transpose=1' movie.mp4
