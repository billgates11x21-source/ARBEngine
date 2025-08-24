# ARBengine Documentation

## Overview
ARBengine is a fully autonomous arbitrage engine combining:
- Multi-DEX + CEX scanning
- Flash loan arbitrage (free + paid platforms)
- Self-healing resilience
- Glassmorphism dashboard

## Structure
- `src/config.py` → loads environment keys
- `src/utils/resilience.py` → retries, circuit breaker
- `src/strategies/` → arb, scalper, breakout, liquidity, cross-agg
- `src/discovery/` → token/DEX discovery
- `src/api/server.py` → FastAPI backend
- `Dashboard/` → React Native Expo dashboard

## Usage
1. Install dependencies: `pip install -r requirements.txt`
2. Copy env: `cp .env.example .env`
3. Run orchestrator: `python src/runner_orchestrator.py`
4. Run API server: `uvicorn src.api.server:app --port 8000`
5. Start dashboard: `npm start` inside Dashboard/

## Security
- Never commit real API keys to GitHub
- Always use .env for secrets


