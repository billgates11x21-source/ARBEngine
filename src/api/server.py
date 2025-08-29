from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.strategies.arb_engine import ArbEngine
from src.api.okx_client import OKXClient
from src.runner_orchestrator import orchestrator
from src.utils.error_handler import error_handler
import asyncio
import threading
import time
import traceback

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

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_handler.handle_error(exc, f"API endpoint: {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "path": request.url.path},
    )

# Start WebSockets in a background thread
def start_ws_background():
    try:
        okx.start_websockets()
        time.sleep(2)  # Give time for connection to establish
        
        # Subscribe to ticker updates for common trading pairs
        for pair in ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "ADA-USDT", 
                    "XRP-AUD", "AUD-USDT", "BTC-AUD", "AUD-USDC", "SOL-AUD"]:
            okx.subscribe_public("tickers", pair)
        
        # Subscribe to account updates
        okx.subscribe_private("account")
        okx.subscribe_private("orders")
    except Exception as e:
        error_handler.handle_error(e, "WebSocket initialization")

# Start WebSockets in background
threading.Thread(target=start_ws_background).start()

# Start the strategy orchestrator
threading.Thread(target=orchestrator.start_monitoring).start()

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
        error_handler.handle_error(e, "balance endpoint")
        # Fallback to demo data if API call fails
        return {'balances': arb.balance, 'note': f'Demo data (API error occurred: {str(e)})'}

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
        error = error_handler.handle_error(e, f"get_ticker for {instId}")
        raise HTTPException(status_code=500, detail=f"Error fetching ticker: {str(e)}")

@app.get('/market/orderbook/{instId}')
async def get_orderbook(instId: str, depth: int = 20):
    try:
        orderbook = okx.get_orderbook(instId, str(depth))
        return orderbook
    except Exception as e:
        error_handler.handle_error(e, f"get_orderbook for {instId}")
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
    # Get active strategies from the orchestrator
    active_strategies = []
    for strategy_name, strategy in orchestrator.strategies.items():
        if strategy.active:
            status = strategy.get_status()
            active_strategies.append({
                "id": strategy_name,
                "status": "running",
                "last_execution": status.get('last_execution'),
                "profit_24h": status.get('profit_24h', 0.0)
            })
    
    return {"active_strategies": active_strategies}

@app.post('/strategies/{strategy_id}/toggle')
async def toggle_strategy(strategy_id: str):
    try:
        # Check if strategy exists
        if strategy_id not in orchestrator.strategies:
            raise HTTPException(status_code=404, detail=f"Strategy {strategy_id} not found")
        
        # Get current status
        status = orchestrator.get_strategy_status(strategy_id)
        
        # Toggle strategy
        if status.get('active', False):
            # Stop strategy
            result = orchestrator.stop_strategy(strategy_id)
            new_status = "stopped"
        else:
            # Start strategy
            result = orchestrator.start_strategy(strategy_id)
            new_status = "running"
        
        if not result:
            raise HTTPException(status_code=500, detail=f"Failed to toggle strategy {strategy_id}")
        
        return {"status": "success", "strategy_id": strategy_id, "active": new_status == "running"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        error_handler.handle_error(e, f"toggle_strategy for {strategy_id}")
        raise HTTPException(status_code=500, detail=f"Error toggling strategy: {str(e)}")

@app.get('/triangular/opportunities')
async def get_triangular_opportunities():
    """Get current triangular arbitrage opportunities"""
    try:
        # Check if triangular_arb strategy is initialized
        if 'triangular_arb' not in orchestrator.strategies:
            raise HTTPException(status_code=404, detail="Triangular arbitrage strategy not found")
        
        # Get the strategy instance
        strategy = orchestrator.strategies['triangular_arb']
        
        # Get opportunities
        opportunities = []
        for triangle in strategy.triangles:
            # Skip if we don't have ticker data for all pairs in the triangle
            if not all(pair in strategy.ticker_data for pair in triangle):
                continue
            
            # Calculate potential profit
            profit_pct, direction = strategy._calculate_triangle_profit(triangle)
            
            # Add to opportunities list if profit is positive
            if profit_pct > 0:
                opportunities.append({
                    "triangle": triangle,
                    "direction": direction,
                    "profit_pct": profit_pct,
                    "timestamp": time.time()
                })
        
        # Sort by profit percentage (descending)
        opportunities.sort(key=lambda x: x["profit_pct"], reverse=True)
        
        return {"opportunities": opportunities}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        error_handler.handle_error(e, "get_triangular_opportunities")
        raise HTTPException(status_code=500, detail=f"Error getting triangular opportunities: {str(e)}")

@app.get('/triangular/status')
async def get_triangular_status():
    """Get status of triangular arbitrage strategy"""
    try:
        # Check if triangular_arb strategy is initialized
        if 'triangular_arb' not in orchestrator.strategies:
            raise HTTPException(status_code=404, detail="Triangular arbitrage strategy not found")
        
        # Get the strategy instance
        strategy = orchestrator.strategies['triangular_arb']
        
        # Get status
        status = strategy.get_status()
        
        # Add open positions
        status['open_positions'] = list(strategy.open_positions.values())
        
        return status
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        error_handler.handle_error(e, "get_triangular_status")
        raise HTTPException(status_code=500, detail=f"Error getting triangular status: {str(e)}")

@app.get('/system/status')
async def system_status():
    """Get system status including API connections"""
    try:
        # Get OKX connection status
        okx_status = okx.get_connection_status()
        
        # Get orchestrator status
        orchestrator_status = {
            "running": orchestrator.running,
            "active_strategies": len([s for s in orchestrator.strategies.values() if s.active]),
            "total_strategies": len(orchestrator.strategies)
        }
        
        # Get error statistics
        error_stats = {
            "total_errors": sum(error_handler.error_counts.values()),
            "error_types": list(error_handler.error_counts.keys())
        }
        
        return {
            "okx_connections": okx_status,
            "orchestrator": orchestrator_status,
            "errors": error_stats,
            "system_time": time.time()
        }
    except Exception as e:
        error_handler.handle_error(e, "system_status")
        raise HTTPException(status_code=500, detail=f"Error getting system status: {str(e)}")

@app.get('/system/errors')
async def system_errors():
    """Get system error information"""
    try:
        return {
            "error_counts": error_handler.error_counts,
            "recent_errors": {
                key: len(timestamps) 
                for key, timestamps in error_handler.error_timestamps.items()
            }
        }
    except Exception as e:
        error_handler.handle_error(e, "system_errors")
        raise HTTPException(status_code=500, detail=f"Error getting error information: {str(e)}")