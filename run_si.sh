#!/bin/bash

time pypy3 mcsplit-si.py 32 1 100 | tee si-results/si.txt

time pypy3 mcsplit-si-clique.py 32 1 100 | tee si-results/si-clique.txt

time python3 mcsplit-si-all.py 16 1 100 | tee si-results/si-all.txt
