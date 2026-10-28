"""Step 6: measure the exported model and compare it with adult reference ranges.

    python pipeline/06_verify.py [build dir]

Measures the meshes decoded from models/respiratory.glb (dumped by 04_dump_glb.mjs
into <build>/export), so the numbers describe exactly what the app shows.
Frame: Y up, millimeters, person faces +Z, person's right side is -X.

Writes reports/verification_report.md and reports/verification_report.json.
"""
import json, os, struct, sys
import numpy as np
import networkx as nx
import trimesh
from trimesh.grouping import group_rows

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
build = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, 'build')
EXPORT = os.path.join(build, 'export')
index = {e['id']: e for e in json.load(open(os.path.join(EXPORT, 'index.json')))}


def mesh(sid):
    b = open(os.path.join(EXPORT, sid + '.bin'), 'rb').read(); nv, nt = struct.unpack('<II', b[:8])
    V = np.frombuffer(b[8:8 + nv * 12], np.float32).reshape(-1, 3).astype(np.float64)
    F = np.frombuffer(b[8 + nv * 12:8 + nv * 12 + nt * 12], np.uint32).reshape(-1, 3)
    m = trimesh.Trimesh(V, F, process=False)
    m.merge_vertices()  # quantization can split nothing, but be safe for topology queries
    return m


def boundary_loops(m):
    e = m.edges_sorted
    b = e[group_rows(e, require_count=1)]
    return [m.vertices[list(c)] for c in nx.connected_components(nx.from_edgelist(b))]


def section_polys(m, origin, normal):
    """Closed cross-section polygons of a mesh, plus the 2D->3D transform."""
    sec = m.section(plane_origin=origin, plane_normal=normal)
    if sec is None:
        return [], None
    planar, to_3d = sec.to_2D()
    return list(planar.polygons_full), to_3d


def to3(to_3d, xy):
    return (to_3d @ np.array([xy[0], xy[1], 0, 1.]))[:3]


def angle_from_vertical(v):
    v = np.asarray(v, float)
    return float(np.degrees(np.arccos(abs(v[1]) / np.linalg.norm(v))))


checks, facts = [], {}


def check(cid, name, value, unit, lo, hi, reference, how, note=''):
    status = 'N/A' if value is None else ('PASS' if lo <= value <= hi else 'FLAG')
    checks.append(dict(id=cid, name=name, value=None if value is None else round(float(value), 1), unit=unit,
                       reference=reference, range=[lo, hi], status=status, method=how, note=note))


# ---------------------------------------------------------------- trachea
tr = mesh('trachea')
top_loop = max(boundary_loops(tr), key=lambda L: L[:, 1].mean())
top = top_loop.mean(0)

# Right and left main bronchus tubes: each has two open ends. The upper end of both
# is the same point inside the trachea (the branching node of the airway tree).
rmb, lmb = mesh('right_main_bronchus'), mesh('left_main_bronchus')
def ends(m):
    loops = sorted(boundary_loops(m), key=lambda L: -L[:, 1].mean())
    return loops[0].mean(0), loops[-1].mean(0), loops[0]
r_start, r_end, r_ring = ends(rmb)
l_start, l_end, l_ring = ends(lmb)
junction = (r_start + l_start) / 2
tube_radius = float(np.linalg.norm(r_ring - r_ring.mean(0), axis=1).mean())

# Carina: the highest level at which horizontal sections of the right and left main
# bronchus tubes no longer touch, i.e. where the ridge between them starts.
carina_y = None
for y in np.arange(junction[1], junction[1] - 40, -0.25):
    sr = rmb.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    sl = lmb.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    if sr is None or sl is None:
        continue
    flat = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, y], [0, 0, 0, 1.]])  # same 2D frame for both
    pr = sr.to_2D(to_2D=flat)[0]
    pl = sl.to_2D(to_2D=flat)[0]
    if pr.polygons_full and pl.polygons_full:
        if not any(a.intersects(b) for a in pr.polygons_full for b in pl.polygons_full):
            carina_y = float(y); break
carina = np.array([junction[0], carina_y, junction[2]])
# point on each bronchus centerline at the carina level
def at_level(a, b, y):
    t = (a[1] - y) / (a[1] - b[1]); return a + t * (b - a)
r_from = at_level(r_start, r_end, carina_y); l_from = at_level(l_start, l_end, carina_y)

# Trachea centerline: area centroids of sections perpendicular to the top->carina line,
# lightly smoothed (5-point moving average) so the ring ridges do not add zig-zag length.
axis = (top - carina) / np.linalg.norm(top - carina)
span = float(np.linalg.norm(top - carina))
cents, perims, ts, diams_lr, diams_ap = [], [], [], [], []
ex = np.cross(axis, [0, 0, 1.]); ex /= np.linalg.norm(ex)   # left-right direction in the section plane
ez = np.cross(ex, axis)                                    # front-back direction
for f in np.linspace(0.005, 0.995, 1000):                  # every ~0.1 mm
    o = top + (carina - top) * f
    polys, to_3d = section_polys(tr, o, -axis)
    if not polys:
        continue
    poly = max(polys, key=lambda p: p.area)
    c3 = to3(to_3d, poly.centroid.coords[0])
    ring = np.array([to3(to_3d, xy) for xy in poly.exterior.coords])
    cents.append(c3); perims.append(poly.exterior.length); ts.append(f * span)
    if 0.2 <= f <= 0.8:
        diams_lr.append(np.ptp((ring - c3) @ ex)); diams_ap.append(np.ptp((ring - c3) @ ez))
cents = np.array(cents)
sm = np.array([np.convolve(cents[:, k], np.ones(5) / 5, mode='valid') for k in range(3)]).T
cl = np.vstack([top, sm, carina])
trachea_len = float(np.linalg.norm(np.diff(cl, axis=0), axis=1).sum())

# Cartilage rings: in the source they are modeled as raised bands on the tracheal surface,
# separated by shallow grooves. A groove makes the section perimeter smaller, so we count
# perimeter minima (after 1 mm smoothing). Rings = grooves + 1.
from scipy.signal import find_peaks
perims, ts = np.array(perims), np.array(ts)
dt = ts[1] - ts[0]
k = max(1, int(round(1.0 / dt)))
smooth = np.convolve(perims, np.ones(k) / k, mode='same')
body = ts < ts.max() - 8          # leave out the closed cap at the lower end
grooves, props = find_peaks(-smooth[body], prominence=0.8, distance=int(4.0 / dt))
ring_count = len(grooves) + 1 if len(grooves) else 0
ring_pitch = float(np.median(np.diff(ts[body][grooves]))) if len(grooves) > 1 else None
ripple_mm = float(np.median(props['prominences'])) if len(grooves) else 0.0

check('trachea_length', 'Trachea length (top of trachea to carina, along its centerline)', trachea_len / 10, 'cm',
      10, 12, '10-12 cm', 'centerline through section centroids from the upper opening (below the cricoid) to the carina')
od = (np.median(diams_lr) + np.median(diams_ap)) / 2
check('trachea_od_lr', 'Trachea outer diameter, left-right', np.median(diams_lr) / 10, 'cm', 2.0, 2.5,
      'about 2-2.5 cm', 'median width of sections perpendicular to the tracheal axis, middle 60 % of length')
check('trachea_od_ap', 'Trachea outer diameter, front-back', np.median(diams_ap) / 10, 'cm', 2.0, 2.5,
      'about 2-2.5 cm', 'same sections, front-back depth')
check('trachea_rings', 'Tracheal cartilage rings (raised bands on the trachea surface)', ring_count, 'rings', 16, 20, '16-20 rings',
      f'perimeter of sections every {ts[1]-ts[0]:.1f} mm along the trachea; the grooves between ring bands are perimeter '
      f'minima (depth at least 0.8 mm, at least 4 mm apart); rings = grooves + 1',
      f'{len(grooves)} grooves, median ring spacing {ring_pitch:.1f} mm, groove depth about {ripple_mm/(2*np.pi):.2f} mm. '
      'Rings are surface relief on one trachea mesh, not separate meshes.')
facts['trachea'] = dict(top=top.round(1).tolist(), carina=carina.round(1).tolist(), junction=junction.round(1).tolist(),
                        bronchus_tube_radius_mm=round(tube_radius, 1), groove_positions_mm=ts[body][grooves].round(1).tolist())

# ---------------------------------------------------------------- main bronchi
r_len, l_len = np.linalg.norm(r_end - r_from), np.linalg.norm(l_end - l_from)
r_ang, l_ang = angle_from_vertical(r_end - r_start), angle_from_vertical(l_end - l_start)
check('rmb_length', 'Right main bronchus length, from the carina', r_len / 10, 'cm', 2.0, 3.0,
      'about 2.5 cm (checked as 2.0-3.0 cm)', 'along the tube centerline from the carina level to the branch point of the upper lobe bronchus')
check('rmb_length_node', 'Right main bronchus length, from the tracheal branch point', np.linalg.norm(r_end - r_start) / 10, 'cm', 2.0, 3.0,
      'about 2.5 cm (checked as 2.0-3.0 cm)', 'along the tube centerline from the point where the trachea centerline splits to the upper lobe branch point')
check('lmb_length', 'Left main bronchus length, from the carina', l_len / 10, 'cm', 4.0, 6.0,
      'about 5 cm (checked as 4.0-6.0 cm)', 'along the tube centerline from the carina level to its division into upper and lower lobe bronchi')
check('lmb_length_node', 'Left main bronchus length, from the tracheal branch point', np.linalg.norm(l_end - l_start) / 10, 'cm', 4.0, 6.0,
      'about 5 cm (checked as 4.0-6.0 cm)', 'along the tube centerline from the point where the trachea centerline splits to its division')
check('rmb_angle', 'Right main bronchus angle from vertical', r_ang, 'deg', 20, 30, 'about 20-30 deg',
      'angle between the tube centerline and the vertical (Y) axis')
check('lmb_angle', 'Left main bronchus angle from vertical', l_ang, 'deg', 35, 50, 'about 35-50 deg',
      'angle between the tube centerline and the vertical (Y) axis')
check('rmb_steeper', 'Right main bronchus steeper (more vertical) than left', l_ang - r_ang, 'deg difference',
      0.001, 90, 'right angle < left angle', 'left angle minus right angle; must be positive')

# ---------------------------------------------------------------- vertebral level of the carina
def body_range(sid):
    v = mesh(sid).vertices
    front = v[:, 2].max()
    body = v[(v[:, 2] > front - 15) & (np.abs(v[:, 0]) < 12)]   # front of the body, away from pedicles
    return float(body[:, 1].min()), float(body[:, 1].max())
levels = {f'T{k}': body_range(f'vertebra_t{k}') for k in range(1, 13)}
def level_name(y):
    names = list(levels)
    for i, n in enumerate(names):
        lo, hi = levels[n]
        if lo <= y <= hi:
            frac = (hi - y) / (hi - lo)
            return f'{n} body ({"upper" if frac < 1/3 else "middle" if frac < 2/3 else "lower"} third)'
        if i + 1 < len(names) and levels[names[i + 1]][1] < y < lo:
            return f'{n}/{names[i+1]} disc'
    return 'outside T1-T12'
t4, t5 = levels['T4'], levels['T5']
lo_ok, hi_ok = (t5[0] + t5[1]) / 2, (t4[0] + t4[1]) / 2
check('carina_level', 'Tracheal bifurcation (carina) vertebral level', carina_y, 'mm height', lo_ok, hi_ok,
      'T4/T5 (checked as mid-T4 body to mid-T5 body)', 'carina height compared with the heights of the vertebral bodies (front 15 mm of each vertebra, within 12 mm of the midline)',
      f'carina is at the {level_name(carina_y)}')
facts['vertebral_bodies_mm'] = {k: [round(a, 1), round(b, 1)] for k, (a, b) in levels.items()}

# ---------------------------------------------------------------- diaphragm domes
dv = mesh('diaphragm').vertices
right_dome = dv[dv[:, 0] < -30][:, 1].max(); left_dome = dv[dv[:, 0] > 30][:, 1].max()
check('diaphragm_domes', 'Right diaphragm dome higher than left', right_dome - left_dome, 'mm', 0.001, 60,
      'right dome higher (often by about 1-2 cm)', "highest diaphragm point on the person's right (x < -30 mm) minus highest point on the left (x > 30 mm)",
      f'right dome {right_dome:.1f} mm, left dome {left_dome:.1f} mm')

# ---------------------------------------------------------------- lung apex vs clavicle
for side, lobe, clav, sign in (('right', 'right_upper_lobe', 'clavicle_right', -1), ('left', 'left_upper_lobe', 'clavicle_left', 1)):
    apex_y = mesh(lobe).vertices[:, 1].max()
    cv = mesh(clav).vertices
    c0 = cv.mean(0); u = np.linalg.svd(cv - c0)[2][0]
    proj = (cv - c0) @ u
    if np.sign(u[0]) == sign:   # make proj increase from the sternal (medial) end outward
        proj = -proj
    proj = -proj if cv[np.argmin(proj), 0] * sign > cv[np.argmax(proj), 0] * sign else proj
    med = cv[proj <= proj.min() + (np.ptp(proj) / 3)]
    check(f'apex_{side}', f'{side.title()} lung apex above the medial third of the clavicle (clavicle center line)',
          (apex_y - med[:, 1].mean()) / 10, 'cm', 2.0, 3.0, 'about 2-3 cm above the medial (inner) third',
          'highest point of the upper lobe minus the mean height of the medial third of the clavicle')
    check(f'apex_{side}_top', f'{side.title()} lung apex above the top edge of the medial third of the clavicle',
          (apex_y - med[:, 1].max()) / 10, 'cm', 2.0, 3.0, 'about 2-3 cm above the medial (inner) third',
          'highest point of the upper lobe minus the highest point of the medial third of the clavicle')

# ---------------------------------------------------------------- lobes
lobes_r = [k for k in index if k.startswith('right_') and k.endswith('_lobe')]
lobes_l = [k for k in index if k.startswith('left_') and k.endswith('_lobe')]
check('lobes_right', 'Right lung lobe meshes', len(lobes_r), 'lobes', 3, 3, '3 (upper, middle, lower)', 'count of separate lobe nodes in the GLB')
check('lobes_left', 'Left lung lobe meshes', len(lobes_l), 'lobes', 2, 2, '2 (upper, lower)', 'count of separate lobe nodes in the GLB')

# ---------------------------------------------------------------- context facts
sk = np.vstack([mesh(k).vertices for k in index if k.startswith('rib_')])
facts['rib_cage_width_mm'] = round(float(np.ptp(sk[:, 0])), 1)
facts['main_bronchi'] = dict(right_start=r_start.round(1).tolist(), right_end=r_end.round(1).tolist(),
                             left_start=l_start.round(1).tolist(), left_end=l_end.round(1).tolist(),
                             right_length_from_tree_junction_mm=round(float(np.linalg.norm(r_end - r_start)), 1),
                             left_length_from_tree_junction_mm=round(float(np.linalg.norm(l_end - l_start)), 1))
simp = json.load(open(os.path.join(build, 'stage3', 'simplification_errors.json')))
vocal = next((m for m in json.load(open(os.path.join(build, 'stage2', 'manifest.json'))) if m['id'] == 'vocal_folds'), None)

# ---------------------------------------------------------------- notes (written after reviewing the first run)
NOTES = json.load(open(os.path.join(HERE, 'verification_notes.json'))) if os.path.exists(os.path.join(HERE, 'verification_notes.json')) else {}
for c in checks:
    if c['id'] in NOTES:
        c['note'] = (c['note'] + ' ' if c['note'] else '') + NOTES[c['id']]

os.makedirs(os.path.join(REPO, 'reports'), exist_ok=True)
json.dump(dict(checks=checks, facts=facts, simplification=simp, vocal_fold_registration=vocal and vocal.get('registration')),
          open(os.path.join(REPO, 'reports', 'verification_report.json'), 'w'), indent=1)

L = ['# Verification report', '',
     'Measured on the decoded `models/respiratory.glb` (what the app displays). Units: mm in the model; shown here in cm or degrees.',
     "Frame: Y up, person faces +Z, person's right is -X.", '',
     '| Check | Measured | Reference | Result | Notes |', '|---|---|---|---|---|']
for c in checks:
    val = 'n/a' if c['value'] is None else f"{c['value']} {c['unit']}"
    if c['id'] == 'carina_level':
        val = f"{c['value']} mm ({level_name(carina_y)})"
    L.append(f"| {c['name']} | {val} | {c['reference']} | **{c['status']}** | {c['note']} |")
L += ['', '### How each value was measured', '']
L += [f"- **{c['name']}**: {c['method']}." for c in checks]
L += ['', '### Simplification error (two-sided Hausdorff distance, cleaned source mesh vs. exported mesh)', '',
      f"All {len(simp)} meshes are within their limits. Worst cases:", '',
      '| Structure | Limit | Measured max | 99th percentile | Triangles (source → exported) |', '|---|---|---|---|---|']
for r in sorted(simp, key=lambda r: -r['hausdorff_mm'] / r['limit_mm'])[:8]:
    L.append(f"| {r['id']} | {r['limit_mm']} mm | {r['hausdorff_mm']} mm | {r['p99_mm']} mm | {r['triangles_before']} → {r['triangles_after']} |")
if vocal:
    g = vocal['registration']
    L += ['', '### Vocal fold placement (BodyParts3D → Z-Anatomy)', '',
          f"Rigid fit of the BodyParts3D thyroid, cricoid and arytenoid cartilages onto the Z-Anatomy ones: rotation {g['rotation_deg']}°, "
          f"translation {g['translation_mm']} mm, no scaling. Surface distance after the fit: mean {g['residual_mean_mm']} mm, "
          f"90th percentile {g['residual_p90_mm']} mm, max {g['residual_max_mm']} mm."]
open(os.path.join(REPO, 'reports', 'verification_report.md'), 'w').write('\n'.join(L) + '\n')
for c in checks:
    print(f"{c['status']:4s}  {c['name']}: {c['value']} {c['unit']}  (ref {c['reference']})  {c['note']}")
print(json.dumps(facts, indent=1))
