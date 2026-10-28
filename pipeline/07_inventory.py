"""Step 7: write the source inventory.

    python pipeline/07_inventory.py [build dir] [BodyParts3D dir]

reports/source_inventory.md      every structure in the GLB: source file, source objects, FMA ID, sizes
reports/zanatomy_objects.tsv     every mesh object found in the four Z-Anatomy FBX files (the candidate list)
reports/bp3d_candidates.tsv      BodyParts3D 4.0 OBJ files for respiratory-related concepts, with FMA IDs
"""
import glob, json, os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
build = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, 'build')
bp_dir = sys.argv[2] if len(sys.argv) > 2 else None
out = os.path.join(REPO, 'reports'); os.makedirs(out, exist_ok=True)
manifest = json.load(open(os.path.join(build, 'stage2', 'manifest.json')))
simp = {r['id']: r for r in json.load(open(os.path.join(build, 'stage3', 'simplification_errors.json')))}

L = ['# Source inventory', '',
     'Every node in `models/respiratory.glb`. "Quad share" is the fraction of four-sided faces in the source object. '
     'BodyParts3D meshes are triangle meshes, so a high quad share suggests the surface was modeled or retopologized by '
     'Z-Anatomy artists on the BodyParts3D body rather than taken over unchanged. This is a hint, not proof.', '',
     '| Node | Group | Source file | Source object(s) | FMA ID (from BodyParts3D lists) | Source verts | Exported tris | Max simplification error | Quad share |',
     '|---|---|---|---|---|---|---|---|---|']
for m in manifest:
    s = simp[m['id']]
    objs = ', '.join(m['source_objects'][:4]) + (f' (+{len(m["source_objects"]) - 4} more)' if len(m['source_objects']) > 4 else '')
    L.append(f"| {m['id']} | {m['group']} | {', '.join(m['source_file'])} | {objs} | {m['fma_id'] or 'n/a'} | "
             f"{m['source_vertices']} | {s['triangles_after']} | {s['hausdorff_mm']} mm (limit {s['limit_mm']}) | {m['quad_fraction']:.2f} |")
open(os.path.join(out, 'source_inventory.md'), 'w').write('\n'.join(L) + '\n')

with open(os.path.join(out, 'zanatomy_objects.tsv'), 'w') as fh:
    fh.write('fbx_file\tobject\tparent\tvertices\ttriangles\tquad_fraction\tused_in_node\n')
    used = {(f, o): m['id'] for m in manifest for f in m['source_file'] for o in m['source_objects']}
    for f in sorted(glob.glob(os.path.join(build, 'za_*.npz'))):
        name = os.path.basename(f).replace('za_', '').replace('.npz', '.fbx')
        for o in json.loads(str(np.load(f)['meta'])):
            fh.write(f"{name}\t{o['name']}\t{o['parent']}\t{o['nverts']}\t{o['ntris']}\t{o['quad_fraction']}\t{used.get((name, o['name']), '')}\n")

if bp_dir:
    pat = re.compile(r'lung|bronch|trache|laryn|cartilage|epiglott|vocal|concha|ethmoid|pharyn|diaphragm|rib\b|stern|manubr|'
                     r'xiphoid|clavicle|thoracic vertebra|heart|aorta|pulmonary|esophag|nasal|vomer', re.I)
    with open(os.path.join(out, 'bp3d_candidates.tsv'), 'w') as fh:
        fh.write('tree\tfile\tFMA_id\tname\tvertices\n')
        for tree in ('partof', 'isa'):
            for p in sorted(glob.glob(os.path.join(bp_dir, tree, '*', '*.obj'))):
                head = open(p, errors='ignore').read(1200)
                c = re.search(r'Concept ID : (\S+)', head); n = re.search(r'English name : (.+)', head)
                if c and n and pat.search(n.group(1)):
                    nv = sum(1 for line in open(p) if line.startswith('v '))
                    fh.write(f"{tree}\t{os.path.basename(p)}\t{c.group(1)}\t{n.group(1).strip()}\t{nv}\n")
print('inventory written to', out)
