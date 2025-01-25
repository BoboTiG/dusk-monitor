#!/bin/bash
#
# A bunch of useful GQL queries (used, or not, in that project).
#
# Some Python code can be found here on how to use RUES:
#     https://github.com/BoboTiG/dusk-monitor/blob/d4ee9f94d96c3a115c6f375a8765862598d4e0f0/app/listen.py
#


# Fetch the latest block height
curl 'https://nodes.dusk.network/on/graphql/query' --data-raw \
   'query { block(height: -1) { header { height } } }'


# Fetch latest 100 blocks (only the height, and provisioner)
# You can find more retreivable data from `BlockInfo`: https://github.com/dusk-network/rusk/blob/835bc6f57d3f1edb06f45266b9005018772b0561/explorer/src/lib/services/gql-queries.js#L27
curl 'https://nodes.dusk.network/on/graphql/query' --data-raw \
   'fragment BlockInfo on Block { header { height, generatorBlsPubkey } } query() { blocks(last: 100) {...BlockInfo} }'


# Same as above, but using HTTP headers to pass the number of blocks to fetch as a variable
curl 'https://nodes.dusk.network/on/graphql/query' -H 'rusk-gqlvar-count: 100' --data-raw \
   'fragment BlockInfo on Block { header { height, generatorBlsPubkey } } query($count: Int!) { blocks(last: $count) {...BlockInfo} }'


# Fetch a range of blocks (here, from blocks at height 10 until 12)
curl 'https://nodes.dusk.network/on/graphql/query' --data-raw \
   'fragment BlockInfo on Block { header { height, generatorBlsPubkey } } query() { blocks(range: [10, 12]) {...BlockInfo} }'
