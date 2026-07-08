# Image-Encryption-Using-Chaotic-Maps

A secure image encryption system combining **Arnold Cat Map** (confusion) and the **Logistic Map** (diffusion) — a hybrid chaos approach widely cited in the cryptography literature.

<img width="1537" height="412" alt="image" src="https://github.com/user-attachments/assets/f24edbea-52be-44e0-91ae-be7781db2803" />

---

## How It Works

```
Original Image
      ↓
Arnold Cat Map  ──────  Confusion (pixel position scrambling)
      ↓
Logistic Map + Double-pass Diffusion  ────  Diffusion (pixel value modification)
      ↓
Encrypted Image
```

Decryption is the exact reverse:

```
Encrypted Image
      ↓
Inverse double-pass diffusion (same Logistic key stream)
      ↓
Inverse Arnold Cat Map
      ↓
Original Image  (PSNR = ∞)
```

---

## Project Structure

```
ChaoticImageEncryption/
├── datasets/           # Input images (picture.png, etc.)
├── chaotic_maps.py     # Logistic Map + Arnold Cat Map implementations
├── encryption.py       # encrypt_image()
├── decryption.py       # decrypt_image()
├── metrics.py          # Entropy, Correlation, NPCR, UACI, PSNR
├── visualization.py    # All analysis plots
├── main.py             # CLI entry point
├── requirements.txt
└── results/
    ├── encrypted/      # {image_name}_encrypted.png
    ├── decrypted/      # {image_name}_decrypted.png
    └── analysis/       # {image_name}_pipeline.png, {image_name}_histograms.png, {image_name}_correlation.png, {image_name}_metrics_summary.png
```

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
# Default run (picture.png, default keys)
python main.py

# Custom image and secret key
python main.py --image datasets/image.png --x0 0.12345 --r 3.98765 --arnold-iter 30
```

| Argument | Default | Description |
|---|---|---|
| `--image` | `datasets/image.png` | Input image path |
| `--x0` | random | Logistic Map initial condition (auto-generated if omitted) |
| `--r` | random | Logistic Map control parameter 3.57 < r ≤ 4 (auto-generated if omitted) |
| `--arnold-iter` | `20` | Arnold Cat Map iterations |

> **Secret Key** = (x0, r, arnold_iter). A tiny change in any parameter produces a completely different encrypted image and makes decryption fail.

---

## Security Metrics

### Information Entropy
Measures how uniformly pixel values are distributed across 0–255. A perfectly random image has maximum entropy of **8.0 bits** — meaning every pixel value is equally likely and no information about the original image can be inferred. An acceptable encrypted image should achieve **≥ 7.9 bits**.

### Pixel Correlation
Measures the statistical relationship between adjacent pixels in three directions — horizontal, vertical, and diagonal. In a natural image, neighbouring pixels are almost always similar, giving a correlation close to **+1**. After encryption, this relationship should be completely destroyed, with correlation as close to **0** as possible. An acceptable value is **< 0.05** in all three directions.

### NPCR — Number of Pixel Change Rate
Measures resistance to differential attacks. It answers the question: if you flip a single bit in the original image and re-encrypt, what percentage of the encrypted image changes? Ideally, one tiny change in the plaintext should cascade through the entire ciphertext. An acceptable value is **> 99%**.

### UACI — Unified Average Changing Intensity
Companion to NPCR — where NPCR counts how many pixels changed, UACI measures how much they changed on average. A value too low means changes are subtle and detectable; a value too high means the distribution is skewed. The acceptable range is **between 30% and 36%**, with an ideal of approximately **33%**.

### PSNR — Peak Signal-to-Noise Ratio
Measures the quality of the decrypted image compared to the original. Unlike the other metrics which evaluate the encrypted image, PSNR evaluates the round-trip — it checks whether decryption recovers the original perfectly. An acceptable value is **∞ (infinity)**, which means zero error and not a single pixel was lost or altered during encryption and decryption.

---

## Chaotic Maps

### Logistic Map
```
x_{n+1} = r · x_n · (1 − x_n)
```
- Control parameter r ∈ (3.57, 4.0] → chaotic regime
- Used for **diffusion**: generates a pseudo-random key stream which is applied via double-pass modular diffusion (forward XOR + modular addition, then backward pass) for avalanche effect

### Arnold Cat Map
```
x' = (x + y)   mod N
y' = (x + 2y)  mod N
```
- Used for **confusion**: scrambles pixel positions
- Invertible, period-based — requires the same iteration count to reverse

---
