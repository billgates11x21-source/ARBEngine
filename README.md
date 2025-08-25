# ARBengine

![CI](https://github.com/x1asdkl-hue/ARBEngine/actions/workflows/ci.yml/badge.svg?branch=main)
![Version](https://img.shields.io/badge/version-0.1.0-orange)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)

Autonomous arbitrage engine with:

- Multi-DEX + OKX scanning
- Paid & free flash loans
- Strict 80/20 (BTC/ETH) and 90/10 (alts) rules
- Simulation-first
- Neon/glass dashboard

## Setup

\`\`\`bash
pip install -r requirements.txt
cp .env.example .env
\`\`\`

## Regulatory Compliance

This project is intended for lawful use in accordance with Australian financial regulations. Users are responsible for their own compliance.

## Security

Never commit real API keys or secrets to GitHub. Always use `.env` for secrets. Example configuration is provided in `.env.example`.
