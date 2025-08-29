# ARBEngine - OKX Trading Dashboard

## Overview

ARBEngine is an automated trading system for OKX that implements 5 different spot wallet trading strategies. The system is designed to run autonomously, finding and executing profitable trading opportunities without user intervention.

## Features

- **Automated Trading**: All strategies run automatically without requiring user input
- **Multiple Strategies**: 5 different spot trading strategies working simultaneously:
  - **Scalping Strategy**: Quick trades to profit from small price movements
  - **Breakout Strategy**: Capitalizes on price movements beyond support/resistance levels
  - **Liquidity Strategy**: Provides liquidity to earn fees in high-volume markets
  - **Cross-Exchange Aggregation**: Finds price differences across multiple exchanges
  - **Arbitrage Strategy**: Exploits price differences between markets
- **Real-time Monitoring**: Track profits, balances, and trade history
- **Mobile Optimized**: Fully responsive design for Android devices
- **Secure API Integration**: Safely connected to your OKX account

## Setup

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

## Running the System

Use the start script to run both the backend API and the dashboard:

```bash
./start.sh
```

This will:
1. Start the OKX API server on port 8000
2. Launch the dashboard in development mode

## Dashboard

The dashboard provides a user-friendly interface to monitor your trading activities:

- **Home**: System status and overview
- **Explore**: Monitor account balance, active strategies, and trading performance

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

## Security

- API keys are stored securely in the `.env` file
- All API requests are authenticated using OKX's signature mechanism
- The system uses HTTPS for all external communications

## Disclaimer

This software is for educational purposes only. Trading cryptocurrencies involves significant risk. Use at your own risk.