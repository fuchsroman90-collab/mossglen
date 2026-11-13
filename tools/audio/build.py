"""Compose and render Mossglen music + sound effects into game/audio/generated.

Usage:  python tools/audio/build.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.io import wavfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from synth import (SR, bandpass, bell, flute, highpass, lowpass, marimba, midi_hz, normalize, pad,  # noqa: E402
                   place, pluck, reverb, shaker, soft_limit, t_axis, env_adsr, rng)

OUT = HERE.parent.parent / "game" / "audio" / "generated"


def write(name: str, x: np.ndarray) -> None:
    x = np.clip(x, -1, 1)
    wavfile.write(OUT / f"{name}.wav", SR, (x * 32767).astype(np.int16))
    ch = "stereo" if x.ndim == 2 else "mono"
    print(f"{name}.wav  {x.shape[0] / SR:5.2f}s {ch}")


# ---------------------------------------------------------------- music

N = {n: i for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "Bb", "B"])}


def note(s: str) -> int:
    """'A4' -> midi"""
    return 12 * (int(s[-1]) + 1) + N[s[:-1]]


# Key F major, 84 BPM, 16 bars (A: bars 1-8, B: bars 9-16)
CHORDS = {
    "Fmaj7": ([53, 57, 60, 64], 41), "Am7": ([52, 55, 57, 60], 45), "Bbmaj7": ([53, 57, 58, 62], 46),
    "C": ([52, 55, 60, 64], 48), "Dm7": ([53, 57, 60, 62], 38), "Gm7": ([53, 55, 58, 62], 43),
    "C7": ([52, 55, 58, 60], 48), "F": ([53, 57, 60, 65], 41),
}
PROG = ["Fmaj7", "Am7", "Bbmaj7", "C", "Fmaj7", "Dm7", "Gm7", "C7",
        "Bbmaj7", "C", "Am7", "Dm7", "Gm7", "C", "F", "C7"]

# melody: per bar list of (beat, length in beats, note)
MELODY = [
    [(0, 1, "A4"), (1, 1, "C5"), (2, 1.5, "E5"), (3.5, .5, "D5")],
    [(0, 1.5, "C5"), (1.5, .5, "A4"), (2, 1, "E5"), (3, 1, "C5")],
    [(0, 1, "D5"), (1, 1, "F5"), (2, 1.5, "A5"), (3.5, .5, "G5")],
    [(0, 1, "G5"), (1, 1, "E5"), (2, 2, "D5")],
    [(0, 1, "A4"), (1, 1, "C5"), (2, 1.5, "F5"), (3.5, .5, "E5")],
    [(0, 1, "D5"), (1, 1, "F5"), (2, 2, "A5")],
    [(0, 1, "G5"), (1, .5, "F5"), (1.5, .5, "D5"), (2, 1, "Bb4"), (3, 1, "D5")],
    [(0, 1.5, "C5"), (1.5, .5, "D5"), (2, 2, "E5")],
    [(0, 1.5, "F5"), (1.5, .5, "D5"), (2, 1, "F5"), (3, 1, "A5")],
    [(0, 3, "G5"), (3, 1, "E5")],
    [(0, 1.5, "E5"), (1.5, .5, "C5"), (2, 1, "E5"), (3, 1, "G5")],
    [(0, 2, "F5"), (2, 2, "D5")],
    [(0, 1, "D5"), (1, 1, "G5"), (2, 1.5, "Bb5"), (3.5, .5, "A5")],
    [(0, 1.5, "G5"), (1.5, .5, "F5"), (2, 1, "E5"), (3, 1, "D5")],
    [(0, 1, "C5"), (1, 1, "F5"), (2, 2, "A5")],
    [(0, 1, "G5"), (1, 1, "E5"), (2, 2, "C5")],
]
ARP = [0, 1, 2, 3, 2, 1, 2, 3]


def humanize(t: float) -> float:
    return t + rng.normal(0, 0.006)


def compose_meadow(bpm: float = 84.0) -> np.ndarray:
    beat = 60.0 / bpm
    bar = beat * 4
    loop_len = bar * len(PROG)
    tail = 5.0
    n = int((loop_len + tail) * SR)
    dry_l, dry_r = np.zeros(n), np.zeros(n)
    send = np.zeros(n)

    def put(sig, at, gain, pan=0.0, rev=0.3):
        l, r = gain * (1 - pan) / 1.0, gain * (1 + pan) / 1.0
        place(dry_l, sig, at, l * 0.5)
        place(dry_r, sig, at, r * 0.5)
        place(send, sig, at, gain * rev)

    for b, cname in enumerate(PROG):
        voicing, root = CHORDS[cname]
        t0 = b * bar
        section_b = b >= 8
        # pad
        put(pad(voicing, bar + 0.6), t0, 0.55, 0.0, 0.5)
        # bass pluck
        put(pluck(root, beat * 2.2, 0.9, bright=0.15), humanize(t0), 0.55, -0.1, 0.1)
        put(pluck(root + 7, beat * 1.2, 0.7, bright=0.15), humanize(t0 + 2 * beat), 0.45, -0.1, 0.1)
        put(pluck(root + 12, beat * 1.2, 0.6, bright=0.15), humanize(t0 + 3 * beat), 0.4, -0.1, 0.1)
        # broken chord arpeggio (guitar in A, soft marimba in B)
        for k, idx in enumerate(ARP):
            m = voicing[idx] + 12
            at = humanize(t0 + k * beat / 2)
            vel = 0.75 if k % 2 == 0 else 0.55
            if section_b:
                put(marimba(m, 0.9, vel), at, 0.28, 0.35, 0.35)
            else:
                put(pluck(m, 1.2, vel, bright=0.55), at, 0.3, 0.35, 0.3)
        # melody
        for beat_pos, length, nm in MELODY[b]:
            m = note(nm)
            at = humanize(t0 + beat_pos * beat)
            if section_b:
                put(flute(m, length * beat * 0.98 + 0.1), at, 0.42, -0.2, 0.45)
            else:
                put(marimba(m, max(0.8, length * beat + 0.4), 0.95), at, 0.5, -0.2, 0.4)
        # sparkle bell every 4 bars
        if b % 4 == 0:
            put(bell(voicing[-1] + 24, 2.5, 0.5), t0 + beat * 0.02, 0.12, 0.5, 0.7)
        # shaker in B section
        if section_b:
            for k in range(8):
                put(shaker(0.1, 0.9 if k % 2 else 0.5), humanize(t0 + k * beat / 2), 0.5, 0.25, 0.1)

    wet_l = reverb(send, 0.82, 5200, 0.0)
    wet_r = reverb(send, 0.82, 5200, 0.0011)
    left = dry_l + wet_l * 0.55
    right = dry_r + wet_r * 0.55
    st = np.stack([left, right], axis=1)
    # wrap the tail into the start for a seamless loop
    L = int(loop_len * SR)
    out = st[:L].copy()
    out[:n - L] += st[L:]
    out = highpass(out.T, 30).T
    return soft_limit(normalize(out, 0.8))


# ---------------------------------------------------------------- sfx

def sfx_click():
    t = t_axis(0.08)
    y = np.sin(2 * np.pi * 1320 * t) * np.exp(-t * 70) + 0.4 * np.sin(2 * np.pi * 2640 * t) * np.exp(-t * 120)
    return normalize(y, 0.5)


def sfx_pop():
    t = t_axis(0.18)
    f = 300 + 900 * (1 - np.exp(-t * 40))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22) * np.clip(t / 0.003, 0, 1)
    return normalize(y, 0.6)


def sfx_plant():
    t = t_axis(0.3)
    thud = np.sin(2 * np.pi * np.cumsum(180 - 90 * t / 0.3) / SR) * np.exp(-t * 25)
    dirt = bandpass(rng.standard_normal(len(t)), 300, 2500) * np.exp(-t * 30) * 0.5
    sprout = np.zeros(len(t))
    place(sprout, marimba(77, 0.25, 0.4), 0.05)
    return normalize(thud + dirt + sprout, 0.6)


def sfx_harvest():
    t = t_axis(0.45)
    swish_env = np.exp(-((t - 0.08) / 0.05) ** 2)
    swish = bandpass(rng.standard_normal(len(t)), 1500, 7000) * swish_env * 0.6
    y = swish.copy()
    place(y, marimba(72, 0.35, 0.7), 0.1)
    place(y, marimba(79, 0.35, 0.6), 0.16)
    return normalize(y, 0.65)


def sfx_coin():
    y = np.zeros(int(0.7 * SR))
    place(y, bell(88, 0.6, 0.8), 0.0)
    place(y, bell(93, 0.6, 1.0), 0.07)
    return normalize(y, 0.55)


def sfx_cluck():
    y = np.zeros(int(0.45 * SR))
    for at, f0, d in ((0.0, 520, 0.09), (0.14, 610, 0.12)):
        t = t_axis(d)
        f = f0 * (1 + 0.4 * np.sin(np.pi * t / d))
        saw = 2 * ((np.cumsum(f) / SR) % 1.0) - 1
        voice = bandpass(saw, 700, 2600) + 0.5 * bandpass(saw, 2800, 4200)
        voice *= np.sin(np.pi * t / d) ** 0.6
        place(y, voice, at)
    return normalize(lowpass(y, 5000), 0.45)


def sfx_whoosh():
    t = t_axis(0.35)
    noise = rng.standard_normal(len(t))
    env = np.sin(np.pi * t / 0.35) ** 2
    y = bandpass(noise, 600, 3000) * env
    return normalize(y, 0.35)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write("music_meadow", compose_meadow())
    for name, fn in [("sfx_click", sfx_click), ("sfx_pop", sfx_pop), ("sfx_plant", sfx_plant),
                     ("sfx_harvest", sfx_harvest), ("sfx_coin", sfx_coin), ("sfx_cluck", sfx_cluck),
                     ("sfx_whoosh", sfx_whoosh)]:
        write(name, fn())


if __name__ == "__main__":
    main()
