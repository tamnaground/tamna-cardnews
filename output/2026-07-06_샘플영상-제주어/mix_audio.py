"""Mix rain ambience + synthesized dialogue lines into the final soundtrack."""
import json, math, os, random, struct, wave

os.chdir(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open('timeline.json'))
SR = 44100
N = int(SR * T['total'])
rng = random.Random(7)

mix = [0.0] * N

# ---- rain ambience: filtered noise with slow gusts ----
lp1, lp2 = 0.0, 0.0
for i in range(N):
    t = i / SR
    n = rng.uniform(-1, 1)
    lp1 += 0.18 * (n - lp1)          # low-pass stages -> soft rumble/hiss
    lp2 += 0.35 * (lp1 - lp2)
    gust = 1.0 + 0.35 * math.sin(2 * math.pi * 0.07 * t + 1.3) + 0.2 * math.sin(2 * math.pi * 0.13 * t)
    mix[i] = lp2 * 0.55 * gust       # rain bed

# ---- dialogue lines ----
for L in T['lines']:
    off = int(L['start'] * SR)
    with wave.open(f"line{L['i']}.wav") as w:
        assert w.getframerate() == SR and w.getnchannels() == 1
        data = struct.unpack('<' + 'h' * w.getnframes(), w.readframes(w.getnframes()))
    for j, s in enumerate(data):
        k = off + j
        if k < N:
            mix[k] += (s / 32768.0) * 0.95

# ---- soft outro chime ----
for (st, f) in [(T['outro_start'] + 0.6, 784.0), (T['outro_start'] + 0.6, 1046.5)]:
    for j in range(int(2.2 * SR)):
        k = int(st * SR) + j
        if k < N:
            dt = j / SR
            mix[k] += math.sin(2 * math.pi * f * dt) * math.exp(-2.2 * dt) * 0.05

# ---- master envelope + clip ----
out = []
DUR = T['total']
for i in range(N):
    t = i / SR
    v = mix[i]
    if t < 0.8: v *= t / 0.8
    if t > DUR - 1.6: v *= max((DUR - t) / 1.6, 0.0)
    out.append(int(max(-1.0, min(1.0, v)) * 32767))

with wave.open('mix.wav', 'w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(struct.pack('<' + 'h' * N, *out))
print('mix.wav written', N / SR, 's')
