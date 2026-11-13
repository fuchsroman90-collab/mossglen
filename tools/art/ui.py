"""Glossy UI pieces (9-slice capsules, round buttons, XP bar). numpy only, 2x resolution."""
from __future__ import annotations

import numpy as np

OUTLINE = np.array([0x4A, 0x32, 0x22], np.float32) / 255.0


def _sdf_round_rect(w, h, r):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    qx = np.abs(xx - w / 2) - (w / 2 - r)
    qy = np.abs(yy - h / 2) - (h / 2 - r)
    outside = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2)
    inside = np.minimum(np.maximum(qx, qy), 0)
    return outside + inside - r, yy / h


def _cov(d):
    return np.clip(0.5 - d, 0, 1)


def capsule(w, h, top, bottom, border=5.0, shadow=4.0, gloss=0.45) -> np.ndarray:
    """Rounded capsule with vertical gradient, dark border, top gloss and a drop shadow."""
    H = h + int(shadow) + 2
    r = h / 2 - 2
    d, ty = _sdf_round_rect(w, h, r)
    top_c = np.array(top, np.float32) / 255.0
    bot_c = np.array(bottom, np.float32) / 255.0
    fill = top_c + (bot_c - top_c) * ty[..., None]
    # gloss band in the upper half
    d_in = d + border + 2.0
    g = np.clip((0.48 - ty) * 6.0, 0, 1) * _cov(d_in + 1.5)
    fill = fill + (1.0 - fill) * (g * gloss)[..., None]
    col = np.where((d > -border)[..., None], OUTLINE, fill)
    a = _cov(d)
    out = np.zeros((H, w, 4), np.float32)
    # drop shadow
    sd, _ = _sdf_round_rect(w, h, r)
    out[int(shadow):int(shadow) + h, :, 3] = np.clip(0.5 - sd / 2.0, 0, 1) * 0.35
    out[int(shadow):int(shadow) + h, :, :3] = OUTLINE * 0.6
    # composite capsule over shadow
    base = out[:h]
    na = a + base[..., 3] * (1 - a)
    base[..., :3] = (col * a[..., None] + base[..., :3] * (base[..., 3] * (1 - a))[..., None]) / np.maximum(na, 1e-4)[..., None]
    base[..., 3] = na
    return out


def round_button(size, top, bottom, border=6.0) -> np.ndarray:
    return capsule(size, size, top, bottom, border=border, shadow=6.0, gloss=0.55)


def ui_sprites() -> dict:
    """name -> float RGBA image. Anchors are irrelevant for UI (centre)."""
    return {
        "ui_capsule": capsule(128, 76, (255, 251, 238), (240, 222, 182)),
        "ui_bar_back": capsule(128, 44, (120, 96, 70), (150, 122, 92), border=5.0, shadow=0.0, gloss=0.0),
        "ui_bar_fill": capsule(128, 34, (140, 226, 92), (72, 170, 48), border=0.0, shadow=0.0, gloss=0.5),
        "ui_btn_yellow": round_button(120, (255, 226, 92), (246, 168, 34)),
        "ui_btn_green": round_button(72, (150, 226, 96), (70, 168, 48), border=5.0),
        "ui_btn_cream": capsule(200, 84, (255, 251, 238), (236, 214, 170)),
    }
