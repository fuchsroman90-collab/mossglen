"""Additional Mossglen music loops: night, village, primeval vale.

Every song is a 16 bar loop described as data (chords, progression, melody)
plus a small arrangement function. The reverb tail is folded back into the
start so the loop is seamless.
"""
from __future__ import annotations

import numpy as np

from synth import (SR, bandpass, bell, flute, highpass, lowpass, marimba, normalize, pad, place, pluck,
                   reverb, rng, shaker, soft_limit, t_axis)

_N = {n: i for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "Bb", "B"])}
_N.update({"Eb": 3, "Ab": 8, "Db": 1, "Gb": 6})


def note(s: str) -> int:
    return 12 * (int(s[-1]) + 1) + _N[s[:-1]]


def hum(t: float, amount: float = 0.006) -> float:
    return t + rng.normal(0, amount)


def thump(dur: float = 0.5, vel: float = 1.0) -> np.ndarray:
    """Soft low frame drum."""
    t = t_axis(dur)
    f = 70 + 50 * np.exp(-t * 30)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    skin = lowpass(rng.standard_normal(len(t)), 900) * np.exp(-t * 60) * 0.25
    return (body + skin) * np.clip(t / 0.003, 0, 1) * vel * 0.7


def woodblock(dur: float = 0.15, vel: float = 1.0) -> np.ndarray:
    t = t_axis(dur)
    y = np.sin(2 * np.pi * 1250 * t) * np.exp(-t * 55) + 0.4 * np.sin(2 * np.pi * 2380 * t) * np.exp(-t * 80)
    return y * vel * 0.35


class Mix:
    def __init__(self, loop_len: float, tail: float = 5.0):
        self.loop_len = loop_len
        n = int((loop_len + tail) * SR)
        self.l, self.r, self.send = np.zeros(n), np.zeros(n), np.zeros(n)

    def put(self, sig, at, gain, pan=0.0, rev=0.3):
        place(self.l, sig, at, gain * (1 - pan) * 0.5)
        place(self.r, sig, at, gain * (1 + pan) * 0.5)
        place(self.send, sig, at, gain * rev)

    def render(self, size=0.82, damp=5200, wet=0.55, peak=0.8) -> np.ndarray:
        left = self.l + reverb(self.send, size, damp, 0.0) * wet
        right = self.r + reverb(self.send, size, damp, 0.0011) * wet
        st = np.stack([left, right], axis=1)
        L = int(self.loop_len * SR)
        out = st[:L].copy()
        out[:len(st) - L] += st[L:]
        out = highpass(out.T, 30).T
        return soft_limit(normalize(out, peak))


def _melody(rows):
    return [[(b, ln, note(n)) for b, ln, n in row] for row in rows]


# ------------------------------------------------------------------ night
# Bb major, 64 BPM: pad, music-box bells, slow harp arpeggio. Calm, a bit dreamy.

NIGHT_CHORDS = {
    "Bbmaj7": ([58, 62, 65, 69], 46), "Gm7": ([55, 58, 62, 65], 43), "Ebmaj7": ([51, 55, 58, 62], 39),
    "F": ([53, 57, 60, 65], 41), "Fsus": ([53, 58, 60, 65], 41), "Dm7": ([53, 57, 60, 62], 38),
    "Cm7": ([55, 58, 60, 63], 48),
}
NIGHT_PROG = ["Bbmaj7", "Gm7", "Ebmaj7", "F", "Bbmaj7", "Dm7", "Ebmaj7", "Fsus",
              "Gm7", "Dm7", "Ebmaj7", "Bbmaj7", "Cm7", "F", "Bbmaj7", "F"]
NIGHT_MEL = _melody([
    [(0, 2, "D5"), (2, 2, "F5")],
    [(0, 1.5, "G5"), (1.5, .5, "F5"), (2, 2, "D5")],
    [(0, 2, "Eb5"), (2, 1, "G5"), (3, 1, "Bb5")],
    [(0, 3, "A5"), (3, 1, "F5")],
    [(0, 2, "D5"), (2, 1, "F5"), (3, 1, "A5")],
    [(0, 1.5, "A5"), (1.5, .5, "G5"), (2, 2, "F5")],
    [(0, 1, "G5"), (1, 1, "Bb5"), (2, 2, "G5")],
    [(0, 4, "F5")],
    [(0, 2, "D5"), (2, 1, "G5"), (3, 1, "Bb5")],
    [(0, 3, "A5"), (3, 1, "F5")],
    [(0, 1.5, "G5"), (1.5, .5, "F5"), (2, 2, "Eb5")],
    [(0, 2, "D5"), (2, 2, "F5")],
    [(0, 1, "Eb5"), (1, 1, "G5"), (2, 2, "C6")],
    [(0, 1.5, "A5"), (1.5, .5, "G5"), (2, 2, "F5")],
    [(0, 4, "D5")],
    [(0, 2, "C5"), (2, 2, "A4")],
])


def compose_night(bpm: float = 64.0) -> np.ndarray:
    beat = 60 / bpm
    bar = 4 * beat
    mix = Mix(bar * len(NIGHT_PROG), 7.0)
    for b, cname in enumerate(NIGHT_PROG):
        voicing, root = NIGHT_CHORDS[cname]
        t0 = b * bar
        second = b >= 8
        mix.put(pad(voicing, bar + 1.0, 0.9), t0, 0.6, 0.0, 0.6)
        mix.put(pluck(root, beat * 3.5, 0.7, bright=0.05), hum(t0), 0.5, -0.1, 0.2)
        # slow harp: chord tones up, one per beat, gentle
        for k, idx in enumerate([0, 1, 2, 3]):
            mix.put(pluck(voicing[idx] + 12, 2.2, 0.55, bright=0.25), hum(t0 + k * beat + beat * 0.5, 0.01),
                    0.2, 0.4 if k % 2 else -0.4, 0.5)
        for pos, ln, m in NIGHT_MEL[b]:
            at = hum(t0 + pos * beat, 0.008)
            mix.put(bell(m, max(2.0, ln * beat + 1.2), 0.9), at, 0.32, -0.15, 0.6)
            if second:
                mix.put(flute(m - 12, ln * beat * 0.97 + 0.15, 0.8), at, 0.22, 0.2, 0.5)
    return mix.render(size=0.86, damp=4200, wet=0.7, peak=0.72)


# ------------------------------------------------------------------ village
# G major, 100 BPM: bouncy bass, marimba off-beat chops, woodblock, flute tune.

VILLAGE_CHORDS = {
    "G": ([55, 59, 62, 67], 43), "Em7": ([55, 59, 62, 64], 40), "C": ([55, 60, 64, 67], 48),
    "D": ([54, 57, 62, 66], 38), "Bm7": ([54, 57, 59, 62], 47), "D7": ([54, 57, 60, 62], 38),
    "Am7": ([55, 57, 60, 64], 45),
}
VILLAGE_PROG = ["G", "Em7", "C", "D", "G", "Bm7", "C", "D7",
                "Em7", "C", "G", "D", "Am7", "D7", "G", "G"]
VILLAGE_MEL = _melody([
    [(0, .5, "B4"), (.5, .5, "D5"), (1, 1, "G5"), (2, .5, "F#5"), (2.5, .5, "E5"), (3, 1, "D5")],
    [(0, 1, "E5"), (1, .5, "G5"), (1.5, .5, "E5"), (2, 2, "B4")],
    [(0, .5, "C5"), (.5, .5, "E5"), (1, 1, "G5"), (2, 1, "A5"), (3, 1, "G5")],
    [(0, 1.5, "F#5"), (1.5, .5, "E5"), (2, 2, "D5")],
    [(0, .5, "B4"), (.5, .5, "D5"), (1, 1, "G5"), (2, .5, "A5"), (2.5, .5, "B5"), (3, 1, "G5")],
    [(0, 1, "F#5"), (1, 1, "D5"), (2, 2, "B4")],
    [(0, 1, "E5"), (1, 1, "G5"), (2, 1, "C6"), (3, 1, "B5")],
    [(0, 2, "A5"), (2, 1, "F#5"), (3, 1, "D5")],
    [(0, 1, "G5"), (1, .5, "F#5"), (1.5, .5, "E5"), (2, 2, "B4")],
    [(0, 1, "C5"), (1, 1, "E5"), (2, 2, "G5")],
    [(0, .5, "D5"), (.5, .5, "G5"), (1, 1, "B5"), (2, 1, "A5"), (3, 1, "G5")],
    [(0, 3, "F#5"), (3, 1, "A5")],
    [(0, 1, "C6"), (1, 1, "A5"), (2, 1, "E5"), (3, 1, "G5")],
    [(0, 1.5, "F#5"), (1.5, .5, "E5"), (2, 1, "D5"), (3, 1, "C5")],
    [(0, 2, "B4"), (2, 2, "D5")],
    [(0, 3, "G5"), (3, 1, "D5")],
])


def compose_village(bpm: float = 100.0) -> np.ndarray:
    beat = 60 / bpm
    bar = 4 * beat
    mix = Mix(bar * len(VILLAGE_PROG), 4.0)
    for b, cname in enumerate(VILLAGE_PROG):
        voicing, root = VILLAGE_CHORDS[cname]
        t0 = b * bar
        second = b >= 8
        mix.put(pad(voicing, bar + 0.4, 0.6), t0, 0.32, 0.0, 0.4)
        # bass: root on 1, fifth on 3, walking pickup on 4&
        mix.put(pluck(root, beat * 1.4, 0.95, bright=0.2), hum(t0), 0.6, -0.1, 0.08)
        mix.put(pluck(root + 7, beat * 1.4, 0.8, bright=0.2), hum(t0 + 2 * beat), 0.5, -0.1, 0.08)
        mix.put(pluck(root + 5 if b % 2 else root + 12, beat * 0.6, 0.6, bright=0.2),
                hum(t0 + 3.5 * beat), 0.35, -0.1, 0.08)
        # off-beat chord chops on the "and"s
        for k in range(4):
            at = hum(t0 + (k + 0.5) * beat)
            for m in voicing[1:]:
                mix.put(marimba(m + 12, 0.35, 0.7), at, 0.09, 0.35, 0.2)
        # percussion: woodblock on 2 and 4, shaker eighths
        for k in (1, 3):
            mix.put(woodblock(0.15, 0.9), hum(t0 + k * beat, 0.003), 0.45, 0.3, 0.1)
        for k in range(8):
            mix.put(shaker(0.09, 0.9 if k % 2 else 0.45), hum(t0 + k * beat / 2, 0.004), 0.45, -0.3, 0.05)
        if second:
            mix.put(thump(0.4, 0.8), t0, 0.5, 0.0, 0.05)
        for pos, ln, m in VILLAGE_MEL[b]:
            at = hum(t0 + pos * beat)
            if second:
                mix.put(flute(m, ln * beat * 0.95 + 0.06), at, 0.45, -0.2, 0.35)
            else:
                mix.put(pluck(m, max(0.6, ln * beat + 0.3), 0.95, bright=0.6), at, 0.42, -0.2, 0.3)
                mix.put(marimba(m + 12, 0.6, 0.4), at, 0.08, 0.2, 0.3)
    return mix.render(size=0.78, damp=5600, wet=0.42, peak=0.8)


# ------------------------------------------------------------------ primeval vale
# D dorian, 76 BPM: low marimba ostinato, frame drum, airy flute. Mysterious but warm.

VALE_CHORDS = {
    "Dm9": ([53, 57, 60, 64], 38), "C": ([52, 55, 60, 64], 36), "G": ([55, 59, 62, 67], 43),
    "Em7": ([52, 55, 59, 62], 40), "Am7": ([55, 57, 60, 64], 45), "F": ([53, 57, 60, 65], 41),
}
VALE_PROG = ["Dm9", "C", "Dm9", "G", "Dm9", "C", "Em7", "Am7",
             "F", "G", "Dm9", "Am7", "F", "G", "Em7", "Am7"]
VALE_MEL = _melody([
    [(0, 2, "A4"), (2, 1, "D5"), (3, 1, "E5")],
    [(0, 2, "E5"), (2, 2, "C5")],
    [(0, 1, "D5"), (1, 1, "F5"), (2, 1.5, "A5"), (3.5, .5, "G5")],
    [(0, 1.5, "D5"), (1.5, .5, "E5"), (2, 2, "B4")],
    [(0, 2, "A4"), (2, 1, "D5"), (3, 1, "F5")],
    [(0, 1.5, "E5"), (1.5, .5, "D5"), (2, 2, "C5")],
    [(0, 1, "B4"), (1, 1, "D5"), (2, 2, "G5")],
    [(0, 4, "E5")],
    [(0, 1, "F5"), (1, 1, "A5"), (2, 2, "C6")],
    [(0, 2, "B5"), (2, 2, "G5")],
    [(0, 1, "A5"), (1, 1, "F5"), (2, 1, "E5"), (3, 1, "D5")],
    [(0, 3, "E5"), (3, 1, "C5")],
    [(0, 2, "A4"), (2, 2, "C5")],
    [(0, 2, "D5"), (2, 2, "B4")],
    [(0, 2, "E5"), (2, 2, "G5")],
    [(0, 2, "C5"), (2, 2, "E5")],
])
OSTINATO = [0, 7, 12, 14, 12, 7, 3, 7]  # semitones over the bass root


def compose_vale(bpm: float = 76.0) -> np.ndarray:
    beat = 60 / bpm
    bar = 4 * beat
    mix = Mix(bar * len(VALE_PROG), 6.0)
    for b, cname in enumerate(VALE_PROG):
        voicing, root = VALE_CHORDS[cname]
        t0 = b * bar
        second = b >= 8
        mix.put(pad(voicing, bar + 0.8, 1.0), t0, 0.62, 0.0, 0.55)
        mix.put(pad([root + 12], bar + 0.8, 0.8), t0, 0.35, 0.0, 0.3)
        # low marimba ostinato (minor third only on minor chords)
        minor = cname.startswith(("Dm", "Em", "Am"))
        for k, step in enumerate(OSTINATO):
            if step == 3 and not minor:
                step = 4
            mix.put(marimba(root + 24 + step, 0.7, 0.8 if k % 2 == 0 else 0.55),
                    hum(t0 + k * beat / 2), 0.2, 0.3 if k % 2 else -0.3, 0.3)
        # frame drum: 1 and 2&, soft ghost on 4
        mix.put(thump(0.6, 1.0), hum(t0, 0.003), 0.62, 0.0, 0.15)
        mix.put(thump(0.5, 0.7), hum(t0 + 1.5 * beat, 0.003), 0.45, 0.0, 0.15)
        if second:
            mix.put(thump(0.4, 0.45), hum(t0 + 3 * beat, 0.003), 0.35, 0.0, 0.15)
            for k in range(4):
                mix.put(shaker(0.14, 0.6), hum(t0 + (k + 0.5) * beat, 0.005), 0.4, 0.4, 0.15)
        for pos, ln, m in VALE_MEL[b]:
            at = hum(t0 + pos * beat, 0.01)
            mix.put(flute(m, ln * beat * 0.97 + 0.12, 0.95), at, 0.46, -0.2, 0.55)
            if second:
                mix.put(bell(m + 12, 1.6, 0.4), at, 0.07, 0.4, 0.6)
    return mix.render(size=0.85, damp=4600, wet=0.65, peak=0.78)
