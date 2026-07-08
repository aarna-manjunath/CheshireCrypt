"""
analyze.py: Standalone security analysis

Usage:
    # With decrypted image (enables PSNR)
    python analyze.py datasets/lena.png results/encrypted/encrypted.png \
           --decrypted results/decrypted/decrypted.png \
           --x0 0.56789 --r 3.99991

    # Without decrypted image
    python analyze.py datasets/lena.png results/encrypted/encrypted.png \
           --x0 0.56789 --r 3.99991
"""
import argparse, sys
from pathlib import Path
import numpy as np
import cv2

from metrics import (information_entropy, correlation_all_directions, npcr_uaci_from_original, psnr)
from visualization import (plot_histograms, plot_correlation, plot_metrics_summary, plot_logistic_bifurcation)

def load(path):
    img = cv2.imread(str(path))
    if img is None:
        print(f"[error] Cannot read: {path}"); sys.exit(1)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def run_analysis(original, encrypted, decrypted, x0, r, arnold_iter, out_dir):
    out_dir = Path(out_dir);  out_dir.mkdir(parents=True, exist_ok=True)

    ent_orig  = information_entropy(original)
    ent_enc   = information_entropy(encrypted)
    corr_orig = correlation_all_directions(original)
    corr_enc  = correlation_all_directions(encrypted)

    print("Computing NPCR/UACI (re-encrypts a 1-bit-altered copy) …")
    npcr_val, uaci_val = npcr_uaci_from_original(original, x0, r, arnold_iter)
    psnr_val = psnr(original, decrypted) if decrypted is not None else None

    print("\n" + "=" * 54)
    print("           SECURITY ANALYSIS REPORT")
    print("=" * 54)
    print(f"  Entropy (original)         : {ent_orig:.4f} bits")
    print(f"  Entropy (encrypted)        : {ent_enc:.4f} bits  {'✓' if ent_enc > 7.9 else '✗ (ideal >7.9)'}")
    print("-" * 54)
    for d in ('horizontal', 'vertical', 'diagonal'):
        ov, ev = corr_orig[d], corr_enc[d]
        ok = '✓' if abs(ev) < 0.05 else '✗ (ideal ≈0)'
        print(f"  Corr {d[0].upper()} (original)          : {ov:+.4f}")
        print(f"  Corr {d[0].upper()} (encrypted)         : {ev:+.4f}  {ok}")
    print("-" * 54)
    print(f"  NPCR                       : {npcr_val:.4f} %  {'✓' if npcr_val > 99 else '✗ (ideal >99%)'}")
    print(f"  UACI                       : {uaci_val:.4f} %  {'✓' if 30 < uaci_val < 36 else '✗ (ideal ≈33%)'}")
    print("-" * 54)
    if psnr_val is not None:
        ps = '∞' if psnr_val == float('inf') else f'{psnr_val:.2f} dB'
        ok = '✓ perfect reconstruction' if (psnr_val == float('inf') or psnr_val > 60) else '✗ key mismatch?'
        print(f"  PSNR (original/decrypted)  : {ps}  {ok}")
    else:
        print("  PSNR                       : N/A (--decrypted not provided)")
    print("=" * 54)

    report = {
        'entropy_original': ent_orig, 'entropy_encrypted': ent_enc,
        'corr_original': corr_orig,   'corr_encrypted': corr_enc,
        'npcr': npcr_val, 'uaci': uaci_val,
        'psnr': psnr_val if psnr_val is not None else float('inf'),
        'enc_time_ms': 0, 'dec_time_ms': 0,
    }
    print("\nGenerating plots …")
    plot_histograms(original, encrypted,  out_dir / 'histograms.png')
    plot_correlation(original, encrypted, out_dir / 'correlation.png')
    plot_metrics_summary(report,          out_dir / 'metrics_summary.png')
    plot_logistic_bifurcation(            out_dir / 'bifurcation.png')
    print(f"\nAll plots saved to: {out_dir}/")


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Security analysis for Chaotic Image Encryption',
                                formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument('original')
    p.add_argument('encrypted')
    p.add_argument('--decrypted', '-d', default=None)
    p.add_argument('--x0',              type=float, required=True)
    p.add_argument('--r',               type=float, required=True)
    p.add_argument('--arnold-iter',     type=int,   default=20)
    p.add_argument('--out-dir', '-o',   default='results/analysis')
    args = p.parse_args()

    print(f"Original  : {args.original}")
    print(f"Encrypted : {args.encrypted}")
    if args.decrypted: print(f"Decrypted : {args.decrypted}")

    orig = load(args.original);  enc = load(args.encrypted)
    N = min(orig.shape[:2]);  orig = orig[:N,:N];  enc = enc[:N,:N]
    dec = load(args.decrypted)[:N,:N] if args.decrypted else None

    run_analysis(orig, enc, dec, args.x0, args.r, args.arnold_iter, args.out_dir)
