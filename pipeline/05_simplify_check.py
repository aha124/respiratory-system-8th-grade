"""Step 5: build the GLB, decode it, and measure how far each simplified mesh is
from its cleaned original (two-sided Hausdorff distance, mm). If a mesh is over its
limit (1 mm small / 2 mm large), tighten its simplifier target and rebuild.

    python pipeline/05_simplify_check.py [build dir]

Writes <build>/stage3/simplification_errors.json
"""
import json, os, struct, subprocess, sys
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
build = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, 'build')
glb = os.path.join(REPO, 'models', 'respiratory.glb')
stage3 = os.path.join(build, 'stage3'); os.makedirs(stage3, exist_ok=True)
rng = np.random.default_rng(0)


def read_bin(p):
    b = open(p, 'rb').read(); nv, nt = struct.unpack('<II', b[:8])
    V = np.frombuffer(b[8:8 + nv * 12], np.float32).reshape(-1, 3).astype(np.float64)
    F = np.frombuffer(b[8 + nv * 12:8 + nv * 12 + nt * 12], np.uint32).reshape(-1, 3)
    return trimesh.Trimesh(V, F, process=False)


def hausdorff(a, b, n=30000):
    """Two-sided distance: surface samples + all vertices of each mesh against the other."""
    pa = np.vstack([trimesh.sample.sample_surface(a, n, seed=rng)[0], a.vertices])
    pb = np.vstack([trimesh.sample.sample_surface(b, n, seed=rng)[0], b.vertices])
    d_ab = trimesh.proximity.closest_point(b, pa)[1]
    d_ba = trimesh.proximity.closest_point(a, pb)[1]
    return float(max(d_ab.max(), d_ba.max())), float(np.percentile(np.r_[d_ab, d_ba], 99))


targets_path = os.path.join(stage3, 'targets.json')
targets = json.load(open(targets_path)) if os.path.exists(targets_path) else {}
for it in range(8):
    subprocess.run(['node', os.path.join(HERE, '03_build_glb.mjs'), build, glb], check=True, cwd=REPO)
    subprocess.run(['node', os.path.join(HERE, '04_dump_glb.mjs'), glb, os.path.join(build, 'export')], check=True, cwd=REPO)
    rep = {r['id']: r for r in json.load(open(os.path.join(stage3, 'simplify_report.json')))}
    failing, results = [], []
    for sid, r in rep.items():
        h, p99 = hausdorff(read_bin(os.path.join(build, 'stage2', sid + '.bin')),
                           read_bin(os.path.join(build, 'export', sid + '.bin')))
        ok = h < r['limit_mm']
        results.append(dict(r, hausdorff_mm=round(h, 3), p99_mm=round(p99, 3), ok=ok))
        if not ok:
            failing.append(sid)
            targets[sid] = round(r['target_mm'] * 0.5, 4) if r['target_mm'] > 0.02 else 0
    json.dump(results, open(os.path.join(stage3, 'simplification_errors.json'), 'w'), indent=1)
    print(f'iteration {it}: {len(failing)} over limit {failing}')
    if not failing:
        break
    json.dump(targets, open(targets_path, 'w'), indent=1)
else:
    sys.exit('simplification check did not converge')
worst = max(results, key=lambda r: r['hausdorff_mm'] / r['limit_mm'])
print(f"all {len(results)} meshes within limits; worst ratio {worst['id']} {worst['hausdorff_mm']} / {worst['limit_mm']} mm")
