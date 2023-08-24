// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./Interfaces/IERC20.sol";
import "./Interfaces/IERC4626.sol";
import "./ERC20.sol";

contract TokenVault is IERC4626, ERC20 {
    event Deposit(address caller, uint256 amounts);
    event Withdraw(
        address caller,
        address reciever,
        uint256 amount,
        uint256 shares
    );

    // Immutable ERC20 variable used as constructor
    ERC20 public immutable asset;

    // Mapping that checks when a user has deposited
    mapping(address => uint256) shareHolder;

    // Constructor assigns the asset variable to the underlying token
    constructor(
        ERC20 _underlying,
        string memory _name,
        string memory _symbol
    ) ERC20(_name, _symbol, 18) {
        asset = _underlying;
    }

    // deposit function recieves assets from users
    function deposit(uint256 assets) public {
        require(assets > 0, "You must deposit more than 0");
        asset.transferFrom(msg.sender, address(this), assets);
        shareHolder[msg.sender] += assets;
        _mint(msg.sender, assets);
        emit Deposit(msg.sender, assets);
    }

    // totalAssets function returns total number of assets
    function totalAssets() public view override returns (uint256) {
        return asset.balanceOf(address(this));
    }

    // redeem function checks whether a user has shares, and if the number of shares is > 0
    function redeem(
        uint256 shares,
        address receiver
    ) internal returns (uint256 assets) {
        require(shareHolder[msg.sender] > 0, "Not a shareholder");
        shareHolder[msg.sender] -= shares;
        uint256 per = (10 * shares) / 100;
        _burn(msg.sender, shares);
        assets = shares + per;
        emit Withdraw(msg.sender, receiver, assets, per);
        return assets;
    }

    // withdraw function allows msg.sender to withdraw his deposit plus interest
    function withdraw(uint256 shares, address receiver) public {
        uint256 payout = redeem(shares, receiver);
        asset.transfer(receiver, payout);
    }
}
