"""Seamless ground textures (grass, dirt) and the soft blob shadow. numpy + Pillow only.

The textures live in grid space (top-down); the ground shader in Godot maps
them onto the dimetric view, so they read as a flat lawn.
"""
from __future__ import annotations

import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SIZE = 512  # covers TEX_CELLS grid cells (see ground.gdshader)


def periodic_noise(size, scale, seed):
    """Tileable smooth noise in [0, 1] (band-limited white noise via FFT)."""
    rng = np.random.default_rng(seed)
    white = rng.standard_normal((size, size))
    f = np.fft.fft2(white)
    ky = np.fft.fftfreq(size)[:, None]
    kx = np.fft.fftfreq(size)[None, :]
    k = np.sqrt(kx * kx + ky * ky)
    filt = np.exp(-(k * size / scale) ** 2)
    n = np.real(np.fft.ifft2(f * filt))
    n -= n.min()
    n /= max(n.max(), 1e-9)
    return n


def hexc(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0


def _wrap_draw(draw_fn, size):
    """Call draw_fn(dx, dy) for the 9 wrap offsets so strokes tile seamlessly."""
    for dx in (-size, 0, size):
        for dy in (-size, 0, size):
            draw_fn(dx, dy)


def grass(seed=3) -> Image.Image:
    rng = random.Random(seed)
    lo = periodic_noise(SIZE, 3.0, seed)
    mid = periodic_noise(SIZE, 14.0, seed + 1)
    light, base, dark = hexc("#A6D64B"), hexc("#8FC63E"), hexc("#74AE34")
    t = (0.55 * lo + 0.45 * mid)[..., None]
    rgb = np.where(t > 0.5, base + (light - base) * (t - 0.5) * 2.0, dark + (base - dark) * t * 2.0)
    img = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8), "RGB").convert("RGBA")

    # blade tufts: small fans of strokes, darker below, lighter tips
    layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    tufts = []
    for _ in range(1500):
        tufts.append((rng.uniform(0, SIZE), rng.uniform(0, SIZE), rng.uniform(3.0, 6.5), rng.random()))
    for x, y, h, v in tufts:
        def draw(dx, dy, x=x, y=y, h=h, v=v):
            col_dark = (84, 140, 40, 120) if v < 0.7 else (70, 122, 34, 140)
            col_light = (190, 228, 110, 150)
            for k in (-1, 0, 1):
                ang = k * 0.45 + rng.uniform(-0.15, 0.15)
                x2 = x + dx + math.sin(ang) * h
                y2 = y + dy - math.cos(ang) * h * 0.9
                d.line([(x + dx, y + dy), (x2, y2)], fill=col_dark, width=2)
                d.point((x2, y2), fill=col_light)
        _wrap_draw(draw, SIZE)
    # light flecks
    for _ in range(900):
        x, y = rng.uniform(0, SIZE), rng.uniform(0, SIZE)
        r = rng.uniform(0.8, 1.6)
        _wrap_draw(lambda dx, dy, x=x, y=y, r=r: d.ellipse(
            [x + dx - r, y + dy - r, x + dx + r, y + dy + r], fill=(206, 236, 130, 110)), SIZE)
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.35)))

    # alpha carries a tileable noise used by the shader for organic path edges
    edge = periodic_noise(SIZE, 18.0, seed + 7)
    arr = np.asarray(img).copy()
    arr[..., 3] = (edge * 255).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def dirt(seed=11) -> Image.Image:
    rng = random.Random(seed)
    lo = periodic_noise(SIZE, 4.0, seed)
    mid = periodic_noise(SIZE, 20.0, seed + 1)
    light, base, dark = hexc("#E9CB92"), hexc("#DDB87A"), hexc("#C59B5E")
    t = (0.5 * lo + 0.5 * mid)[..., None]
    rgb = np.where(t > 0.5, base + (light - base) * (t - 0.5) * 2.0, dark + (base - dark) * t * 2.0)
    img = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8), "RGB").convert("RGBA")
    layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(420):
        x, y = rng.uniform(0, SIZE), rng.uniform(0, SIZE)
        rx, ry = rng.uniform(1.5, 4.5), rng.uniform(1.2, 3.2)
        light_p = rng.random() < 0.6
        fill = (240, 220, 178, 200) if light_p else (176, 138, 88, 170)

        def draw(dx, dy, x=x, y=y, rx=rx, ry=ry, fill=fill, lp=light_p):
            if lp:  # pebble with a little shadow below
                d.ellipse([x + dx - rx, y + dy - ry + 1.2, x + dx + rx, y + dy + ry + 1.2], fill=(160, 120, 74, 120))
            d.ellipse([x + dx - rx, y + dy - ry, x + dx + rx, y + dy + ry], fill=fill)
        _wrap_draw(draw, SIZE)
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.4)))
    return img


def blob_shadow(w=120, h=56) -> np.ndarray:
    """Soft elliptical contact shadow for animals (float RGBA)."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (xx - w / 2 + 0.5) / (w / 2)
    ny = (yy - h / 2 + 0.5) / (h / 2)
    r = np.sqrt(nx * nx + ny * ny)
    a = np.clip(1.0 - r, 0, 1) ** 1.2 * 0.5
    rgb = np.broadcast_to(np.array([36, 58, 18], np.float32) / 255.0, (h, w, 3))
    return np.concatenate([rgb, a[..., None]], -1)
