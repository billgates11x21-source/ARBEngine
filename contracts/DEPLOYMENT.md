# MultiExchangeArbEngine Deployment Guide

This guide walks you through deploying the MultiExchangeArbEngine contract to the Base network and setting up arbitrage paths.

## Prerequisites

1. **Private Key**: You need a wallet with ETH on the Base network
2. **API Keys**: 
   - Infura or Alchemy API key for RPC access
   - BaseScan API key for contract verification
3. **Node.js Environment**: Node.js and npm installed

## Step 1: Set Up Environment Variables

Create a `.env` file in the project root with the following variables:

```
# Blockchain RPC URLs
INFURA_API_KEY=your_infura_api_key
ALCHEMY_API_KEY=your_alchemy_api_key

# Explorer API Keys for contract verification
ETHERSCAN_API_KEY=your_etherscan_api_key
BASESCAN_API_KEY=your_basescan_api_key

# Wallet Private Key (without 0x prefix)
PRIVATE_KEY=your_private_key_without_0x_prefix
```

## Step 2: Install Dependencies

```bash
cd ARBEngine
npm install --save @aave/core-v3 @openzeppelin/contracts @uniswap/v2-periphery hardhat @nomicfoundation/hardhat-toolbox dotenv
```

## Step 3: Compile the Contract

```bash
npx hardhat compile
```

## Step 4: Deploy to Base Network

```bash
npx hardhat run scripts/deploy-multi-exchange.js --network base
```

This script will:
1. Deploy the MultiExchangeArbEngine contract
2. Add popular exchanges on Base
3. Verify the contract on BaseScan

After deployment, you'll see output like:

```
MultiExchangeArbEngine deployed to: 0x...
Exchanges added: 4
Contract verified successfully
```

**Important**: Save the contract address for the next steps.

## Step 5: Set Up Arbitrage Paths

Set the contract address as an environment variable:

```bash
export CONTRACT_ADDRESS=0x... # Your deployed contract address
```

Then run the setup script:

```bash
npx hardhat run scripts/setup-arbitrage-paths.js --network base
```

This will add several arbitrage paths across different exchanges.

## Step 6: Execute Arbitrage

Start the arbitrage monitoring and execution script:

```bash
npx hardhat run scripts/execute-arbitrage.js --network base
```

This script will:
1. Monitor all arbitrage paths for profitable opportunities
2. Simulate potential profits before execution
3. Execute flash loan arbitrage when profitable
4. Report profits after successful execution

## Step 7: Withdraw Profits

When you want to withdraw profits, use the Hardhat console:

```bash
npx hardhat console --network base
```

Then execute:

```javascript
const MultiExchangeArbEngine = await ethers.getContractFactory("MultiExchangeArbEngine");
const arbEngine = await MultiExchangeArbEngine.attach("0x..."); // Your contract address
await arbEngine.withdraw("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"); // USDC on Base
```

## Troubleshooting

### Gas Errors

If you encounter "out of gas" errors:
- Increase the gas limit in the hardhat.config.js file
- Reduce the complexity of arbitrage paths
- Try during periods of lower network congestion

### Flash Loan Errors

If flash loans fail:
- Ensure the Aave Pool Address Provider is correct for the network
- Check that the token you're borrowing is supported by Aave
- Verify there's enough liquidity in the Aave pool

### Slippage Errors

If trades fail due to slippage:
- Reduce the loan amount
- Choose paths with higher liquidity
- Implement more sophisticated slippage protection

## Monitoring and Maintenance

### Checking Contract Balance

```javascript
const usdc = await ethers.getContractAt("IERC20", "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913");
const balance = await usdc.balanceOf("0x..."); // Your contract address
console.log(`USDC Balance: ${ethers.formatUnits(balance, 6)}`);
```

### Updating Exchange Routers

If an exchange updates its router address:

```javascript
await arbEngine.updateExchange(0, "0xNEW_ROUTER_ADDRESS", "Exchange Name", true);
```

### Pausing Specific Arbitrage Paths

If a path becomes unprofitable:

```javascript
const pathKey = await arbEngine.pathKeys(0);
await arbEngine.updateArbitragePath(pathKey, false);
```

## Security Best Practices

1. **Regular Audits**: Periodically review the contract for vulnerabilities
2. **Profit Monitoring**: Set up alerts for unexpected profit patterns
3. **Gas Price Monitoring**: Avoid executing during gas price spikes
4. **Exchange Updates**: Stay informed about exchange protocol updates
5. **Withdrawal Limits**: Consider implementing withdrawal limits and timeouts

## Advanced Configuration

For advanced users, you can modify the contract parameters:

1. **Custom Exchanges**: Add specialized exchanges with unique swap mechanics
2. **Complex Paths**: Create paths with more than 3 tokens for multi-hop arbitrage
3. **Token Allowlists**: Modify the contract to only work with specific tokens
4. **Gas Optimization**: Implement gas price oracles for optimal execution timing