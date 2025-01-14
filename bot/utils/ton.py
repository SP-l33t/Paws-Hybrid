import json
from os import path
from tonsdk.contract.wallet import Wallets, WalletVersionEnum


def generate_ton_wallet(config_path: str, wallets_path=None, existing_address=None):
    if existing_address:
        return {
            "mnemonic_phrase": "",
            "public_key": "",
            "private_key": "",
            "wallet_address": existing_address
        }

    mnemonics, public_key, private_key, wallet = Wallets.create(WalletVersionEnum.v4r2, workchain=0)
    wallet_address = wallet.address.to_string(True, True, False)
    wallet = {
        "mnemonic_phrase": " ".join(mnemonics),
        "public_key": public_key.hex(),
        "private_key": private_key.hex(),
        "wallet_address": wallet_address
    }
    if not wallets_path:
        wallets_path = path.join(path.dirname(config_path), 'wallets.txt')

    with open(wallets_path, "a+") as f:
        json.dump(wallet, f, indent=4)
        f.write('\n')

    return wallet
