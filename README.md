![CI](https://github.com/x1asdkl-hue/ARBEngine/actions/workflows/ci.yml/badge.svg) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg) ![Python](https://img.shields.io/badge/python-3.10%2B-blue)

![CI](https://github.com/x1asdkl-hue/ARBEngine/actions/workflows/ci.yml/badge.svg)

# ARBengine
Autonomous arbitrage engine with:
- Multi-DEX + OKX scanning
- Paid & free flash loans
- Strict 80/20 (BTC/ETH) and 90/10 (alts) rules
- Simulation-first
- Neon/glass dashboard

## Setup
pip install -r requirements.txt
cp .env.example .env

## Run
python -m src.runner_orchestrator
