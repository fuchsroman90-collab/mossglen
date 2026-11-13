"""Post-process raw Blender renders into final sprite frames.

- soft ground shadow, tinted like darkened grass
- thin outline in a darkened version of the sprite's own edge colour
- trim to content, keep the anchor
Pure numpy/Pillow, runs without Blender.
"""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageFilter

SHADOW_RGB = np.array([36, 58, 18], np.float32) / 255.0
SHADOW_ALPHA = 0.55
OUTLINE_PX = 2.0
OUTLINE_DARKEN = 0.42
OUTLINE_ALPHA = 0.9


def _load(path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGBA"), np.float32) / 255.0


def _blur(a: np.ndarray, r: float) -> np.ndarray:
    im = Image.fromarray(np.clip(a * 255.0, 0, 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), np.float32) / 255.0


def _dilate(a: np.ndarray, r: float) -> np.ndarray:
    """Smooth dilation of an alpha mask by r pixels."""
    size = int(2 * np.ceil(r) + 1)
    im = Image.fromarray(np.clip(a * 255.0, 0, 255).astype(np.uint8))
    d = np.asarray(im.filter(ImageFilter.MaxFilter(size)), np.float32) / 255.0
    return np.maximum(_blur(d, 0.6), a)


def outline(rgba: np.ndarray, px: float = OUTLINE_PX) -> np.ndarray:
    a = rgba[..., 3]
    if px <= 0:
        return rgba
    # colour field that extends beyond the silhouette: blur premultiplied colour
    pre = rgba[..., :3] * a[..., None]
    k = px + 1.5
    bc = np.stack([_blur(pre[..., i], k) for i in range(3)], -1)
    ba = _blur(a, k)[..., None]
    near = bc / np.maximum(ba, 1e-4)
    ring_col = near * OUTLINE_DARKEN
    ring_col[..., 0] *= 1.05  # warm the dark edge slightly
    ring_a = _dilate(a, px) * OUTLINE_ALPHA
    # composite object over ring
    out_a = a + ring_a * (1.0 - a)
    out_rgb = (rgba[..., :3] * a[..., None] + ring_col * (ring_a * (1.0 - a))[..., None]) / np.maximum(out_a, 1e-4)[..., None]
    return np.concatenate([out_rgb, out_a[..., None]], -1)


def composite(obj_path, shadow_path=None, outline_px: float = OUTLINE_PX) -> np.ndarray:
    obj = outline(_load(obj_path), outline_px)
    if shadow_path is None:
        return obj
    sh = _load(shadow_path)[..., 3] * SHADOW_ALPHA
    a = obj[..., 3]
    out_a = a + sh * (1.0 - a)
    out_rgb = (obj[..., :3] * a[..., None] + SHADOW_RGB * (sh * (1.0 - a))[..., None]) / np.maximum(out_a, 1e-4)[..., None]
    return np.concatenate([out_rgb, out_a[..., None]], -1)


def trim(img: np.ndarray, ax: int, ay: int, pad: int = 1):
    """Crop to non-transparent content. Returns (image, new_ax, new_ay)."""
    a = img[..., 3]
    ys, xs = np.nonzero(a > 1.0 / 255.0)
    if len(xs) == 0:
        return img[:1, :1], 0, 0
    x0 = max(0, xs.min() - pad)
    y0 = max(0, ys.min() - pad)
    x1 = min(img.shape[1], xs.max() + 1 + pad)
    y1 = min(img.shape[0], ys.max() + 1 + pad)
    return img[y0:y1, x0:x1], ax - x0, ay - y0


def to_pil(img: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(img * 255.0 + 0.5, 0, 255).astype(np.uint8), "RGBA")
