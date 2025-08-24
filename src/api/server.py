from fastapi import FastAPI
from src.strategies.arb_engine import ArbEngine

app = FastAPI()
arb = ArbEngine()

@app.get('/')
def root():
    return {'status':'ARBengine API running'}

@app.get('/balance')
def balance():
    return {'balances': arb.balance}

@app.get('/last_trade')
def last_trade():
    return arb.state.get('last_trade', {})
