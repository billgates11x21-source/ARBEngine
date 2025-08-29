require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

// Load environment variables
const PRIVATE_KEY = process.env.PRIVATE_KEY || "0x0000000000000000000000000000000000000000000000000000000000000000";
const ETHERSCAN_API_KEY = process.env.ETHERSCAN_API_KEY || "";
const BASESCAN_API_KEY = process.env.BASESCAN_API_KEY || "";
const INFURA_API_KEY = process.env.INFURA_API_KEY || "";
const ALCHEMY_API_KEY = process.env.ALCHEMY_API_KEY || "";

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    // Mainnet networks
    ethereum: {
      url: `https://mainnet.infura.io/v3/${INFURA_API_KEY}`,
      accounts: [PRIVATE_KEY],
      chainId: 1
    },
    base: {
      url: `https://mainnet.base.org`,
      accounts: [PRIVATE_KEY],
      chainId: 8453,
      gasPrice: 1000000000 // 1 gwei
    },
    
    // Testnet networks
    sepolia: {
      url: `https://sepolia.infura.io/v3/${INFURA_API_KEY}`,
      accounts: [PRIVATE_KEY],
      chainId: 11155111
    },
    "base-sepolia": {
      url: `https://sepolia.base.org`,
      accounts: [PRIVATE_KEY],
      chainId: 84532,
      gasPrice: 1000000000 // 1 gwei
    },
    
    // Local development networks
    hardhat: {
      forking: {
        url: `https://mainnet.base.org`,
        blockNumber: 10000000
      }
    },
    localhost: {
      url: "http://127.0.0.1:8545"
    }
  },
  etherscan: {
    apiKey: {
      mainnet: ETHERSCAN_API_KEY,
      sepolia: ETHERSCAN_API_KEY,
      base: BASESCAN_API_KEY,
      "base-sepolia": BASESCAN_API_KEY
    },
    customChains: [
      {
        network: "base",
        chainId: 8453,
        urls: {
          apiURL: "https://api.basescan.org/api",
          browserURL: "https://basescan.org"
        }
      },
      {
        network: "base-sepolia",
        chainId: 84532,
        urls: {
          apiURL: "https://api-sepolia.basescan.org/api",
          browserURL: "https://sepolia.basescan.org"
        }
      }
    ]
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts"
  },
  mocha: {
    timeout: 40000
  }
};