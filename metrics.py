"""
metrics.py  –  Entropy, Correlation, NPCR, UACI, PSNR
"""
import numpy as np
from scipy.stats import pearsonr


def information_entropy(image: np.ndarray) -> float:
    counts = np.bincount(image.flatten(), minlength=256)
    probs  = counts / counts.sum();  probs = probs[probs > 0]
    return float(-np.sum(probs * np.log2(probs)))


def _sample_pairs(ch, direction, n=5000):
    H, W = ch.shape;  rng = np.random.default_rng(0)
    if direction == 'horizontal':
        r=rng.integers(0,H,n); c=rng.integers(0,W-1,n); return ch[r,c], ch[r,c+1]
    elif direction == 'vertical':
        r=rng.integers(0,H-1,n); c=rng.integers(0,W,n); return ch[r,c], ch[r+1,c]
    else:
        r=rng.integers(0,H-1,n); c=rng.integers(0,W-1,n); return ch[r,c], ch[r+1,c+1]


def pixel_correlation(image: np.ndarray, direction='horizontal') -> float:
    channels = [image] if image.ndim == 2 else [image[:,:,c] for c in range(image.shape[2])]
    rs = [pearsonr(*[a.astype(float) for a in _sample_pairs(ch, direction)])[0] for ch in channels]
    return float(np.mean(rs))


def correlation_all_directions(image: np.ndarray) -> dict:
    return {d: pixel_correlation(image, d) for d in ('horizontal', 'vertical', 'diagonal')}


def npcr_uaci(img1: np.ndarray, img2: np.ndarray) -> tuple[float, float]:
    D    = (img1 != img2).astype(np.float64)
    npcr = 100.0 * D.sum() / D.size
    uaci = 100.0 * np.abs(img1.astype(float) - img2.astype(float)).sum() / (255.0 * D.size)
    return float(npcr), float(uaci)


def npcr_uaci_from_original(original, x0, r, arnold_iter):
    """
    Correct differential attack test:
      Encrypt original  →  enc1
      Flip 1 bit of pixel[0,0,0]  →  encrypt altered  →  enc2
      Compare enc1 vs enc2
    With double-pass diffusion this gives NPCR ≈ 99.6%, UACI ≈ 33.5%.
    """
    from chaotic_maps import arnold_cat_map_fast, logistic_key_stream, diffuse

    def _enc(img):
        s = arnold_cat_map_fast(img, iterations=arnold_iter)
        k = logistic_key_stream(x0, r, s.shape)
        return diffuse(s, k)

    enc1    = _enc(original)
    altered = original.copy();  altered[0, 0, 0] = int(altered[0, 0, 0]) ^ 1
    enc2    = _enc(altered)
    return npcr_uaci(enc1, enc2)


def psnr(original: np.ndarray, recovered: np.ndarray) -> float:
    mse = np.mean((original.astype(float) - recovered.astype(float)) ** 2)
    return float('inf') if mse == 0 else float(10 * np.log10(255**2 / mse))


def full_security_report(original, encrypted, decrypted, enc_time, dec_time, x0, r, arnold_iter):
    npcr_val, uaci_val = npcr_uaci_from_original(original, x0, r, arnold_iter)
    return {
        'entropy_original':  information_entropy(original),
        'entropy_encrypted': information_entropy(encrypted),
        'corr_original':     correlation_all_directions(original),
        'corr_encrypted':    correlation_all_directions(encrypted),
        'npcr':  npcr_val,
        'uaci':  uaci_val,
        'psnr':  psnr(original, decrypted),
        'enc_time_ms': enc_time * 1000,
        'dec_time_ms': dec_time * 1000,
    }
