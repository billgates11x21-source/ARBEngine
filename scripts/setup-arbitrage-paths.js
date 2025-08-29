// Script to set up arbitrage paths for the MultiExchangeArbEngine contract
const hre = require("hardhat");

async function main() {
  console.log("Setting up arbitrage paths...");

  // Get the network we're working with
  const network = hre.network.name;
  console.log(`Network: ${network}`);

  // Get the deployer account
  const [deployer] = await hre.ethers.getSigners();
  console.log(`Using account: ${deployer.address}`);

  // Contract address - replace with your deployed contract address
  const contractAddress = process.env.CONTRACT_ADDRESS;
  if (!contractAddress) {
    console.error("Please set CONTRACT_ADDRESS in your environment variables");
    process.exit(1);
  }

  // Get the contract instance
  const MultiExchangeArbEngine = await hre.ethers.getContractFactory("MultiExchangeArbEngine");
  const arbEngine = await MultiExchangeArbEngine.attach(contractAddress);

  console.log(`Connected to contract at: ${contractAddress}`);

  // Get the number of exchanges
  const exchangeCount = await arbEngine.getExchangeCount();
  console.log(`Number of exchanges: ${exchangeCount}`);
  if (exchangeCount === 0) {
    console.error("No exchanges found. Please add exchanges first.");
    process.exit(1);
  }

  // Define token addresses based on the network
  let tokens = {};
  
  if (network === "base") {
    // Base Mainnet tokens
    tokens = {
      USDC: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      USDT: "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
      DAI: "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
      WETH: "0x4200000000000000000000000000000000000006",
      WBTC: "0x236aa50979D5f3De3Bd1Eeb40E81137F22ab794b",
      USDbC: "0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA"
    };
  } else if (network === "ethereum") {
    // Ethereum Mainnet tokens
    tokens = {
      USDC: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
      USDT: "0xdAC17F958D2ee523a2206206994597C13D831ec7",
      DAI: "0x6B175474E89094C44Da98b954EedeAC495271d0F",
      WETH: "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
      WBTC: "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
    };
  } else {
    // Default tokens for testing
    tokens = {
      USDC: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
      USDT: "0xdAC17F958D2ee523a2206206994597C13D831ec7",
      DAI: "0x6B175474E89094C44Da98b954EedeAC495271d0F",
      WETH: "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
      WBTC: "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
    };
  }

  // Define arbitrage paths
  const arbitragePaths = [
    {
      name: "USDC-WETH-USDT-USDC",
      path: [tokens.USDC, tokens.WETH, tokens.USDT, tokens.USDC],
      exchangeIndexes: [0, 1, 2] // Use first 3 exchanges in sequence
    },
    {
      name: "USDT-WBTC-WETH-USDT",
      path: [tokens.USDT, tokens.WBTC, tokens.WETH, tokens.USDT],
      exchangeIndexes: [1, 0, 2] // Mix different exchanges
    },
    {
      name: "DAI-WETH-USDC-DAI",
      path: [tokens.DAI, tokens.WETH, tokens.USDC, tokens.DAI],
      exchangeIndexes: [0, 1, 0] // Reuse exchanges
    },
    {
      name: "WETH-WBTC-USDC-WETH",
      path: [tokens.WETH, tokens.WBTC, tokens.USDC, tokens.WETH],
      exchangeIndexes: [1, 2, 0] // Different order
    }
  ];

  // Add each arbitrage path
  for (const path of arbitragePaths) {
    console.log(`Adding arbitrage path: ${path.name}`);
    
    try {
      const tx = await arbEngine.addArbitragePath(path.path, path.exchangeIndexes);
      await tx.wait();
      console.log(`Successfully added path: ${path.name}`);
    } catch (error) {
      console.error(`Error adding path ${path.name}:`, error.message);
    }
  }

  // Get the number of paths
  const pathCount = await arbEngine.getArbitragePathCount();
  console.log(`Total arbitrage paths: ${pathCount}`);

  console.log("Setup complete!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });