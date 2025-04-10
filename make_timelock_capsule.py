import os
import qrcode
import base58
from ecdsa import SECP256k1, SigningKey
from hashlib import sha256

unlock_block = 1352460
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

def generate_keypair():
    sk = SigningKey.generate(curve=SECP256k1)
    vk = sk.get_verifying_key()
    priv_key_bytes = sk.to_string()
    pub_key_bytes = b'\x04' + vk.to_string()
    return priv_key_bytes, pub_key_bytes

def private_key_to_wif(priv_key_bytes):
    extended = b'\x80' + priv_key_bytes
    checksum = sha256(sha256(extended).digest()).digest()[:4]
    return base58.b58encode(extended + checksum).decode()

def pubkey_to_hash160(pubkey):
    sha = sha256(pubkey).digest()
    rip = sha256(sha).digest()  # Corrected to use double SHA256 for RIPEMD160
    return rip

def create_redeem_script_bytes(pubkey_hash, block_height):
    result = bytearray()
    # Push block height (as minimal encoding)
    if block_height < 17:
        result.append(0x50 + block_height)  # OP_1 .. OP_16
    else:
        height_bytes = block_height.to_bytes((block_height.bit_length() + 7) // 8, 'little')
        result.append(len(height_bytes))
        result += height_bytes
    result += bytes([
        0xb1,  # OP_CHECKLOCKTIMEVERIFY
        0x75,  # OP_DROP
        0x76,  # OP_DUP
        0xa9,  # OP_HASH160
        0x14  # push 20 bytes
    ])
    result += pubkey_hash
    result += bytes([
        0x88,  # OP_EQUALVERIFY
        0xac   # OP_CHECKSIG
    ])
    return bytes(result)

def redeem_script_to_p2sh_address(script_bytes):
    script_hash160 = sha256(sha256(script_bytes).digest()).digest()  # Corrected to use double SHA256 for RIPEMD160
    raw = b'\x05' + script_hash160
    checksum = sha256(sha256(raw).digest()).digest()[:4]
    return base58.b58encode(raw + checksum).decode()

def save_qr(data, path):
    img = qrcode.make(data)
    img.save(path)

def main():
    priv_key, pub_key = generate_keypair()
    wif = private_key_to_wif(priv_key)
    pub_hash = pubkey_to_hash160(pub_key)
    redeem_script_bytes = create_redeem_script_bytes(pub_hash, unlock_block)
    address = redeem_script_to_p2sh_address(redeem_script_bytes)

    with open(os.path.join(output_dir, "capsule_info.txt"), "w", encoding='utf-8') as f:
        f.write("🎁 Bitcoin Time Capsule\n")
        f.write("=========================\n")
        f.write(f"⏳ Unlock Block: {unlock_block}\n")
        f.write(f"📮 P2SH Address: {address}\n")
        f.write(f"🔑 Private Key (WIF): {wif}\n\n")
        f.write("🔐 Redeem Script (hex):\n{}\n".format(redeem_script_bytes.hex()))

    save_qr(address, os.path.join(output_dir, "p2sh_address_qr.png"))
    save_qr(wif, os.path.join(output_dir, "private_key_qr.png"))

    print("[✓] Капсула готова. Смотри папку output/")

if __name__ == "__main__":
    main()