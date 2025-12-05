
import base64
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

def generate_vapid_keys():
    # Generate private key
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    # Serialize private key to integer
    private_val = private_key.private_numbers().private_value
    private_bytes = private_val.to_bytes(32, byteorder='big')
    
    # Serialize public key to uncompressed point format (65 bytes)
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )

    # Encode to URL-safe Base64 without padding
    private_b64 = base64.urlsafe_b64encode(private_bytes).decode('utf-8').rstrip('=')
    public_b64 = base64.urlsafe_b64encode(public_bytes).decode('utf-8').rstrip('=')

    with open("temp_keys.txt", "w") as f:
        f.write(f"VAPID_PRIVATE_KEY={private_b64}\n")
        f.write(f"VAPID_PUBLIC_KEY={public_b64}\n")
    
    print("Keys written to temp_keys.txt")

if __name__ == "__main__":
    generate_vapid_keys()
