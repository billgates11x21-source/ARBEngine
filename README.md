# ARBEngine - OKX Trading Dashboard

## Overview

ARBEngine is an automated trading system for OKX that implements 6 different spot wallet trading strategies. The system is designed to run autonomously, finding and executing profitable trading opportunities without user intervention.

## Features

- **Automated Trading**: All strategies run automatically without requiring user input
- **Multiple Strategies**: 6 different spot trading strategies working simultaneously:
  - **Scalping Strategy**: Quick trades to profit from small price movements
  - **Breakout Strategy**: Capitalizes on price movements beyond support/resistance levels
  - **Liquidity Strategy**: Provides liquidity to earn fees in high-volume markets
  - **Cross-Exchange Aggregation**: Finds price differences across multiple exchanges
  - **Arbitrage Strategy**: Exploits price differences between markets
  - **Triangular Arbitrage**: Exploits price differences across three related trading pairs (with AUD pairs)
- **Real-time Monitoring**: Track profits, balances, and trade history
- **Mobile Optimized**: Fully responsive design for Android devices
- **Secure API Integration**: Safely connected to your OKX account
- **Automatic Error Handling**: Built-in error detection, recovery, and reporting
- **Connection Monitoring**: Continuous monitoring of API connections with automatic reconnection

## Triangular Arbitrage

The triangular arbitrage strategy specifically focuses on AUD-based trading pairs:
- XRP -> AUD -> USDT -> XRP
- BTC -> AUD -> USDC -> BTC
- SOL -> USDT -> AUD -> SOL
- ETH -> AUD -> USDT -> ETH
- LTC -> AUD -> USDT -> LTC

This strategy monitors price differences across these triangular paths and executes trades when profitable opportunities are detected.

## Deployment Options

### Option 1: Local Deployment

1. Clone the repository:
```bash
git clone https://github.com/billgates11x21-source/ARBEngine.git
cd ARBEngine
```

2. Create a `.env` file with your OKX API credentials:
```
OKX_API_KEY=your_api_key
OKX_API_SECRET=your_api_secret
OKX_API_PASSPHRASE=your_passphrase
OKX_API_NAME=your_api_name
OKX_PERMISSIONS=Read/Withdraw/Trade
OKX_IP=your_ip_address
```

3. Install backend dependencies:
```bash
pip install -r requirements.txt
```

4. Install dashboard dependencies:
```bash
cd Dashboard
npm install
```

5. Run the application:
```bash
./start.sh
```

### Option 2: Replit Deployment (Recommended)

1. Go to [Replit](https://replit.com) and create an account if you don't have one.

2. Click on "Create Repl" and select "Import from GitHub".

3. Enter the repository URL: `https://github.com/billgates11x21-source/ARBEngine.git`

4. Click "Import from GitHub" and wait for the repository to be imported.

5. Once imported, Replit will automatically detect the project configuration.

6. Click the "Run" button to start the application.

7. The application will be available at the URL provided by Replit.

## Dashboard

The dashboard provides a user-friendly interface to monitor your trading activities:

- **Home**: System status and overview
- **Explore**: Monitor account balance, active strategies, and trading performance
- **System Status**: View connection status, error statistics, and system health

## API Endpoints

The backend API provides several endpoints:

- `GET /`: API status
- `GET /balance`: Account balance
- `GET /last_trade`: Last executed trade
- `GET /profit`: Total profit
- `GET /market/ticker/{instId}`: Current ticker for a trading pair
- `GET /market/orderbook/{instId}`: Current orderbook for a trading pair
- `GET /strategies/available`: List of available strategies
- `GET /strategies/active`: List of active strategies
- `POST /strategies/{strategy_id}/toggle`: Toggle a strategy on/off
- `GET /triangular/opportunities`: Get current triangular arbitrage opportunities
- `GET /triangular/status`: Get status of triangular arbitrage strategy
- `GET /system/status`: Get system status including API connections
- `GET /system/errors`: Get system error information

## Error Handling

The system includes robust error handling:

- **Automatic Recovery**: The system attempts to recover from common errors
- **Error Logging**: All errors are logged for later analysis
- **Connection Monitoring**: WebSocket and API connections are continuously monitored
- **Automatic Reconnection**: The system automatically reconnects if connections are lost

## Security

- API keys are stored securely in the `.env` file
- All API requests are authenticated using OKX's signature mechanism
- The system uses HTTPS for all external communications

## Disclaimer

This software is for educational purposes only. Trading cryptocurrencies involves significant risk. Use at your own risk.