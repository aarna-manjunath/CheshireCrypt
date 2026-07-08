"""
decryption.py
-------------
  1. Reverse double-pass diffusion
  2. Inverse Arnold Cat Map
"""
from pathlib import Path
from matplotlib.path import Path
import time
import numpy as np
import cv2
from chaotic_maps import inverse_arnold_cat_map, logistic_key_stream, undiffuse

def decrypt_image(encrypted_path, x0, r, arnold_iter=20, output_path=None):
    enc = cv2.imread(str(encrypted_path))
    if enc is None:
        raise FileNotFoundError(f"Cannot read: {encrypted_path}")
    enc = cv2.cvtColor(enc, cv2.COLOR_BGR2RGB)

    t0 = time.perf_counter()
    key_stream = logistic_key_stream(x0, r, enc.shape)
    unxored    = undiffuse(enc, key_stream)
    decrypted  = inverse_arnold_cat_map(unxored, iterations=arnold_iter)
    elapsed    = time.perf_counter() - t0

    if output_path:
        cv2.imwrite(str(output_path), cv2.cvtColor(decrypted, cv2.COLOR_RGB2BGR))
        print(f"[decrypt] Saved → {output_path}")
    return decrypted, elapsed

# ── CLI ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='Decrypt an image using Chaotic Maps')
    p.add_argument('image')
    p.add_argument('--output', '-o',   default=None, help='Output path (default: results/decrypted/{name}_decrypted.png)')    
    p.add_argument('--x0',             type=float, required=True)
    p.add_argument('--r',              type=float, required=True)
    p.add_argument('--arnold-iter',    type=int,   default=20)
    args = p.parse_args()

    if args.output is None:
        from pathlib import Path
        out_dir = Path('results/decrypted')
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(out_dir / f'{Path(args.image).stem}_decrypted.png')
    else:
        output_path = args.output

    print(f"\nDecrypting : {args.image}")
    print(f"Output     : {output_path}")
    print(f"Key        : x0={args.x0}, r={args.r}, arnold-iter={args.arnold_iter}")
    print("-" * 50)
    _, elapsed = decrypt_image(args.image, args.x0, args.r, args.arnold_iter, output_path)
    print(f"\nDecryption complete  ({elapsed*1000:.1f} ms)")