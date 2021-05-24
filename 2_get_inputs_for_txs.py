# -*- coding: utf-8 -*-
"""
Fetches GraphSense data (including TX input addresses).
"""

import json
import asyncio
import logging.config
from argparse import ArgumentParser

from graphsense_simple import GraphsenseSimpleAsync
from utils import chunks, GraphsenseConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8.8s] %(message)s",
    handlers=[logging.StreamHandler()]
)


async def fetch(tx_ids: dict) -> list:
    """
    Fetches transaction details from GraphSense.
    :param tx_ids: The transactions to fetch
    :return: GraphSense transaction details
    """
    gsa = GraphsenseSimpleAsync(GraphsenseConfig.HOST, key=GraphsenseConfig.API_KEY)
    try:
        return await asyncio.gather(*[gsa.get_tx_hash(tx_id) for tx_id in tx_ids])
    except Exception as e:
        logging.error(f'Error fetching transactions: {e}')
        return []
    finally:
        await gsa.close()


if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('-i', '--in_', required=True,
                    help='Path to `parse_coinjoins.py` outputs for either Wasabi or Samourai')
    ap.add_argument('-o', '--out', required=True, help='Path to store results')
    args = ap.parse_args()

    with open(f'{args.in_}', 'r') as fp:
        txs_raw = json.load(fp)

    logging.info(f'Fetching {len(txs_raw)} transactions...')
    txs_parsed = list()
    parsed = 0
    # Fetch details in chunks
    for i, chunk in enumerate(chunks(txs_raw)):
        logging.info(f'Fetching {len(chunk.keys())} transactions ({i*1000}/{len(txs_raw)} TXs done, '
                     f'{round(parsed/len(txs_raw), 4)*100})')
        txs_parsed.extend(asyncio.run(fetch(chunk)))

    with open(f'{args.out}', 'w') as fp:
        json.dump(txs_parsed, fp)
