"""Tiny additive / physical-modelling synth used for all Mossglen audio."""
from __future__ import annotations

import numpy as np
from scipy.signal import butter, lfilter, sosfilt

SR = 44100
rng = np.random.default_rng(7)


def midi_hz(m: float) -> float:
    return 440.0 * 2 ** ((m - 69) / 12)


def t_axis(dur: float) -> np.ndarray:
    return np.arange(int(dur * SR)) / SR


def env_adsr(n: int, a=0.01, d=0.1, s=0.7, r=0.2) -> np.ndarray:
    t = np.arange(n) / SR
    dur = n / SR
    e = np.ones(n) * s
    e[t < a] = t[t < a] / max(a, 1e-4)
    m = (t >= a) & (t < a + d)
    e[m] = 1 - (1 - s) * (t[m] - a) / max(d, 1e-4)
    rel = t > dur - r
    e[rel] *= np.clip((dur - t[rel]) / max(r, 1e-4), 0, 1)
    return e


def lowpass(x, hz, order=2):
    sos = butter(order, hz, "low", fs=SR, output="sos")
    return sosfilt(sos, x)


def highpass(x, hz, order=2):
    sos = butter(order, hz, "high", fs=SR, output="sos")
    return sosfilt(sos, x)


def bandpass(x, lo, hi, order=2):
    sos = butter(order, [lo, hi], "band", fs=SR, output="sos")
    return sosfilt(sos, x)


# ---------------- instruments ----------------

def marimba(m: float, dur: float = 1.2, vel: float = 1.0) -> np.ndarray:
    f = midi_hz(m)
    t = t_axis(dur)
    partials = [(1.0, 1.0, 3.2), (3.93, 0.22, 9.0), (9.2, 0.05, 20.0)]
    y = sum(a * np.exp(-d * t) * np.sin(2 * np.pi * f * k * t) for k, a, d in partials if f * k < SR / 2)
    click = lowpass(rng.standard_normal(len(t)), 3000) * np.exp(-t * 300) * 0.15
    y = (y + click) * np.clip(t / 0.002, 0, 1)
    return y * vel


def pluck(m: float, dur: float = 1.5, vel: float = 1.0, bright: float = 0.5) -> np.ndarray:
    """Karplus-Strong string."""
    f = midi_hz(m)
    n = int(dur * SR)
    period = SR / f
    N = max(2, int(round(period - 0.5)))  # averaging filter adds half a sample of delay
    burst = np.zeros(n)
    burst[:N] = lowpass(rng.uniform(-1, 1, N), 1500 + 6000 * bright)
    decay = 0.996
    a = np.zeros(N + 2)
    a[0] = 1.0
    a[N] = -decay * 0.5
    a[N + 1] = -decay * 0.5
    y = lfilter([1.0], a, burst)
    y *= env_adsr(n, 0.001, 0.0, 1.0, 0.05)
    return y / (np.max(np.abs(y)) + 1e-9) * 0.8 * vel


def flute(m: float, dur: float, vel: float = 1.0) -> np.ndarray:
    f = midi_hz(m)
    t = t_axis(dur)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - 0.25) / 0.3, 0, 1)
    phase = 2 * np.pi * f * np.cumsum(vib) / SR
    y = np.sin(phase) + 0.18 * np.sin(2 * phase) + 0.05 * np.sin(3 * phase)
    breath = bandpass(rng.standard_normal(len(t)), f * 0.8, min(f * 3, 16000)) * 0.08
    y = (y + breath) * env_adsr(len(t), 0.06, 0.1, 0.85, min(0.15, dur / 3))
    return y * vel * 0.6


def pad(notes, dur: float, vel: float = 1.0) -> np.ndarray:
    t = t_axis(dur)
    y = np.zeros(len(t))
    for m in notes:
        f = midi_hz(m)
        for det in (-0.12, 0.0, 0.11):
            ff = f * 2 ** (det / 12)
            ph = rng.uniform(0, 2 * np.pi)
            y += np.sin(2 * np.pi * ff * t + ph) + 0.25 * np.sin(4 * np.pi * ff * t + ph)
    y = lowpass(y, 1800)
    y *= env_adsr(len(t), 0.7, 0.3, 0.8, 0.9)
    return y / (len(notes) * 3) * vel


def bell(m: float, dur: float = 2.0, vel: float = 1.0) -> np.ndarray:
    f = midi_hz(m)
    t = t_axis(dur)
    partials = [(1.0, 1.0, 2.0), (2.76, 0.35, 5.0), (5.4, 0.12, 9.0), (8.93, 0.05, 14.0)]
    y = sum(a * np.exp(-d * t) * np.sin(2 * np.pi * f * k * t) for k, a, d in partials if f * k < SR / 2)
    return y * np.clip(t / 0.001, 0, 1) * vel


def shaker(dur: float = 0.12, vel: float = 1.0) -> np.ndarray:
    t = t_axis(dur)
    y = highpass(rng.standard_normal(len(t)), 5000) * np.exp(-t * 40) * np.clip(t / 0.01, 0, 1)
    return y * vel * 0.25


# ---------------- effects ----------------

def comb(x, delay_s, fb):
    d = int(delay_s * SR)
    a = np.zeros(d + 1)
    a[0], a[d] = 1.0, -fb
    b = np.zeros(d + 1)
    b[d] = 1.0
    return lfilter(b, a, x)


def allpass(x, delay_s, g=0.5):
    d = int(delay_s * SR)
    b = np.zeros(d + 1)
    a = np.zeros(d + 1)
    b[0], b[d] = -g, 1.0
    a[0], a[d] = 1.0, -g
    return lfilter(b, a, x)


def reverb(x: np.ndarray, size: float = 0.8, damp_hz: float = 5000, spread: float = 0.0011) -> np.ndarray:
    """Schroeder reverb, returns the wet signal only."""
    delays = [0.0297, 0.0371, 0.0411, 0.0437, 0.0253, 0.0331]
    wet = sum(comb(x, d + spread, size) for d in delays) / len(delays)
    for d in (0.005, 0.0017):
        wet = allpass(wet, d)
    return lowpass(wet, damp_hz)


def place(buf: np.ndarray, sig: np.ndarray, at_s: float, gain: float = 1.0) -> None:
    i = max(0, int(at_s * SR))
    if i >= len(buf):
        return
    n = min(len(sig), len(buf) - i)
    buf[i:i + n] += sig[:n] * gain


def normalize(x: np.ndarray, peak: float = 0.89) -> np.ndarray:
    return x / (np.max(np.abs(x)) + 1e-9) * peak


def soft_limit(x: np.ndarray) -> np.ndarray:
    return np.tanh(x * 1.1) / np.tanh(1.1)
