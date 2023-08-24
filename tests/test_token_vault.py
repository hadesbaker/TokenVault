import brownie
import pytest

# Import your TokenVault and ERC20 contracts
from brownie import TokenVault, ERC20, accounts

# Define test constants
NAME = "TestCoin"
SYMBOL = "TC"
DECIMALS = 18
INITIAL_SUPPLY = 1000000
INITIAL_BALANCE = 1000


@pytest.fixture
def setup():
    # Deploy the TokenVault and ERC20 contract
    deployer = accounts[0]
    erc20 = ERC20.deploy(NAME, SYMBOL, DECIMALS, {"from": deployer})
    token_vault = TokenVault.deploy(erc20, NAME, SYMBOL, {"from": deployer})

    # Mint some initial tokens and deposit into the vault for testing
    erc20._mint(deployer, INITIAL_SUPPLY, {"from": deployer})
    erc20.approve(token_vault, INITIAL_BALANCE, {"from": deployer})
    token_vault.deposit(INITIAL_BALANCE, {"from": deployer})

    yield erc20, token_vault, deployer


def test_deposit_and_balance(setup):
    erc20, token_vault, deployer = setup
    user = accounts[1]
    deposit_amount = 500

    # User deposits tokens
    erc20.approve(token_vault, deposit_amount, {"from": user})
    token_vault.deposit(deposit_amount, {"from": user})

    # Check user's balance in the vault
    user_balance_in_vault = token_vault.balanceOf(user)
    assert user_balance_in_vault == deposit_amount


def test_withdraw(setup):
    erc20, token_vault, deployer = setup
    user = accounts[1]
    deposit_amount = 500

    # User deposits tokens
    erc20.approve(token_vault, deposit_amount, {"from": user})
    token_vault.deposit(deposit_amount, {"from": user})

    # User withdraws tokens
    shares = token_vault.balanceOf(user)
    initial_user_balance = erc20.balanceOf(user)
    token_vault.withdraw(shares, user, {"from": user})

    # Check that the user received the correct amount of tokens
    final_user_balance = erc20.balanceOf(user)
    assert final_user_balance - initial_user_balance == deposit_amount


def test_redeem(setup):
    erc20, token_vault, deployer = setup
    user = accounts[1]
    deposit_amount = 500

    # User deposits tokens
    erc20.approve(token_vault, deposit_amount, {"from": user})
    token_vault.deposit(deposit_amount, {"from": user})

    # User redeems shares
    shares = token_vault.balanceOf(user)
    initial_user_balance = erc20.balanceOf(user)
    token_vault.redeem(shares, user, {"from": user})

    # Check that the user received the correct amount of tokens
    final_user_balance = erc20.balanceOf(user)
    assert final_user_balance - initial_user_balance == deposit_amount


def test_total_assets(setup):
    erc20, token_vault, deployer = setup

    # Check the total assets in the vault
    total_assets = token_vault.totalAssets()
    assert total_assets == INITIAL_BALANCE + INITIAL_SUPPLY


def test_invalid_withdraw(setup):
    erc20, token_vault, deployer = setup
    user = accounts[1]

    # Attempt an invalid withdraw with zero shares
    with brownie.reverts("Not a shareholder"):
        token_vault.withdraw(0, user, {"from": user})

    # Attempt an invalid withdraw with more shares than the user has
    with brownie.reverts("Not a shareholder"):
        token_vault.withdraw(10000, user, {"from": user})
