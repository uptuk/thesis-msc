# Analysis of Decentralized Mixing Services in the Greater Bitcoin Ecosystem

Implementation of heuristics used in the master thesis __Analysis of Decentralized Mixing Services in the Greater 
Bitcoin Ecosystem__.

## Requirements
* Python 3.7 (more recent versions of Python should work just fine)
  * See `requirements.txt` for additional required Python packages
* A Full Bitcoin Node (https://bitcoin.org/en/full-node, the raw data will be parsed by [bitcoin-blockchain-parser](https://github.com/alecalve/python-bitcoin-blockchain-parser))

## Replicating Data

In `utils.py` change the value of `API_KEY` in the class `GraphsenseConfig` to an actual [GraphSense](https://graphsense.info/) 
API key. Then, execute the Python files in order (check the individual `-h` help commands for possible/required 
parameters):
1. `1_parse_coinjoins.py`
2. `2_get_inputs_for_txs.py` (you probably want to run this twice - once for Wasabi, once for Samourai)
3. `3_refine_wasabi.py` (for Wasabi)
4. `3_refine_samourai` (for Samourai)