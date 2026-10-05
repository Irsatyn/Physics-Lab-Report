"""Plot explicitly selected CSV columns. Adapt for the actual experiment."""
import argparse
import json
from pathlib import Path

import numpy as np


def calculate(x, y, fit=False):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if x.ndim != 1 or y.ndim != 1 or len(x) != len(y) or len(x) < 2:
        raise ValueError('Need at least two paired one-dimensional observations')
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError('Missing or non-finite measurements; resolve against the source')
    result = {'n': len(x), 'fit': bool(fit)}
    if fit:
        if len(x) < 3 or np.ptp(x) == 0:
            raise ValueError('Linear fit requires >=3 pairs and variable x')
        x_mean, y_mean = float(np.mean(x)), float(np.mean(y))
        centered_x, centered_y = x - x_mean, y - y_mean
        scale = float(np.max(np.abs(centered_x)))
        coefficients, _, rank, _ = np.linalg.lstsq(
            np.column_stack([centered_x / scale, np.ones(len(x))]), centered_y, rcond=None)
        if rank != 2 or not np.isfinite(coefficients).all():
            raise ValueError('Numerically singular fit; inspect input precision and units')
        slope = coefficients[0] / scale
        intercept = y_mean + coefficients[1] - slope * x_mean
        residuals = centered_y - (slope * centered_x + coefficients[1])
        sse = float(residuals @ residuals)
        sst = float(np.sum((y - np.mean(y)) ** 2))
        result.update(slope=float(slope), intercept=float(intercept),
                      x_reference=x_mean, y_at_reference=float(y_mean + coefficients[1]),
                      r_squared=None if sst == 0 else 1 - sse / sst,
                      residual_std=float(np.sqrt(sse / (len(x) - 2))))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--x', required=True)
    parser.add_argument('--y', required=True)
    parser.add_argument('--xlabel', required=True, help='Physical quantity and unit')
    parser.add_argument('--ylabel', required=True, help='Physical quantity and unit')
    parser.add_argument('--fit', action='store_true', help='Only when justified by the physical model')
    args = parser.parse_args()
    import csv
    with args.csv.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    x = np.array([float(r[args.x]) for r in rows])
    y = np.array([float(r[args.y]) for r in rows])
    result = calculate(x, y, args.fit)
    args.output.mkdir(parents=True, exist_ok=True)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['font.family'] = ['Times New Roman', 'SimSun']
    plt.rcParams['axes.unicode_minus'] = False
    fig, ax = plt.subplots(figsize=(6.4, 4.4), layout='constrained')
    ax.scatter(x, y, label='测量值')
    if args.fit:
        grid = np.linspace(x.min(), x.max(), 200)
        ax.plot(grid, result['slope'] * (grid-result['x_reference']) + result['y_at_reference'], label='线性拟合')
    ax.set(xlabel=args.xlabel, ylabel=args.ylabel)
    ax.grid(alpha=0.25)
    ax.legend()
    fig.savefig(args.output / 'data_plot.png', dpi=300)
    plt.close(fig)
    (args.output / 'results.json').write_text(json.dumps(result, indent=2, allow_nan=False), encoding='utf-8')


if __name__ == '__main__':
    main()
