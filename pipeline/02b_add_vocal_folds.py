"""Step 2b: fill the one gap in Z-Anatomy we can fill from real data, the vocal folds.

    python pipeline/02b_add_vocal_folds.py <build dir> <BodyParts3D isa obj dir>

Z-Anatomy has no vocal fold mesh. BodyParts3D 4.0 (the body Z-Anatomy is built on)
has the vocal ligaments (FMA55245/55246) and vocalis muscles (FMA46592/46593), which
together make the core of each vocal fold. BodyParts3D uses its own origin, so we
find the rigid transform (rotation + translation, no scaling) that best maps the
BodyParts3D laryngeal cartilages (thyroid, cricoid, both arytenoids) onto the
Z-Anatomy cartilages already in stage2, and apply that same transform to the vocal
ligaments and vocalis muscles. The fit residual is saved and shown in the report.
The vocal folds are never moved on their own: they ride with the cartilages they
attach to.
"""
import json, os, struct, sys
import numpy as np
import trimesh

build, bp_dir = sys.argv[1], sys.argv[2]
stage2 = os.path.join(build, 'stage2')
CARTILAGES = {'FJ2808': 'thyroid cartilage', 'FJ2440': 'cricoid cartilage',
              'FJ2775': 'left arytenoid cartilage', 'FJ2792': 'right arytenoid cartilage'}
FOLDS = {'FJ2805': ('right vocal ligament', 'FMA55245'), 'FJ2787': ('left vocal ligament', 'FMA55246'),
         'FJ2806': ('right vocalis', 'FMA46592'), 'FJ2788': ('left vocalis', 'FMA46593')}


def load_obj(fj):
    V, F = [], []
    for line in open(os.path.join(bp_dir, fj + '.obj')):
        if line.startswith('v '):
            V.append([float(x) for x in line.split()[1:4]])
        elif line.startswith('f '):
            F.append([int(x.split('/')[0]) - 1 for x in line.split()[1:4]])
    V = np.array(V)
    # BodyParts3D: Z-up, mm, person faces -Y  ->  Y-up, mm, person faces +Z (same rotation as step 2)
    return trimesh.Trimesh(np.stack([V[:, 0], V[:, 2], -V[:, 1]], 1), np.array(F), process=False)


def load_stage2(sid):
    b = open(os.path.join(stage2, sid + '.bin'), 'rb').read(); nv, nt = struct.unpack('<II', b[:8])
    V = np.frombuffer(b[8:8 + nv * 12], np.float32).reshape(-1, 3).astype(np.float64)
    F = np.frombuffer(b[8 + nv * 12:8 + nv * 12 + nt * 12], np.uint32).reshape(-1, 3)
    return trimesh.Trimesh(V, F, process=False)


src = trimesh.util.concatenate([load_obj(f) for f in CARTILAGES])
dst = trimesh.util.concatenate([load_stage2(s) for s in ('thyroid_cartilage', 'cricoid_cartilage', 'arytenoid_cartilages')])
pts = trimesh.sample.sample_surface(src, 8000, seed=1)[0]
init = trimesh.transformations.translation_matrix(dst.centroid - src.centroid)
M, _, _ = trimesh.registration.icp(pts, dst, initial=init, max_iterations=300, scale=False, reflection=False)
moved = src.copy(); moved.apply_transform(M)
d = np.r_[trimesh.proximity.closest_point(dst, trimesh.sample.sample_surface(moved, 20000, seed=2)[0])[1],
          trimesh.proximity.closest_point(moved, trimesh.sample.sample_surface(dst, 20000, seed=3)[0])[1]]
angle = np.degrees(np.arccos(np.clip((np.trace(M[:3, :3]) - 1) / 2, -1, 1)))
fit = dict(rotation_deg=round(float(angle), 3), translation_mm=M[:3, 3].round(2).tolist(),
           residual_mean_mm=round(float(d.mean()), 3), residual_p90_mm=round(float(np.percentile(d, 90)), 3),
           residual_max_mm=round(float(d.max()), 3))
print('cartilage fit:', fit)

folds = trimesh.util.concatenate([load_obj(f) for f in FOLDS])
folds.apply_transform(M)
folds.merge_vertices()
folds.update_faces(folds.nondegenerate_faces(height=1e-9)); folds.update_faces(folds.unique_faces())
folds.remove_unreferenced_vertices()
parts = folds.split(only_watertight=False, repair=False)
for p in parts:
    trimesh.repair.fix_winding(p)
    if p.is_watertight and p.volume < 0:
        p.invert()
folds = trimesh.util.concatenate(parts)
pos = folds.vertices.astype(np.float32); idx = folds.faces.astype(np.uint32)
with open(os.path.join(stage2, 'vocal_folds.bin'), 'wb') as fh:
    fh.write(struct.pack('<II', len(pos), len(idx))); fh.write(pos.tobytes()); fh.write(idx.tobytes())

man_path = os.path.join(stage2, 'manifest.json')
manifest = [m for m in json.load(open(man_path)) if m['id'] != 'vocal_folds']
entry = dict(
    id='vocal_folds', group='airway',
    note='Vocal ligaments and vocalis muscles from BodyParts3D 4.0, placed with the rigid transform that fits '
         'BodyParts3D laryngeal cartilages onto Z-Anatomy laryngeal cartilages.',
    source_file=['BodyParts3D 4.0 isa_BP3D_4.0_obj_99.zip: ' + ', '.join(f + '.obj' for f in FOLDS)],
    source_objects=[v[0] for v in FOLDS.values()],
    fma_id=', '.join(v[1] for v in FOLDS.values()), fma_name='vocal ligament + vocalis',
    source_vertices=int(sum(load_obj(f).vertices.shape[0] for f in FOLDS)),
    vertices=len(pos), triangles=len(idx), quad_fraction=0.0,
    bbox_min=pos.min(0).round(2).tolist(), bbox_max=pos.max(0).round(2).tolist(),
    cleaning=dict(pieces=len(parts)), registration=fit)
# keep larynx order: put vocal folds right after the arytenoids
at = next(i for i, m in enumerate(manifest) if m['id'] == 'corniculate_cartilages') + 1
manifest.insert(at, entry)
json.dump(manifest, open(man_path, 'w'), indent=1)
print('vocal_folds', len(pos), 'v', len(idx), 't', 'extent', folds.extents.round(1))
