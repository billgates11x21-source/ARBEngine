// Script to monitor and execute arbitrage opportunities
const hre = require("hardhat");
const { ethers } = require("hardhat");

async function main() {
  console.log("Starting arbitrage monitoring...");

  // Get the network we're working with
  const network = hre.network.name;
  console.log(`Network: ${network}`);

  // Get the deployer account
  const [deployer] = await hre.ethers.getSigners();
  console.log(`Using account: ${deployer.address}`);
  
  // Get account balance
  const balance = await deployer.provider.getBalance(deployer.address);
  console.log(`Account balance: ${ethers.formatEther(balance)} ETH`);

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

  // Get the number of paths
  const pathCount = await arbEngine.getArbitragePathCount();
  console.log(`Number of arbitrage paths: ${pathCount}`);
  
  if (pathCount === 0) {
    console.error("No arbitrage paths found. Please set up paths first.");
    process.exit(1);
  }

  // Get all path keys
  const pathKeys = [];
  for (let i = 0; i < pathCount; i++) {
    const pathKey = await arbEngine.pathKeys(i);
    pathKeys.push(pathKey);
  }

  console.log(`Retrieved ${pathKeys.length} path keys`);

  // Define loan amounts to try (in token decimals)
  const loanAmounts = {
    // USDC and USDT (6 decimals)
    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48": ethers.parseUnits("1000", 6),
    "0xdAC17F958D2ee523a2206206994597C13D831ec7": ethers.parseUnits("1000", 6),
    "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913": ethers.parseUnits("1000", 6), // Base USDC
    "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb": ethers.parseUnits("1000", 6), // Base USDT
    
    // DAI and most ERC20s (18 decimals)
    "0x6B175474E89094C44Da98b954EedeAC495271d0F": ethers.parseUnits("1000", 18),
    
    // WETH (18 decimals)
    "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2": ethers.parseUnits("1", 18),
    "0x4200000000000000000000000000000000000006": ethers.parseUnits("1", 18), // Base WETH
    
    // WBTC (8 decimals)
    "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599": ethers.parseUnits("0.05", 8),
    "0x236aa50979D5f3De3Bd1Eeb40E81137F22ab794b": ethers.parseUnits("0.05", 8), // Base WBTC
    
    // Default for any other token (assume 18 decimals)
    "default": ethers.parseUnits("100", 18)
  };

  // Monitor and execute arbitrage opportunities
  console.log("Starting arbitrage monitoring loop...");
  
  // Run in a loop
  while (true) {
    try {
      console.log("\n--- Checking for arbitrage opportunities ---");
      console.log(`Time: ${new Date().toISOString()}`);
      
      // Check each path for profitability
      for (const pathKey of pathKeys) {
        try {
          // Get path details
          const pathDetails = await arbEngine.getArbitragePath(pathKey);
          const path = pathDetails[0];
          const exchangeIndexes = pathDetails[1];
          const active = pathDetails[2];
          
          if (!active) {
            console.log(`Path ${pathKey} is not active, skipping...`);
            continue;
          }
          
          // Get the first token in the path (the one we'll borrow)
          const firstToken = path[0];
          
          // Determine loan amount based on token
          let loanAmount;
          if (loanAmounts[firstToken]) {
            loanAmount = loanAmounts[firstToken];
          } else {
            loanAmount = loanAmounts["default"];
          }
          
          // Simulate arbitrage to check profitability
          console.log(`Simulating arbitrage for path starting with token ${firstToken}...`);
          const expectedProfit = await arbEngine.simulateArbitrage(pathKey, loanAmount);
          
          // Format the profit for display
          let formattedProfit;
          if (firstToken === "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48" || 
              firstToken === "0xdAC17F958D2ee523a2206206994597C13D831ec7" ||
              firstToken === "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913" ||
              firstToken === "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb") {
            formattedProfit = ethers.formatUnits(expectedProfit, 6);
          } else if (firstToken === "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599" ||
                     firstToken === "0x236aa50979D5f3De3Bd1Eeb40E81137F22ab794b") {
            formattedProfit = ethers.formatUnits(expectedProfit, 8);
          } else {
            formattedProfit = ethers.formatUnits(expectedProfit, 18);
          }
          
          console.log(`Expected profit: ${formattedProfit} tokens`);
          
          // Check if profitable
          if (expectedProfit > 0) {
            console.log(`Profitable opportunity found! Executing arbitrage...`);
            
            // Execute the arbitrage
            const tx = await arbEngine.startArbitrage(pathKey, loanAmount);
            console.log(`Transaction sent: ${tx.hash}`);
            
            // Wait for confirmation
            console.log("Waiting for confirmation...");
            const receipt = await tx.wait();
            
            console.log(`Arbitrage executed! Gas used: ${receipt.gasUsed}`);
            
            // Look for ArbitrageExecuted event to get actual profit
            const arbEvents = receipt.logs
              .filter(log => log.topics[0] === arbEngine.interface.getEventTopic('ArbitrageExecuted'))
              .map(log => arbEngine.interface.parseLog(log));
            
            if (arbEvents.length > 0) {
              const actualProfit = arbEvents[0].args.profit;
              let formattedActualProfit;
              
              if (firstToken === "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48" || 
                  firstToken === "0xdAC17F958D2ee523a2206206994597C13D831ec7" ||
                  firstToken === "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913" ||
                  firstToken === "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb") {
                formattedActualProfit = ethers.formatUnits(actualProfit, 6);
              } else if (firstToken === "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599" ||
                         firstToken === "0x236aa50979D5f3De3Bd1Eeb40E81137F22ab794b") {
                formattedActualProfit = ethers.formatUnits(actualProfit, 8);
              } else {
                formattedActualProfit = ethers.formatUnits(actualProfit, 18);
              }
              
              console.log(`Actual profit: ${formattedActualProfit} tokens`);
            }
          } else {
            console.log("Not profitable at the moment, skipping...");
          }
        } catch (pathError) {
          console.error(`Error processing path ${pathKey}:`, pathError.message);
        }
      }
      
      // Wait before next check
      console.log("Waiting 30 seconds before next check...");
      await new Promise(resolve => setTimeout(resolve, 30000));
      
    } catch (error) {
      console.error("Error in monitoring loop:", error.message);
      console.log("Waiting 60 seconds before retrying...");
      await new Promise(resolve => setTimeout(resolve, 60000));
    }
  }
}

main()
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });