import json
from base58 import b58decode
from os import path
from solders.keypair import Keypair


def generate_sol_wallet(config_path: str, wallets_path=None):
    keypair = Keypair()
    wallet = {
        "public_key": str(keypair.pubkey()),
        "private_key": str(keypair),
        "wallet_address": str(keypair.pubkey())
    }
    if not wallets_path:
        wallets_path = path.join(path.dirname(config_path), 'sol_wallets.txt')

    with open(wallets_path, "a+") as f:
        json.dump(wallet, f, indent=4)
        f.write('\n')

    return wallet


def import_sol_wallet(private_key: str):
    return Keypair.from_bytes(b58decode(private_key))


def generate_sol_signature(keypair: Keypair, message):
    return keypair.sign_message(message)
