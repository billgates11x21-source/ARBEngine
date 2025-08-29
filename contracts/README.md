# MultiExchangeArbEngine - Flash Loan Arbitrage Smart Contract

This smart contract enables flash loan arbitrage across multiple exchanges, allowing you to profit from price differences between different decentralized exchanges.

## Features

- **Multi-Exchange Support**: Works with 80+ exchanges including Uniswap, Sushiswap, Balancer, Curve, and more
- **Flash Loan Integration**: Uses Aave V3 for flash loans with minimal fees
- **Flexible Arbitrage Paths**: Define custom token paths across different exchanges
- **Profit Simulation**: Simulate arbitrage opportunities before execution
- **Gas Optimization**: Optimized for minimal gas usage during execution
- **Security Features**: Includes reentrancy protection and access controls

## Contract Architecture

The `MultiExchangeArbEngine` contract is designed with the following components:

1. **Exchange Registry**: Stores information about supported exchanges and their router addresses
2. **Arbitrage Paths**: Defines token paths and which exchanges to use for each swap
3. **Flash Loan Handler**: Manages borrowing and repaying flash loans from Aave
4. **Swap Execution**: Executes token swaps across different exchanges
5. **Profit Management**: Calculates and captures arbitrage profits

## Deployment

The contract has been deployed to the following networks:

- **Base Mainnet**: [Contract Address]
- **Ethereum Mainnet**: [Contract Address]

## How to Use

### 1. Adding Exchanges

```javascript
// Add a new exchange
await arbEngine.addExchange(
  "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D", // Router address
  "Uniswap V2" // Exchange name
);
```

### 2. Setting Up Arbitrage Paths

```javascript
// Define a token path
const path = [
  "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", // USDC
  "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", // WETH
  "0xdAC17F958D2ee523a2206206994597C13D831ec7", // USDT
  "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"  // USDC
];

// Define which exchange to use for each swap
const exchangeIndexes = [0, 1, 2]; // Use exchange 0 for first swap, 1 for second, 2 for third

// Add the arbitrage path
await arbEngine.addArbitragePath(path, exchangeIndexes);
```

### 3. Executing Arbitrage

```javascript
// Get the path key
const pathKey = await arbEngine.pathKeys(0);

// Simulate to check profitability
const expectedProfit = await arbEngine.simulateArbitrage(
  pathKey,
  ethers.parseUnits("1000", 6) // 1000 USDC
);

// Execute if profitable
if (expectedProfit > 0) {
  await arbEngine.startArbitrage(
    pathKey,
    ethers.parseUnits("1000", 6) // 1000 USDC
  );
}
```

### 4. Withdrawing Profits

```javascript
// Withdraw profits
await arbEngine.withdraw("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"); // USDC
```

## Scripts

The repository includes several scripts to help you interact with the contract:

- `deploy-multi-exchange.js`: Deploy the contract and add popular exchanges
- `setup-arbitrage-paths.js`: Set up common arbitrage paths
- `execute-arbitrage.js`: Monitor and execute profitable arbitrage opportunities

## Security Considerations

- The contract uses OpenZeppelin's ReentrancyGuard to prevent reentrancy attacks
- Access control ensures only the owner can add exchanges and arbitrage paths
- Flash loans are executed atomically to prevent partial execution issues
- Slippage protection is implemented to prevent sandwich attacks

## Advanced Usage

### Custom Exchange Integration

To integrate with exchanges that don't follow the Uniswap V2 interface, you'll need to:

1. Create a wrapper contract that adapts the exchange's interface
2. Add the wrapper contract as an exchange in the MultiExchangeArbEngine

### Gas Optimization

For optimal gas usage:

1. Use exchanges on the same network to avoid cross-chain transactions
2. Choose token paths with high liquidity
3. Execute during periods of low network congestion
4. Consider using flashbots to avoid frontrunning

## License

This project is licensed under the MIT License.