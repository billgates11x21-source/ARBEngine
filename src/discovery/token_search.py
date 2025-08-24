import requests

class TokenDiscovery:
    def __init__(self):
        self.tokens=[]

    def fetch_from_1inch(self, chain_id=1):
        url=f'https://api.1inch.io/v5.0/{chain_id}/tokens'
        try:
            data=requests.get(url,timeout=10).json()
            self.tokens=list(data['tokens'].keys())
            print(f'[DISCOVERY] Loaded {len(self.tokens)} tokens from 1inch on chain {chain_id}')
        except Exception as e:
            print('[DISCOVERY] Error fetching tokens:', e)

    def fetch_from_0x(self, chain_id=1):
        url=f'https://api.0x.org/swap/v1/tokens'
        try:
            data=requests.get(url,timeout=10).json()
            symbols=[t['symbol'] for t in data['records']]
            self.tokens.extend(symbols)
            print(f'[DISCOVERY] Loaded {len(symbols)} tokens from 0x')
        except Exception as e:
            print('[DISCOVERY] Error fetching tokens:', e)

