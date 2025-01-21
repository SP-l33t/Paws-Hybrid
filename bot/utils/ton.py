import json
from time import time
from os import path
from base64 import b64encode
from hashlib import sha256

from nacl.signing import SigningKey
from tonsdk.contract.wallet import Wallets, WalletVersionEnum
from tonsdk.utils import bytes_to_b64str, Address


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


def generate_ton_proof_v2(mnemonic_string, domain, payload):
    mnemonics, public_key, private_key, wallet = Wallets.from_mnemonics(mnemonic_string.split(), WalletVersionEnum.v4r2, workchain=0)
    wallet_address = wallet.address.to_string(is_url_safe=True, is_user_friendly=False)

    ts = int(time())

    domain_bytes = domain.encode('utf-8')

    msg_bytes = b'ton-proof-item-v2/' + \
                int(wallet_address.split(':')[0]).to_bytes(4, 'big') + \
                wallet.address.hash_part + \
                len(domain_bytes).to_bytes(4, 'little') + \
                domain_bytes + \
                ts.to_bytes(8, 'little') + \
                (payload.encode('utf-8') if payload else b'')

    full_message = b"\xff\xff" + b'ton-connect' + sha256(msg_bytes).digest()
    signature = b64encode(SigningKey(private_key[:32]).sign(sha256(full_message).digest()).signature).decode('utf-8')

    return {
        "address": wallet_address,
        "network": "-239",
        "public_key": public_key.hex(),
        "proof": {
            "timestamp": ts,
            "domain": {
                "lengthBytes": len(domain_bytes),
                "value": domain
            },
            "signature": signature,
            "payload": payload,
            "state_init": bytes_to_b64str(wallet.create_state_init()["state_init"].to_boc(has_idx=False))
        }
    }


def hex_to_uf_address(address):
    return Address(address).to_string(is_user_friendly=True, is_url_safe=True)
