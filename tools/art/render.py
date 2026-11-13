"""Render every sprite frame with Blender (bpy) into tools/art/.cache/.

Raw renders are cached by a hash of the toolkit + the asset module source,
so only changed assets are re-rendered.

    python tools/art/render.py              # everything that changed
    python tools/art/render.py barn chicken # only frames whose name contains one of these
    python tools/art/render.py --force      # ignore the cache
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
CACHE = HERE / ".cache"

# (module, frames function, shadow pass, samples)
REGISTRY = [
    ("buildings", "building_frames", True, 64),
    ("nature", "nature_frames", True, 48),
    ("farm", "farm_frames", True, 48),
    ("animals", "chicken_frames", False, 40),
    ("animals", "dino_frames", False, 40),
    ("animals", "cow_frames", False, 40),
    ("animals", "sheep_frames", False, 40),
    ("animals", "pig_frames", False, 40),
    ("icons", "icon_frames", False, 48),
    ("village", "village_frames", True, 48),
    ("progress", "progress_frames", True, 56),
]


# asset modules that import helpers from other asset modules
DEPS = {
    "buildings": ["farm", "nature"],
    "farm": ["nature"],
    "village": ["animals", "buildings", "farm", "nature"], "progress": ["buildings", "farm", "nature"],
}


# camera-facing sprites that float in the air: no ground shadow
NO_SHADOW = {"mill_sails", "fx_bee", "coin_crate"}


def module_hash(module: str) -> str:
    """Hash of the toolkit + this module + the modules it borrows from."""
    h = hashlib.sha1()
    h.update((HERE / "blender" / "kit.py").read_bytes())
    for m in [module] + DEPS.get(module, []):
        h.update((HERE / "blender" / "assets" / f"{m}.py").read_bytes())
    return h.hexdigest()[:16]


def main(argv: list[str]) -> int:
    force = "--force" in argv
    filters = [a for a in argv if not a.startswith("--")]
    from blender import kit  # noqa: E402  (needs bpy)

    CACHE.mkdir(exist_ok=True)
    meta_path = CACHE / "meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    current = None
    rendered = 0
    t0 = time.time()
    for module, fn, shadow, samples in REGISTRY:
        mod = __import__(f"blender.assets.{module}", fromlist=[fn])
        frames = getattr(mod, fn)()
        key = module_hash(module)
        for name, build in frames.items():
            if filters and not any(f in name for f in filters):
                continue
            entry = meta.get(name)
            obj = CACHE / f"{name}.png"
            if not force and entry and entry["key"] == key and obj.exists():
                continue
            if current != samples:
                kit.reset(samples=samples)
                current = samples
            kit.clear_stage()
            build()
            floating = name in NO_SHADOW or name.startswith("npc_")
            sh = CACHE / f"{name}_shadow.png" if shadow and not floating else None
            t = time.time()
            info = kit.fit_and_render(str(obj), str(sh) if sh else None)
            meta[name] = {"key": key, "ax": info["ax"], "ay": info["ay"], "shadow": sh is not None, "module": module}
            meta_path.write_text(json.dumps(meta, indent=1, sort_keys=True))
            rendered += 1
            print(f"  rendered {name:28s} {info['w']}x{info['h']}  {time.time() - t:5.1f}s", flush=True)
    print(f"render: {rendered} frames in {time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
