"""
visualization.py  –  Pipeline, Histograms, Correlation, Metrics, Bifurcation plots
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

P = {
    'bg': '#0d1117', 'panel': '#161b22', 'border': '#30363d',
    'a1': '#58a6ff', 'a2': '#3fb950', 'a3': '#f78166', 'a4': '#d2a8ff',
    'text': '#e6edf3', 'sub': '#8b949e',
}

def _style():
    plt.rcParams.update({
        'figure.facecolor': P['bg'], 'axes.facecolor': P['panel'],
        'axes.edgecolor': P['border'], 'axes.labelcolor': P['text'],
        'axes.titlecolor': P['text'], 'xtick.color': P['sub'],
        'ytick.color': P['sub'], 'text.color': P['text'],
        'grid.color': P['border'], 'grid.alpha': 0.5,
        'font.family': 'monospace', 'font.size': 9,
    })

def _borders(ax, col):
    for s in ax.spines.values():
        s.set_edgecolor(col); s.set_linewidth(2); s.set_visible(True)

def _dark_ax(ax):
    ax.set_facecolor(P['panel'])
    for s in ax.spines.values():
        s.set_edgecolor(P['border'])


def plot_pipeline(original, scrambled, encrypted, decrypted, save_path):
    _style()
    fig, axes = plt.subplots(1, 4, figsize=(16, 4.5))
    fig.patch.set_facecolor(P['bg'])
    titles  = ['Original', 'Scrambled\n(Arnold Cat Map)', 'Encrypted\n(XOR Diffusion)', 'Decrypted']
    images  = [original, scrambled, encrypted, decrypted]
    colors  = [P['a2'], P['a4'], P['a3'], P['a1']]
    for ax, img, title, col in zip(axes, images, titles, colors):
        ax.imshow(img);  ax.axis('off')
        ax.set_title(title, color=col, fontsize=10, fontweight='bold', pad=8)
        _borders(ax, col)
    fig.suptitle('Chaotic Image Encryption — Full Pipeline',
                 color=P['text'], fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor=P['bg'])
    plt.close();  print(f"[vis] Pipeline → {save_path}")


def plot_histograms(original, encrypted, save_path):
    _style()
    fig, axes = plt.subplots(2, 3, figsize=(14, 7))
    fig.patch.set_facecolor(P['bg'])
    fig.suptitle('Histogram Analysis — Original vs Encrypted',
                 color=P['text'], fontsize=12, fontweight='bold')
    ch_names  = ['Red', 'Green', 'Blue']
    ch_colors = [P['a3'], P['a2'], P['a1']]
    for c, (name, col) in enumerate(zip(ch_names, ch_colors)):
        for row, (img, label) in enumerate([(original,'Original'),(encrypted,'Encrypted')]):
            ax = axes[row, c]
            ax.hist(img[:,:,c].flatten(), bins=256, range=(0,255), color=col, alpha=0.85)
            ax.set_title(f'{label} – {name}', color=col, fontsize=9)
            ax.set_xlim(0, 255);  ax.grid(True, alpha=0.3)
            _dark_ax(ax)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor=P['bg'])
    plt.close();  print(f"[vis] Histograms → {save_path}")


def plot_correlation(original, encrypted, save_path):
    _style()
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    fig.patch.set_facecolor(P['bg'])
    fig.suptitle('Pixel Correlation — Original vs Encrypted',
                 color=P['text'], fontsize=12, fontweight='bold')
    directions = ['Horizontal', 'Vertical', 'Diagonal']
    rng = np.random.default_rng(42)

    def _pairs(ch, d, n=2000):
        H, W = ch.shape
        if d == 'Horizontal':
            r=rng.integers(0,H,n); c=rng.integers(0,W-1,n); return ch[r,c],ch[r,c+1]
        elif d == 'Vertical':
            r=rng.integers(0,H-1,n); c=rng.integers(0,W,n); return ch[r,c],ch[r+1,c]
        else:
            r=rng.integers(0,H-1,n); c=rng.integers(0,W-1,n); return ch[r,c],ch[r+1,c+1]

    for ci, d in enumerate(directions):
        og = original.mean(axis=2).astype(np.uint8)
        eg = encrypted.mean(axis=2).astype(np.uint8)
        for ri, (img_g, label, col) in enumerate([
            (og, f'Original {d}',  P['a2']),
            (eg, f'Encrypted {d}', P['a3']),
        ]):
            a, b = _pairs(img_g, d)
            corr = np.corrcoef(a, b)[0,1]
            ax = axes[ri, ci]
            ax.scatter(a, b, alpha=0.2, s=4, color=col)
            ax.set_title(f'{label}\nr = {corr:.4f}', color=col, fontsize=8.5, fontweight='bold')
            ax.set_xlabel('Pixel x', fontsize=7);  ax.set_ylabel('Pixel x+1', fontsize=7)
            ax.grid(True, alpha=0.25);  _dark_ax(ax)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor=P['bg'])
    plt.close();  print(f"[vis] Correlation → {save_path}")


def plot_metrics_summary(report, save_path):
    _style()
    fig = plt.figure(figsize=(13, 6))
    fig.patch.set_facecolor(P['bg'])
    fig.suptitle('Security Metrics Summary', color=P['text'], fontsize=13, fontweight='bold')
    gs = gridspec.GridSpec(1, 3, figure=fig, wspace=0.38)

    # Entropy
    ax1 = fig.add_subplot(gs[0])
    vals = [report['entropy_original'], report['entropy_encrypted']]
    bars = ax1.bar(['Original','Encrypted'], vals, color=[P['a2'],P['a3']], width=0.5, zorder=3)
    ax1.axhline(8.0, color=P['a1'], linestyle='--', linewidth=1.2, label='Ideal = 8.0')
    ax1.set_ylim(0, 8.5);  ax1.set_title('Information Entropy', color=P['text'], fontsize=10, fontweight='bold')
    ax1.set_ylabel('Bits', color=P['sub']);  ax1.grid(axis='y', alpha=0.3, zorder=0)
    ax1.legend(fontsize=8, facecolor=P['panel'], edgecolor=P['border'], labelcolor=P['text'])
    for bar, v in zip(bars, vals):
        ax1.text(bar.get_x()+bar.get_width()/2, v+0.05, f'{v:.4f}',
                 ha='center', va='bottom', color=P['text'], fontsize=8)
    _dark_ax(ax1)

    # Correlation
    ax2 = fig.add_subplot(gs[1])
    dirs = ['H','V','D']
    oc = [report['corr_original'][d]  for d in ('horizontal','vertical','diagonal')]
    ec = [report['corr_encrypted'][d] for d in ('horizontal','vertical','diagonal')]
    x  = np.arange(3);  w = 0.35
    ax2.bar(x-w/2, oc, w, label='Original',  color=P['a2'], zorder=3)
    ax2.bar(x+w/2, ec, w, label='Encrypted', color=P['a3'], zorder=3)
    ax2.set_xticks(x);  ax2.set_xticklabels(dirs)
    ax2.set_title('Pixel Correlation (H/V/D)', color=P['text'], fontsize=10, fontweight='bold')
    ax2.set_ylabel('Correlation Coefficient');  ax2.set_ylim(-0.15, 1.05)
    ax2.axhline(0, color=P['border'], linewidth=0.8)
    ax2.legend(fontsize=8, facecolor=P['panel'], edgecolor=P['border'], labelcolor=P['text'])
    ax2.grid(axis='y', alpha=0.3, zorder=0);  _dark_ax(ax2)

    # NPCR / UACI / PSNR
    ax3 = fig.add_subplot(gs[2])
    pv  = min(report['psnr'], 100) if report['psnr'] != float('inf') else 100
    mv  = [report['npcr'], report['uaci'], pv]
    ml  = ['NPCR (%)', 'UACI (%)', 'PSNR (dB)\n[cap 100]']
    mc  = [P['a1'], P['a4'], P['a2']]
    bars3 = ax3.bar(np.arange(3), mv, color=mc, width=0.5, zorder=3)
    ax3.set_xticks(np.arange(3));  ax3.set_xticklabels(ml, fontsize=7.5)
    ax3.set_title('Differential & Quality Metrics', color=P['text'], fontsize=10, fontweight='bold')
    ax3.set_ylim(0, 115);  ax3.grid(axis='y', alpha=0.3, zorder=0)
    for bar, val in zip(bars3, [report['npcr'], report['uaci'], report['psnr']]):
        label = '∞' if val == float('inf') else f'{val:.2f}'
        ax3.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1.5,
                 label, ha='center', va='bottom', color=P['text'], fontsize=8)
    _dark_ax(ax3)

    plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor=P['bg'])
    plt.close();  print(f"[vis] Metrics summary → {save_path}")