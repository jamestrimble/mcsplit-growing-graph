#!/bin/bash

pypy3 mcsplit.py $1 > results/full_results.txt

echo "n,v,graph,count" > results/counts.csv
cat results/full_results.txt | grep '^A' | cut -d' ' -f2- >> results/counts.csv

echo "n,soln_num,density,real" > results/densities.csv
cat results/full_results.txt | grep '^B' | cut -d' ' -f2- >> results/densities.csv

echo "n,k,count" > results/summary.csv
cat results/full_results.txt | grep '^SUMMARY' | cut -d' ' -f2- >> results/summary.csv

Rscript -e "rmarkdown::render('results.Rmd')"
