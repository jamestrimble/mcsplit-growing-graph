#!/bin/bash

# seq 1 45 | parallel "sh -c \"../ijcai2017-partitioning-common-subgraph/code/james-cpp/mcsp --dimacs min_max generated-graphs/G{}.grf generated-graphs/H{}.grf > c-results/{}.txt\""

echo n k x

for i in $(seq 1 45); do
    echo $i $(cat c-results/$i.txt | grep 'Solution size' | cut -d' ' -f3) $(echo $i | awk '{
        N = $1;
        a = 4/log(2);
        b = -2/log(2);
        c = 1/2 * a * (1-log(a));
        printf("%.0f", a * log(N) + b * log(log(N)) + c)
    }')
done
