"""Step 1: read Z-Anatomy FBX files with Blender's Python module (bpy) and dump
every mesh object, in world space, to a compressed .npz file.

Run with:  python -I pipeline/01_extract_zanatomy.py <fbx file> <out.npz>

Vertex positions are written exactly as stored in the FBX after Blender applies
each object's world matrix (meters, Blender Z-up). Nothing is scaled or moved here.
"""
import sys, json
import numpy as np
import bpy

fbx, out = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=fbx)
dg = bpy.context.evaluated_depsgraph_get()
arrays, meta = {}, []
for i, o in enumerate(bpy.context.scene.objects):
    if o.type != 'MESH' or len(o.data.vertices) <= 8:
        continue
    polys = o.data.polygons
    quad_fraction = sum(1 for p in polys if len(p.vertices) == 4) / max(1, len(polys))
    me = o.evaluated_get(dg).to_mesh()
    me.transform(o.matrix_world)
    me.calc_loop_triangles()
    V = np.empty(len(me.vertices) * 3, np.float64); me.vertices.foreach_get('co', V)
    F = np.empty(len(me.loop_triangles) * 3, np.int64); me.loop_triangles.foreach_get('vertices', F)
    key = f"m{i}"
    arrays[key + "_v"] = V.reshape(-1, 3).astype(np.float64)
    arrays[key + "_f"] = F.reshape(-1, 3).astype(np.int32)
    mat = o.active_material
    col = list(mat.diffuse_color) if mat else None
    meta.append(dict(key=key, name=o.name, parent=o.parent.name if o.parent else "",
                     material=mat.name if mat else "", color=col,
                     nverts=len(me.vertices), ntris=len(me.loop_triangles),
                     quad_fraction=round(quad_fraction, 3)))
    o.evaluated_get(dg).to_mesh_clear()
arrays["meta"] = np.array(json.dumps(meta))
# Parent links for every object, including empties used as groups.
arrays["hierarchy"] = np.array(json.dumps({o.name: (o.parent.name if o.parent else "")
                                           for o in bpy.context.scene.objects}))
np.savez_compressed(out, **arrays)
print(f"{len(meta)} meshes -> {out}")
