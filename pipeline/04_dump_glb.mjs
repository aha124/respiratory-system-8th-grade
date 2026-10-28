// Step 4 (helper for verification): decode the exported GLB exactly as a viewer
// would (meshopt + dequantization + node transforms) and dump world-space
// triangles per node, so 05_verify.py measures what students will actually see.
//
//   node pipeline/04_dump_glb.mjs models/respiratory.glb build/export
import fs from 'node:fs';
import path from 'node:path';
import { NodeIO } from '@gltf-transform/core';
import { EXTMeshoptCompression, KHRMeshQuantization } from '@gltf-transform/extensions';
import { MeshoptDecoder } from 'meshoptimizer';

const [src = 'models/respiratory.glb', outDir = 'build/export'] = process.argv.slice(2);
await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions([EXTMeshoptCompression, KHRMeshQuantization])
  .registerDependencies({ 'meshopt.decoder': MeshoptDecoder });
const doc = await io.read(src);
fs.mkdirSync(outDir, { recursive: true });
const index = [];
for (const node of doc.getRoot().listNodes()) {
  const mesh = node.getMesh();
  if (!mesh) continue;
  const m = node.getWorldMatrix();
  for (const prim of mesh.listPrimitives()) {
    const acc = prim.getAttribute('POSITION');
    const n = acc.getCount(), el = [0, 0, 0];
    const pos = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) {
      acc.getElement(i, el); // dequantized (normalized ints -> floats)
      const [x, y, z] = el;
      pos[i * 3] = m[0] * x + m[4] * y + m[8] * z + m[12];
      pos[i * 3 + 1] = m[1] * x + m[5] * y + m[9] * z + m[13];
      pos[i * 3 + 2] = m[2] * x + m[6] * y + m[10] * z + m[14];
    }
    const idx = Uint32Array.from(prim.getIndices().getArray());
    const head = Buffer.alloc(8); head.writeUInt32LE(n, 0); head.writeUInt32LE(idx.length / 3, 4);
    fs.writeFileSync(path.join(outDir, node.getName() + '.bin'),
      Buffer.concat([head, Buffer.from(pos.buffer), Buffer.from(idx.buffer)]));
    index.push({ id: node.getName(), extras: node.getExtras(), vertices: n, triangles: idx.length / 3 });
  }
}
fs.writeFileSync(path.join(outDir, 'index.json'), JSON.stringify(index, null, 1));
console.log(`dumped ${index.length} meshes to ${outDir}`);
