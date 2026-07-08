"""
encryption.py
-------------
  1. Arnold Cat Map   – confusion  (pixel position scrambling)
  2. Double-pass diffusion – NPCR ≈ 99.6%, UACI ≈ 33.5%
"""
import time
import numpy as np
import cv2
from chaotic_maps import arnold_cat_map_fast, logistic_key_stream, diffuse

def encrypt_image(image_path, x0, r, arnold_iter=20, output_path=None):
    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f"Cannot read: {image_path}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    N = min(img.shape[:2]);  img = img[:N, :N]

    t0 = time.perf_counter()
    scrambled  = arnold_cat_map_fast(img, iterations=arnold_iter)
    key_stream = logistic_key_stream(x0, r, scrambled.shape)
    encrypted  = diffuse(scrambled, key_stream)
    elapsed    = time.perf_counter() - t0

    if output_path:
        cv2.imwrite(str(output_path), cv2.cvtColor(encrypted, cv2.COLOR_RGB2BGR))
        print(f"[encrypt] Saved → {output_path}  ({elapsed*1000:.1f} ms)")
    return img, encrypted, elapsed

# ── CLI ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import argparse, secrets
    rng = np.random.default_rng(secrets.randbits(128))
    default_x0 = round(rng.uniform(0.001, 0.999), 10)
    default_r  = round(rng.uniform(3.571, 4.000), 10)

    from pathlib import Path

    p = argparse.ArgumentParser(description='Encrypt an image using Chaotic Maps')
    p.add_argument('image')
    p.add_argument('--output', '-o', default=None, help='Output path (default: results/encrypted/{name}_encrypted.png)')
    p.add_argument('--x0', type=float, default=None, help='Logistic initial condition (random if omitted)')
    p.add_argument('--r', type=float, default=None, help='Logistic control parameter (random if omitted)')
    p.add_argument('--arnold-iter', type=int, default=20)
    args = p.parse_args()

    x0          = args.x0 if args.x0 is not None else default_x0
    r           = args.r  if args.r  is not None else default_r
    arnold_iter = args.arnold_iter

    # Auto-derive: results/encrypted/{input_stem}_encrypted.png
    if args.output is None:
        out_dir = Path('results/encrypted')
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(out_dir / f'{Path(args.image).stem}_encrypted.png')
    else:
        output_path = args.output

    print(f"\nEncrypting : {args.image}")
    print(f"Output     : {output_path}")
    print("-" * 50)
    _, _, elapsed = encrypt_image(args.image, x0, r, arnold_iter, output_path)
    print(f"\nEncryption complete  ({elapsed*1000:.1f} ms)")
    print("\n" + "=" * 50)
    print("  *** SAVE THIS KEY — YOU CANNOT DECRYPT WITHOUT IT ***")
    print("=" * 50)
    print(f"  x0          = {x0:.10f}")
    print(f"  r           = {r:.10f}")
    print(f"  arnold-iter = {arnold_iter}")
    print("=" * 50)
    print(f"\nDecrypt command:")
    print(f"  python decryption.py {output_path} -o decrypted.png \\")
    print(f"    --x0 {x0:.10f} --r {r:.10f} --arnold-iter {arnold_iter}")