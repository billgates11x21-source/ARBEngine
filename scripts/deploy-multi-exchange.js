// Deployment script for MultiExchangeArbEngine contract
const hre = require("hardhat");

async function main() {
  console.log("Deploying MultiExchangeArbEngine contract...");

  // Get the network we're deploying to
  const network = hre.network.name;
  console.log(`Deploying to ${network} network`);

  // Get the deployer account
  const [deployer] = await hre.ethers.getSigners();
  console.log(`Deploying with account: ${deployer.address}`);

  // Get the account balance
  const balance = await deployer.provider.getBalance(deployer.address);
  console.log(`Account balance: ${hre.ethers.formatEther(balance)} ETH`);

  // Aave Pool Address Provider - use the correct one for the network
  let poolAddressProvider;
  
  if (network === "base") {
    // Base Mainnet
    poolAddressProvider = "0xe20fCBdBfFC4Dd138cE8b2E6FBb6CB49777ad64D"; // Aave V3 on Base
  } else if (network === "base-sepolia") {
    // Base Sepolia Testnet
    poolAddressProvider = "0x0E8C1a6C0010C88d3e5Fa1e9a4BEb302371C3157"; // Aave V3 on Base Sepolia
  } else if (network === "ethereum") {
    // Ethereum Mainnet
    poolAddressProvider = "0x2f39d218133AFaB8F2B819B1066c7E434Ad94E9e"; // Aave V3 on Ethereum
  } else if (network === "sepolia") {
    // Sepolia Testnet
    poolAddressProvider = "0x012bAC54348C0E635dCAc9D5FB99f06F24136C9A"; // Aave V3 on Sepolia
  } else {
    console.log("Using default Aave V3 Pool Address Provider for testing");
    poolAddressProvider = "0x2f39d218133AFaB8F2B819B1066c7E434Ad94E9e"; // Default to Ethereum Mainnet
  }

  // Deploy the contract
  const MultiExchangeArbEngine = await hre.ethers.getContractFactory("MultiExchangeArbEngine");
  const arbEngine = await MultiExchangeArbEngine.deploy(
    poolAddressProvider,
    deployer.address // Owner address
  );

  await arbEngine.waitForDeployment();
  
  const contractAddress = await arbEngine.getAddress();
  console.log(`MultiExchangeArbEngine deployed to: ${contractAddress}`);

  // Add some popular exchanges
  console.log("Adding popular exchanges...");
  
  // Define exchange routers for different networks
  const exchanges = [];
  
  if (network === "base") {
    // Base Mainnet exchanges
    exchanges.push({
      name: "Uniswap V3",
      router: "0x2626664c2603336E57B271c5C0b26F421741e481"
    });
    exchanges.push({
      name: "Sushiswap",
      router: "0x6BDED42c6DA8FBf0d2bA55B2fa120C3B5714F1Ea"
    });
    exchanges.push({
      name: "Baseswap",
      router: "0x327Df1E6de05895d2ab08513aaDD9313Fe505d86"
    });
    exchanges.push({
      name: "Aerodrome",
      router: "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43"
    });
  } else if (network === "ethereum") {
    // Ethereum Mainnet exchanges
    exchanges.push({
      name: "Uniswap V2",
      router: "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    });
    exchanges.push({
      name: "Sushiswap",
      router: "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
    });
    exchanges.push({
      name: "Pancakeswap",
      router: "0xEfF92A263d31888d860bD50809A8D171709b7b1c"
    });
    exchanges.push({
      name: "Balancer",
      router: "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
    });
  } else {
    // Default exchanges for testing
    exchanges.push({
      name: "Uniswap V2",
      router: "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    });
    exchanges.push({
      name: "Sushiswap",
      router: "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
    });
  }

  // Add exchanges to the contract
  for (const exchange of exchanges) {
    console.log(`Adding ${exchange.name} exchange...`);
    const tx = await arbEngine.addExchange(exchange.router, exchange.name);
    await tx.wait();
    console.log(`${exchange.name} added successfully`);
  }

  console.log("Deployment and setup complete!");
  console.log(`Contract address: ${contractAddress}`);
  console.log(`Exchanges added: ${exchanges.length}`);
  
  // Verify contract on Etherscan if not on a local network
  if (network !== "hardhat" && network !== "localhost") {
    console.log("Waiting for block confirmations before verification...");
    await arbEngine.deploymentTransaction().wait(5);
    
    console.log("Verifying contract on explorer...");
    try {
      await hre.run("verify:verify", {
        address: contractAddress,
        constructorArguments: [
          poolAddressProvider,
          deployer.address
        ],
      });
      console.log("Contract verified successfully");
    } catch (error) {
      console.error("Error verifying contract:", error);
    }
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });