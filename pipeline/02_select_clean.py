"""Step 2: select the structures listed in structures.json, convert to the
three.js frame, and clean each mesh.

    python pipeline/02_select_clean.py <build dir>

Reads  <build>/za_*.npz          (from step 1)
Writes <build>/stage2/<id>.bin    float32 xyz positions (mm) + uint32 triangle indices
       <build>/stage2/manifest.json

Frame conversion (applied identically to every vertex of every structure):
    Blender (Z-up, meters, person faces -Y)  ->  three.js (Y-up, millimeters, person faces +Z)
    x' = 1000 * x,   y' = 1000 * z,   z' = -1000 * y
This is a rotation plus a unit change. No structure is scaled or moved on its own.
After conversion the person's right side is at -X (on the viewer's left in a front view).

Cleaning keeps original vertex positions:
  * vertices with identical positions are merged (no snapping tolerance beyond float rounding),
  * zero-area and duplicate triangles are removed, unreferenced vertices dropped,
  * triangle winding is made consistent per connected piece, and closed pieces are
    flipped outward if they were inside-out.
"""
import glob, json, os, struct, sys
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
build = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'build')
out_dir = os.path.join(build, 'stage2')
os.makedirs(out_dir, exist_ok=True)


def to_three(v_m):
    v = np.asarray(v_m, np.float64)
    return np.stack([v[:, 0], v[:, 2], -v[:, 1]], 1) * 1000.0


# Load every mesh from step 1, remembering which file it came from.
objects, hierarchy = {}, {}
for f in sorted(glob.glob(os.path.join(build, 'za_*.npz'))):
    z = np.load(f)
    hierarchy[os.path.basename(f).replace('za_', '').replace('.npz', '.fbx')] = json.loads(str(z['hierarchy']))
    for m in json.loads(str(z['meta'])):
        m['file'] = os.path.basename(f).replace('za_', '').replace('.npz', '.fbx')
        m['V'], m['F'] = z[m['key'] + '_v'], z[m['key'] + '_f']
        objects.setdefault((m['file'], m['name']), m)
by_name = {}
for (fname, name), m in objects.items():
    by_name.setdefault(name, []).append(m)

# FMA IDs come only from the BodyParts3D term lists (concept id <tab> rep id <tab> name).
fma = {}
for lst in ('isa_parts_list_e.txt', 'partof_parts_list_e.txt'):
    p = os.path.join(build, 'bp3d', lst)
    if os.path.exists(p):
        for line in open(p, encoding='utf-8').read().splitlines()[1:]:
            c, _, en = line.split('\t')
            fma.setdefault(en.strip().lower(), c)


def descendants(root):
    """All mesh objects in the same FBX whose parent chain reaches `root`."""
    parent_of = hierarchy[root['file']]
    out = []
    for m in objects.values():
        if m['file'] != root['file']:
            continue
        p, seen = m['parent'], set()
        while p and p not in seen:
            seen.add(p)
            if p == root['name']:
                out.append(m)
                break
            p = parent_of.get(p, '')
    return out


def clean(V, F):
    stats = {}
    mesh = trimesh.Trimesh(V, F, process=False)
    n0v, n0f = len(mesh.vertices), len(mesh.faces)
    mesh.merge_vertices(merge_tex=True, merge_norm=True)
    stats['merged_vertices'] = n0v - len(mesh.vertices)
    keep = mesh.nondegenerate_faces(height=1e-9)
    stats['degenerate_faces'] = int((~keep).sum())
    mesh.update_faces(keep)
    uniq = mesh.unique_faces()
    stats['duplicate_faces'] = int(len(mesh.faces) - uniq.sum())
    mesh.update_faces(uniq)
    mesh.remove_unreferenced_vertices()
    flipped = 0
    parts = mesh.split(only_watertight=False, repair=False)
    fixed = []
    for part in parts:
        before = part.faces.copy()
        trimesh.repair.fix_winding(part)
        if part.is_watertight and part.volume < 0:
            part.invert()
        flipped += int((part.faces != before).any(axis=1).sum())
        fixed.append(part)
    mesh = trimesh.util.concatenate(fixed) if len(fixed) > 1 else fixed[0]
    stats['faces_reoriented'] = flipped
    stats['pieces'] = len(parts)
    stats['watertight_pieces'] = int(sum(p.is_watertight for p in fixed))
    # Positions must be bit-for-bit original values.
    assert np.isin(mesh.vertices.view([('', mesh.vertices.dtype)] * 3),
                   V.view([('', V.dtype)] * 3)).all()
    return mesh, stats


structures = json.load(open(os.path.join(HERE, 'structures.json')))
manifest = []
for s in structures:
    parts = []
    for name in s['za_objects']:
        cands = by_name.get(name)
        if not cands:
            sys.exit(f"missing source object: {name!r} for {s['id']}")
        root = cands[0]
        parts.append(root)
        if s.get('include_descendants'):
            parts += descendants(root)
    Vs, Fs, off = [], [], 0
    for p in parts:
        Vs.append(to_three(p['V'])); Fs.append(p['F'] + off); off += len(p['V'])
    V = np.concatenate(Vs); F = np.concatenate(Fs)
    mesh, st = clean(V, F)
    pos = mesh.vertices.astype(np.float32); idx = mesh.faces.astype(np.uint32)
    with open(os.path.join(out_dir, s['id'] + '.bin'), 'wb') as fh:
        fh.write(struct.pack('<II', len(pos), len(idx)))
        fh.write(pos.tobytes()); fh.write(idx.tobytes())
    qf = np.average([p['quad_fraction'] for p in parts], weights=[p['nverts'] for p in parts])
    fid = fma.get((s.get('fma_name') or '').lower())
    manifest.append(dict(
        id=s['id'], group=s['group'], note=s.get('note'),
        source_file=sorted({p['file'] for p in parts}),
        source_objects=[p['name'] for p in parts],
        fma_id=fid, fma_name=s.get('fma_name') if fid else None,
        source_vertices=int(sum(p['nverts'] for p in parts)),
        vertices=len(pos), triangles=len(idx),
        quad_fraction=round(float(qf), 3),
        bbox_min=pos.min(0).round(2).tolist(), bbox_max=pos.max(0).round(2).tolist(),
        cleaning=st))
    print(f"{s['id']:40s} {len(pos):7d} v {len(idx):7d} t  {st}")
json.dump(manifest, open(os.path.join(out_dir, 'manifest.json'), 'w'), indent=1)
print(len(manifest), 'structures written to', out_dir)
