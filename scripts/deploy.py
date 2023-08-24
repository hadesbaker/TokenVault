from scripts.helpful_scripts import get_account
from brownie import TokenVault, ERC20


def deploy():
    account = get_account()
    erc_20 = ERC20.deploy("TestCoin", "TC", 18, {"from": account})
    token_vault = TokenVault.deploy(erc_20, "TestCoin", "TC", {"from": account})


def main():
    deploy()
