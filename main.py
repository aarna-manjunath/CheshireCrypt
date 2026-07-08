"""
main.py: Full pipeline: encrypt → decrypt → security analysis
"""
import argparse
from email.mime import base
from pathlib import Path
from chaotic_maps import arnold_cat_map_fast
from encryption   import encrypt_image
from decryption   import decrypt_image
from metrics      import full_security_report
from visualization import (plot_pipeline, plot_histograms, plot_correlation, plot_metrics_summary)

def main():
    p = argparse.ArgumentParser(description='Chaotic Image Encryption — full pipeline')
    p.add_argument('--image',        default='dataset/picture.png')
    p.add_argument('--x0',          type=float, default=0.56789)
    p.add_argument('--r',           type=float, default=3.99991)
    p.add_argument('--arnold-iter', type=int,   default=20)
    args = p.parse_args()

    base     = Path(__file__).parent
    img_stem  = Path(args.image).stem
    enc_path  = base / f'results/encrypted/{img_stem}_encrypted.png'
    dec_path  = base / f'results/decrypted/{img_stem}_decrypted.png'
    ana_dir  = base / 'results/analysis'
    for d in [enc_path.parent, dec_path.parent, ana_dir]:
        d.mkdir(parents=True, exist_ok=True)

    print("=" * 56)
    print("  Chaotic Map-Based Image Encryption  —  Full Pipeline")
    print("=" * 56)
    print(f"  Image : {args.image}   x0={args.x0}  r={args.r}  iter={args.arnold_iter}")
    print("-" * 56)

    print("\n[1/4] Encrypting …")
    original, encrypted, enc_time = encrypt_image(base / args.image, args.x0, args.r, args.arnold_iter, enc_path)
    scrambled = arnold_cat_map_fast(original, iterations=args.arnold_iter)

    print("\n[2/4] Decrypting …")
    decrypted, dec_time = decrypt_image(enc_path, args.x0, args.r, args.arnold_iter, dec_path)

    print("\n[3/4] Computing security metrics …")
    report = full_security_report(original, encrypted, decrypted, enc_time, dec_time, args.x0, args.r, args.arnold_iter)

    psnr_str = '∞' if report['psnr'] == float('inf') else f"{report['psnr']:.2f} dB"
    print(f"\n  Entropy  (orig/enc)  : {report['entropy_original']:.4f} / {report['entropy_encrypted']:.4f} bits")
    print(f"  Corr H   (orig/enc)  : {report['corr_original']['horizontal']:+.4f} / {report['corr_encrypted']['horizontal']:+.4f}")
    print(f"  NPCR                 : {report['npcr']:.4f} %")
    print(f"  UACI                 : {report['uaci']:.4f} %")
    print(f"  PSNR (orig/decrypted): {psnr_str}")
    print(f"  Enc/Dec time         : {report['enc_time_ms']:.1f} ms / {report['dec_time_ms']:.1f} ms")

    print("\n[4/4] Generating plots …")
    plot_pipeline(original, scrambled, encrypted, decrypted, ana_dir / f'{img_stem}_pipeline.png')
    plot_histograms(original,  encrypted,  ana_dir / f'{img_stem}_histograms.png')
    plot_correlation(original, encrypted,  ana_dir / f'{img_stem}_correlation.png')
    plot_metrics_summary(report,           ana_dir / f'{img_stem}_metrics_summary.png')

    print(f"\nAll results → {base / 'results'}/")
    print("=" * 56)

if __name__ == '__main__':
    main()