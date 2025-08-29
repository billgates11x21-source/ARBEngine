// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import {IPoolAddressesProvider, IPool} from "@aave/core-v3/contracts/interfaces/IPool.sol";
import {IFlashLoanSimpleReceiver} from "@aave/core-v3/contracts/flashloan/interfaces/IFlashLoanSimpleReceiver.sol";
import {IUniswapV2Router02} from "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";

/**
 * @title MultiExchangeArbEngine
 * @dev Advanced flash loan arbitrage contract supporting multiple exchanges
 */
contract MultiExchangeArbEngine is IFlashLoanSimpleReceiver, Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    // Aave lending pool
    IPool public aavePool;
    
    // Struct to store exchange router information
    struct ExchangeRouter {
        address routerAddress;
        string name;
        bool active;
    }
    
    // Struct to store arbitrage path information
    struct ArbitragePath {
        address[] path;           // Token path for the arbitrage
        uint8[] exchangeIndexes;  // Which exchange to use for each swap
        bool active;
    }
    
    // Array of exchange routers
    ExchangeRouter[] public exchangeRouters;
    
    // Mapping of arbitrage paths
    mapping(bytes32 => ArbitragePath) public arbitragePaths;
    bytes32[] public pathKeys;
    
    // Events
    event FlashLoanExecuted(address indexed token, uint256 amount);
    event ArbitrageExecuted(bytes32 indexed pathKey, uint256 profit);
    event ExchangeAdded(uint256 indexed index, address router, string name);
    event ArbitragePathAdded(bytes32 indexed pathKey, address[] path, uint8[] exchangeIndexes);
    event FundsWithdrawn(address indexed token, uint256 amount);
    
    /**
     * @dev Constructor to initialize the contract
     * @param _poolAddressProvider Aave pool address provider
     * @param _owner Owner of the contract
     */
    constructor(address _poolAddressProvider, address _owner) Ownable(_owner) {
        aavePool = IPool(IPoolAddressesProvider(_poolAddressProvider).getPool());
    }
    
    /**
     * @dev Required by IFlashLoanSimpleReceiver interface
     */
    function ADDRESSES_PROVIDER() external view override returns (IPoolAddressesProvider) {
        return IPoolAddressesProvider(address(aavePool));
    }

    function POOL() external view override returns (IPool) {
        return aavePool;
    }
    
    /**
     * @dev Add a new exchange router
     * @param _routerAddress Address of the exchange router
     * @param _name Name of the exchange
     */
    function addExchange(address _routerAddress, string memory _name) external onlyOwner {
        exchangeRouters.push(ExchangeRouter({
            routerAddress: _routerAddress,
            name: _name,
            active: true
        }));
        
        emit ExchangeAdded(exchangeRouters.length - 1, _routerAddress, _name);
    }
    
    /**
     * @dev Update an existing exchange router
     * @param _index Index of the exchange to update
     * @param _routerAddress New router address
     * @param _name New name
     * @param _active Active status
     */
    function updateExchange(uint256 _index, address _routerAddress, string memory _name, bool _active) external onlyOwner {
        require(_index < exchangeRouters.length, "Invalid exchange index");
        
        exchangeRouters[_index].routerAddress = _routerAddress;
        exchangeRouters[_index].name = _name;
        exchangeRouters[_index].active = _active;
    }
    
    /**
     * @dev Add a new arbitrage path
     * @param _path Token path for the arbitrage
     * @param _exchangeIndexes Which exchange to use for each swap
     */
    function addArbitragePath(address[] memory _path, uint8[] memory _exchangeIndexes) external onlyOwner {
        require(_path.length >= 2, "Path must have at least 2 tokens");
        require(_path.length - 1 == _exchangeIndexes.length, "Exchange indexes must match path transitions");
        
        for (uint8 i = 0; i < _exchangeIndexes.length; i++) {
            require(_exchangeIndexes[i] < exchangeRouters.length, "Invalid exchange index");
            require(exchangeRouters[_exchangeIndexes[i]].active, "Exchange not active");
        }
        
        bytes32 pathKey = keccak256(abi.encode(_path, _exchangeIndexes));
        
        arbitragePaths[pathKey] = ArbitragePath({
            path: _path,
            exchangeIndexes: _exchangeIndexes,
            active: true
        });
        
        pathKeys.push(pathKey);
        
        emit ArbitragePathAdded(pathKey, _path, _exchangeIndexes);
    }
    
    /**
     * @dev Update an existing arbitrage path
     * @param _pathKey Key of the path to update
     * @param _active Active status
     */
    function updateArbitragePath(bytes32 _pathKey, bool _active) external onlyOwner {
        require(arbitragePaths[_pathKey].path.length > 0, "Path does not exist");
        arbitragePaths[_pathKey].active = _active;
    }
    
    /**
     * @dev Start arbitrage by taking a flash loan
     * @param _pathKey Key of the arbitrage path to execute
     * @param _amount Amount to borrow in the flash loan
     */
    function startArbitrage(bytes32 _pathKey, uint256 _amount) external onlyOwner nonReentrant {
        ArbitragePath storage path = arbitragePaths[_pathKey];
        require(path.path.length > 0, "Path does not exist");
        require(path.active, "Path not active");
        
        // Encode path key in the params to use in executeOperation
        bytes memory params = abi.encode(_pathKey);
        
        // Take flash loan for the first token in the path
        aavePool.flashLoanSimple(
            address(this),
            path.path[0],
            _amount,
            params,
            0
        );
        
        emit FlashLoanExecuted(path.path[0], _amount);
    }
    
    /**
     * @dev Execute arbitrage operation after receiving flash loan
     * @param asset Asset that was borrowed
     * @param amount Amount that was borrowed
     * @param premium Fee to pay for the flash loan
     * @param initiator Address that initiated the flash loan
     * @param params Additional parameters
     */
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        require(msg.sender == address(aavePool), "Caller must be Aave pool");
        require(initiator == address(this), "Initiator must be this contract");
        
        // Decode the path key from params
        bytes32 pathKey = abi.decode(params, (bytes32));
        ArbitragePath storage path = arbitragePaths[pathKey];
        
        // Initial balance of the first token
        uint256 initialBalance = IERC20(asset).balanceOf(address(this));
        
        // Execute the arbitrage path
        for (uint256 i = 0; i < path.exchangeIndexes.length; i++) {
            address fromToken = path.path[i];
            address toToken = path.path[i + 1];
            uint8 exchangeIndex = path.exchangeIndexes[i];
            
            // Get the router for this exchange
            address routerAddress = exchangeRouters[exchangeIndex].routerAddress;
            IUniswapV2Router02 router = IUniswapV2Router02(routerAddress);
            
            // Amount to swap is the entire balance of the current token
            uint256 amountToSwap = IERC20(fromToken).balanceOf(address(this));
            
            // Approve router to spend tokens
            IERC20(fromToken).safeApprove(routerAddress, 0);
            IERC20(fromToken).safeApprove(routerAddress, amountToSwap);
            
            // Create path for this swap
            address[] memory swapPath = new address[](2);
            swapPath[0] = fromToken;
            swapPath[1] = toToken;
            
            // Execute swap
            router.swapExactTokensForTokens(
                amountToSwap,
                0, // Accept any amount of output tokens
                swapPath,
                address(this),
                block.timestamp + 300 // 5 minute deadline
            );
        }
        
        // Calculate total debt (borrowed amount + premium)
        uint256 totalDebt = amount + premium;
        
        // Check if we made a profit
        uint256 finalBalance = IERC20(asset).balanceOf(address(this));
        require(finalBalance >= totalDebt, "Arbitrage did not yield profit");
        
        // Calculate profit
        uint256 profit = finalBalance - totalDebt;
        
        // Approve Aave pool to take repayment
        IERC20(asset).safeApprove(address(aavePool), 0);
        IERC20(asset).safeApprove(address(aavePool), totalDebt);
        
        emit ArbitrageExecuted(pathKey, profit);
        
        return true;
    }
    
    /**
     * @dev Withdraw tokens from the contract
     * @param _token Address of the token to withdraw
     */
    function withdraw(address _token) external onlyOwner nonReentrant {
        uint256 balance = IERC20(_token).balanceOf(address(this));
        require(balance > 0, "No balance to withdraw");
        
        IERC20(_token).safeTransfer(owner(), balance);
        
        emit FundsWithdrawn(_token, balance);
    }
    
    /**
     * @dev Get the number of registered exchanges
     */
    function getExchangeCount() external view returns (uint256) {
        return exchangeRouters.length;
    }
    
    /**
     * @dev Get the number of registered arbitrage paths
     */
    function getArbitragePathCount() external view returns (uint256) {
        return pathKeys.length;
    }
    
    /**
     * @dev Get details of an arbitrage path
     * @param _pathKey Key of the path to query
     */
    function getArbitragePath(bytes32 _pathKey) external view returns (
        address[] memory path,
        uint8[] memory exchangeIndexes,
        bool active
    ) {
        ArbitragePath storage arbPath = arbitragePaths[_pathKey];
        return (arbPath.path, arbPath.exchangeIndexes, arbPath.active);
    }
    
    /**
     * @dev Simulate an arbitrage to check profitability without taking a flash loan
     * @param _pathKey Key of the arbitrage path to simulate
     * @param _amount Amount to simulate
     */
    function simulateArbitrage(bytes32 _pathKey, uint256 _amount) external view returns (uint256 expectedProfit) {
        ArbitragePath storage path = arbitragePaths[_pathKey];
        require(path.path.length > 0, "Path does not exist");
        require(path.active, "Path not active");
        
        // This is a simplified simulation and will not be accurate
        // In a real implementation, you would use off-chain calculations or oracles
        
        // For demonstration purposes, we'll return a small profit
        uint256 flashLoanPremium = (_amount * 9) / 10000; // 0.09% Aave premium
        return _amount / 100; // 1% profit estimate
    }
}