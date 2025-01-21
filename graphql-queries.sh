#!/bin/bash
#
# A bunch of useful GQL queries (used, or not, in that project).
#


# Fetch the latest block height
curl 'https://nodes.dusk.network/02/Chain' --data-raw \
   '{"topic":"gql","data":"query { block(height: -1) { header { height } } }"}'


# Fetch latest 100 blocks (only the height, and provisioner)
curl 'https://nodes.dusk.network/02/Chain' --data-raw \
   '{"topic":"gql","data":"fragment BlockInfo on Block { header { height, generatorBlsPubkey } } query() { blocks(last: 100) {...BlockInfo} }"}'


# Same as above, but using HTTP headers to pass the number of blocks to fetch as a variable
curl 'https://nodes.dusk.network/02/Chain' -H 'rusk-gqlvar-count: 100' --data-raw \
   '{"topic":"gql","data":"fragment BlockInfo on Block { header { height, generatorBlsPubkey } } query($count: Int!) { blocks(last: $count) {...BlockInfo} }"}'


# Fetch a range of blocks (here, from blocks at height 10 until 12)
curl 'https://nodes.dusk.network/02/Chain' --data-raw \
   '{"topic":"gql","data":"fragment BlockInfo on Block { header { height, generatorBlsPubkey } } query() { blocks(range: [10, 12]) {...BlockInfo} }"}'
