# -*- coding: utf-8 -*-
"""
Refines Samourai Whirlpool CoinJoin detections by performing additional checks to filter out false positives.
"""

import json
import logging.config
from argparse import ArgumentParser

from utils import Samourai

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8.8s] %(message)s",
    handlers=[logging.StreamHandler()]
)


def is_samourai_coin_join(tx: dict) -> bool:
    """
    Performs additional refinements to filter false positive detections:
    * TX must have 5 inputs and 5 outputs
    * Output value must be uniform and equal a valid Samourai Whirlpool pool size
    * TX must have 1-3 remix and 2-4 premix inputs
    :param tx: The transaction to check
    :return: True if the transaction is a Samourai Whirlpool CoinJoin
    """
    if len(tx['inputs']) == 5 and len(tx['outputs']) == 5:
        if len(set(output['value']['value'] for output in tx['outputs'])) == 1:
            for sz in Samourai.WHIRLPOOL_SIZES:
                if tx['outputs'][0]['value']['value'] == sz:
                    count_remix = 0
                    count_premix = 0
                    for tx_input_ in tx['inputs']:
                        if tx_input_['value']['value'] == sz:
                            count_remix += 1
                        elif sz < tx_input_['value']['value'] <= sz + Samourai.MAX_POOL_FEE:
                            count_premix += 1
                    return (count_remix == 1 and count_premix == 4)\
                        or (count_remix == 2 and count_premix == 3)\
                        or (count_remix == 3 and count_premix == 2)
    return False


if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('-r', '--in_raw', required=True, help='Path to raw detected Samourai Whirlpool transactions')
    ap.add_argument('-i', '--in_inputs', required=True,
                    help='Path to the detected Samourai Whirlpool transactions with GraphSense inputs')
    ap.add_argument('-o', '--out_refined', required=True, help='Path to store refined Samourai Whirlpool transactions')
    ap.add_argument('-k', '--out_tx0', required=True, help='Path to store Tx0 inputs')
    args = ap.parse_args()

    with open(f'{args.in_raw}', 'r') as fp:
        samourai_potentials = json.load(fp)
    with open(f'{args.in_inputs}', 'r') as fp:
        raw_txs_w_inputs = json.load(fp)

    raw_txs_w_inputs_dict = {tx['tx_hash']: tx for tx in raw_txs_w_inputs}

    refined_txs = dict()
    tx0_txids = list()
    for txid, txdata in raw_txs_w_inputs_dict.items():
        if is_samourai_coin_join(txdata):
            refined_txs[txid] = txdata

            # Get Tx0 inputs (input value not equal to a Samourai Whrilpool pool size)
            for idx, tx_input in enumerate(txdata['inputs']):
                if tx_input['value']['value'] not in Samourai.WHIRLPOOL_SIZES:
                    tx0_txids.append(samourai_potentials[txid]['tx']['inputs'][idx]['hash'])

    with open(f'{args.out_refined}', 'w') as fp:
        json.dump(refined_txs, fp)

    with open(f'{args.out_tx0}', 'w') as fp:
        json.dump(tx0_txids, fp)
