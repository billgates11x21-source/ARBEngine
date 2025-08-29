from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.strategies.arb_engine import ArbEngine
from src.api.okx_client import OKXClient
import asyncio
import threading
import time

app = FastAPI()
arb = ArbEngine()
okx = OKXClient()

# Enable CORS for the dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Start WebSockets in a background thread
def start_ws_background():
    okx.start_websockets()
    time.sleep(2)  # Give time for connection to establish
    
    # Subscribe to ticker updates for common trading pairs
    for pair in ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "ADA-USDT", 
                "XRP-AUD", "AUD-USDT", "BTC-AUD", "ETH-AUD"]:  # Added AUD pairs for triangular arbitrage
        okx.subscribe_public("tickers", pair)
    
    # Subscribe to account updates
    okx.subscribe_private("account")
    okx.subscribe_private("orders")

# Start WebSockets in background
threading.Thread(target=start_ws_background).start()

@app.get('/')
def root():
    return {'status': 'ARBengine API running'}

@app.get('/balance')
async def balance():
    try:
        # Get real balance from OKX
        balance_data = okx.get_account_balance()
        return {'balances': balance_data}
    except Exception as e:
        # Fallback to demo data if API call fails
        return {'balances': arb.balance, 'note': 'Demo data (API error occurred)'}

@app.get('/last_trade')
def last_trade():
    return arb.state.get('last_trade', {})

@app.get('/profit')
def profit():
    # Calculate total profit from state
    total_profit = sum([trade.get('profit', 0) for trade in arb.state.get('trades', [])])
    return {'total_profit': total_profit}

@app.get('/market/ticker/{instId}')
async def get_ticker(instId: str):
    try:
        ticker_data = okx.get_ticker(instId)
        return ticker_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching ticker: {str(e)}")

@app.get('/market/orderbook/{instId}')
async def get_orderbook(instId: str, depth: int = 20):
    try:
        orderbook = okx.get_orderbook(instId, str(depth))
        return orderbook
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching orderbook: {str(e)}")

@app.get('/strategies/available')
def available_strategies():
    return {
        "strategies": [
            {
                "id": "scalping",
                "name": "Scalping Strategy",
                "description": "Quick trades to profit from small price movements"
            },
            {
                "id": "breakout",
                "name": "Breakout Strategy",
                "description": "Capitalizes on price movements beyond support/resistance levels"
            },
            {
                "id": "liquidity",
                "name": "Liquidity Strategy",
                "description": "Provides liquidity to earn fees in high-volume markets"
            },
            {
                "id": "crossagg",
                "name": "Cross-Exchange Aggregation",
                "description": "Finds price differences across multiple exchanges"
            },
            {
                "id": "arb",
                "name": "Arbitrage Strategy",
                "description": "Exploits price differences between markets"
            },
            {
                "id": "triangular_arb",
                "name": "Triangular Arbitrage",
                "description": "Exploits price differences across three related trading pairs"
            }
        ]
    }

@app.get('/strategies/active')
def active_strategies():
    # This would normally come from a database or state management system
    return {
        "active_strategies": [
            {
                "id": "scalping",
                "status": "running",
                "last_execution": "2025-08-29T12:30:45Z",
                "profit_24h": 0.42
            },
            {
                "id": "breakout",
                "status": "running",
                "last_execution": "2025-08-29T14:15:22Z",
                "profit_24h": 0.18
            },
            {
                "id": "triangular_arb",
                "status": "running",
                "last_execution": "2025-08-29T15:05:12Z",
                "profit_24h": 0.65
            }
        ]
    }

@app.post('/strategies/{strategy_id}/toggle')
async def toggle_strategy(strategy_id: str):
    # This would normally update a database or state management system
    return {"status": "success", "strategy_id": strategy_id, "active": True}