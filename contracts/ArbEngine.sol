// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {IPoolAddressesProvider, IPool} from "@aave/core-v3/contracts/interfaces/IPool.sol";
import {IFlashLoanSimpleReceiver} from "@aave/core-v3/contracts/flashloan/interfaces/IFlashLoanSimpleReceiver.sol";
import {IUniswapV2Router02} from "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";

contract ArbEngine is IFlashLoanSimpleReceiver {
    // Required by IFlashLoanSimpleReceiver
    function ADDRESSES_PROVIDER() external view override returns (IPoolAddressesProvider) {
        return IPoolAddressesProvider(address(aavePool));
    }

    function POOL() external view override returns (IPool) {
        return aavePool;
    }
    using SafeERC20 for IERC20;

    address public owner;
    IPool public aavePool;
    IUniswapV2Router02 public uniswapRouter;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    constructor(address _poolAddressProvider, address _uniswapRouter) {
        owner = msg.sender;
        aavePool = IPool(IPoolAddressesProvider(_poolAddressProvider).getPool());
        uniswapRouter = IUniswapV2Router02(_uniswapRouter);
    }

    function startArbitrage(address asset, uint256 amount) external onlyOwner {
        aavePool.flashLoanSimple(address(this), asset, amount, bytes(""), 0);
    }

    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata /* params */
    ) external override returns (bool) {
        require(msg.sender == address(aavePool), "Caller must be Aave pool");
        require(initiator == address(this), "Only self can initiate");

        address[] memory path = new address[](2);
        path[0] = asset;
        path[1] = uniswapRouter.WETH();

    IERC20(asset).approve(address(uniswapRouter), amount);
        uniswapRouter.swapExactTokensForTokens(
            amount,
            0,
            path,
            address(this),
            block.timestamp
        );

        uint256 totalDebt = amount + premium;
    IERC20(asset).approve(address(aavePool), totalDebt);

        return true;
    }

    function withdraw(address token) external onlyOwner {
        uint256 bal = IERC20(token).balanceOf(address(this));
        IERC20(token).safeTransfer(owner, bal);
    }
}
