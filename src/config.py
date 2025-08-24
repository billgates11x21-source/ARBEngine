import os
from dotenv import load_dotenv
load_dotenv()

OKX_API_KEY        = os.getenv('OKX_API_KEY')
OKX_API_SECRET     = os.getenv('OKX_API_SECRET')
OKX_API_PASSPHRASE = os.getenv('OKX_API_PASSPHRASE')
OKX_API_NAME       = os.getenv('OKX_API_NAME')
OKX_PERMISSIONS    = os.getenv('OKX_PERMISSIONS')
OKX_IP             = os.getenv('OKX_IP')

ONEINCH_API_KEY    = os.getenv('ONEINCH_API_KEY')
ZEROX_API_KEY      = os.getenv('ZEROX_API_KEY')

RPC_1              = os.getenv('RPC_1')
PRIVATE_KEY        = os.getenv('PRIVATE_KEY')

CHECKPOINT_FILE    = 'state.json'

def load_state():
    import json, os
    return json.load(open(CHECKPOINT_FILE)) if os.path.exists(CHECKPOINT_FILE) else {}

def save_state(state):
    import json
    json.dump(state, open(CHECKPOINT_FILE,'w'), indent=2)
