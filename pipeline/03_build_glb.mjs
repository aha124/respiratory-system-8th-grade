// Step 3: simplify each cleaned mesh with meshoptimizer, then write one GLB
// with meshopt compression.
//
//   node pipeline/03_build_glb.mjs <build dir> [out.glb]
//
// Reads  <build>/stage2/manifest.json and <build>/stage2/<id>.bin  (from step 2)
// Writes models/respiratory.glb and <build>/stage3/simplify_report.json
//
// Error limits (from the brief): small structures < 1 mm, large ones < 2 mm.
// The simplifier gets a much smaller absolute target (0.2 mm small / 0.4 mm large) to keep
// curved surfaces smooth on screen. 05_simplify_check.py measures the real two-sided
// (Hausdorff) distance after export and, if a mesh is over its limit, writes a tighter
// target to <build>/stage3/targets.json and runs this script again.

import fs from 'node:fs';
import path from 'node:path';
import { Document, NodeIO } from '@gltf-transform/core';
import { EXTMeshoptCompression, KHRMeshQuantization } from '@gltf-transform/extensions';
import { quantize, reorder } from '@gltf-transform/functions';
import { MeshoptSimplifier, MeshoptEncoder } from 'meshoptimizer';

const build = process.argv[2] || 'build';
const out = process.argv[3] || 'models/respiratory.glb';
const stage2 = path.join(build, 'stage2');
const manifest = JSON.parse(fs.readFileSync(path.join(stage2, 'manifest.json'), 'utf8'));

// Which error budget each structure gets.
export const SMALL = (s) => s.group === 'airway' || /pulmonary|aorta/.test(s.id);
const limitMm = (s) => (SMALL(s) ? 1.0 : 2.0);
const targetsFile = path.join(build, 'stage3', 'targets.json');
const targets = fs.existsSync(targetsFile) ? JSON.parse(fs.readFileSync(targetsFile, 'utf8')) : {};
const targetMm = (s) => targets[s.id] ?? (SMALL(s) ? 0.2 : 0.4);

// Display colors. Lobes get different tints on purpose so students can tell them apart;
// the app says so. Vessel colors follow the textbook convention (blue = low-oxygen blood,
// red = oxygen-rich blood), which the app also explains.
function colorFor(s) {
  const lobe = {
    right_upper_lobe: [0.93, 0.62, 0.62], right_middle_lobe: [0.96, 0.75, 0.55],
    right_lower_lobe: [0.85, 0.55, 0.70], left_upper_lobe: [0.70, 0.66, 0.92],
    left_lower_lobe: [0.58, 0.76, 0.88],
  }[s.id];
  if (lobe) return lobe;
  if (/cartilage|epiglottis|trachea|bronch|^seg_/.test(s.id)) return [0.80, 0.88, 0.92];
  if (/nasal_cavity|pharynx/.test(s.id)) return [0.91, 0.62, 0.60];
  if (s.group === 'skeleton' || /concha|ethmoid/.test(s.id)) return [0.92, 0.89, 0.80];
  if (s.id === 'diaphragm') return [0.75, 0.36, 0.33];
  if (s.id === 'heart') return [0.66, 0.22, 0.22];
  if (/aorta|pulmonary_veins/.test(s.id)) return [0.85, 0.20, 0.20];
  if (/pulmonary_(trunk|artery)/.test(s.id)) return [0.25, 0.42, 0.85];
  if (s.id === 'esophagus') return [0.84, 0.60, 0.42];
  return [0.8, 0.8, 0.8];
}

function readBin(id) {
  const buf = fs.readFileSync(path.join(stage2, id + '.bin'));
  const nv = buf.readUInt32LE(0), nt = buf.readUInt32LE(4);
  const pos = new Float32Array(buf.buffer.slice(buf.byteOffset + 8, buf.byteOffset + 8 + nv * 12));
  const idx = new Uint32Array(buf.buffer.slice(buf.byteOffset + 8 + nv * 12, buf.byteOffset + 8 + nv * 12 + nt * 12));
  return { pos, idx };
}

// Drop vertices no longer referenced after simplification. Kept vertices keep
// their exact original coordinates.
function compact(pos, idx) {
  const remap = new Int32Array(pos.length / 3).fill(-1);
  let n = 0;
  for (const i of idx) if (remap[i] < 0) remap[i] = n++;
  const p = new Float32Array(n * 3);
  for (let i = 0; i < remap.length; i++) if (remap[i] >= 0) p.set(pos.subarray(i * 3, i * 3 + 3), remap[i] * 3);
  return { pos: p, idx: Uint32Array.from(idx, (i) => remap[i]) };
}

function vertexNormals(pos, idx) {
  const n = new Float32Array(pos.length);
  for (let t = 0; t < idx.length; t += 3) {
    const [a, b, c] = [idx[t] * 3, idx[t + 1] * 3, idx[t + 2] * 3];
    const ux = pos[b] - pos[a], uy = pos[b + 1] - pos[a + 1], uz = pos[b + 2] - pos[a + 2];
    const vx = pos[c] - pos[a], vy = pos[c + 1] - pos[a + 1], vz = pos[c + 2] - pos[a + 2];
    const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx; // area weighted
    for (const k of [a, b, c]) { n[k] += nx; n[k + 1] += ny; n[k + 2] += nz; }
  }
  for (let i = 0; i < n.length; i += 3) {
    const l = Math.hypot(n[i], n[i + 1], n[i + 2]) || 1;
    n[i] /= l; n[i + 1] /= l; n[i + 2] /= l;
  }
  return n;
}

await MeshoptSimplifier.ready;
await MeshoptEncoder.ready;

const doc = new Document();
doc.createBuffer();
const scene = doc.createScene('Respiratory system');
const root = doc.createNode('respiratory_model').setExtras({
  units: 'millimeter', up_axis: '+Y', facing: '+Z (person faces the viewer in a front view)',
  person_right: '-X',
  frame_note: 'Z-Anatomy Blender coordinates (Z-up, meters) rotated to Y-up and multiplied by 1000. Same transform for every structure.',
});
scene.addChild(root);
const groups = {};
const report = [];

for (const s of manifest) {
  let { pos, idx } = readBin(s.id);
  const limit = limitMm(s);
  const target = targetMm(s);
  const [sIdx, err] = target > 0
    ? MeshoptSimplifier.simplify(idx, pos, 3, 0, target, ['LockBorder', 'ErrorAbsolute'])
    : [idx, 0];
  ({ pos, idx } = compact(pos, sIdx));
  report.push({ id: s.id, limit_mm: limit, target_mm: target, simplifier_error_mm: +err.toFixed(4),
    triangles_before: s.triangles, triangles_after: idx.length / 3 });

  const prim = doc.createPrimitive()
    .setAttribute('POSITION', doc.createAccessor().setType('VEC3').setArray(pos))
    .setAttribute('NORMAL', doc.createAccessor().setType('VEC3').setArray(vertexNormals(pos, idx)))
    .setIndices(doc.createAccessor().setType('SCALAR').setArray(idx))
    .setMaterial(doc.createMaterial(s.id).setBaseColorFactor([...colorFor(s), 1])
      .setRoughnessFactor(0.65).setMetallicFactor(0).setDoubleSided(true));
  const mesh = doc.createMesh(s.id).addPrimitive(prim);
  const node = doc.createNode(s.id).setMesh(mesh).setExtras({
    group: s.group, fma_id: s.fma_id, fma_name: s.fma_name,
    source: 'Z-Anatomy ' + s.source_file.join(', '), source_objects: s.source_objects,
  });
  if (!groups[s.group]) { groups[s.group] = doc.createNode('group_' + s.group); root.addChild(groups[s.group]); }
  groups[s.group].addChild(node);
}

// One quantization volume for the whole scene, so every mesh node gets the
// same dequantization transform (nothing is moved relative to anything else).
await doc.transform(
  reorder({ encoder: MeshoptEncoder, target: 'size' }),
  quantize({ quantizationVolume: 'scene', quantizePosition: 16, quantizeNormal: 10 }),
);
doc.createExtension(EXTMeshoptCompression).setRequired(true).setEncoderOptions({ method: EXTMeshoptCompression.EncoderMethod.FILTER });
doc.createExtension(KHRMeshQuantization).setRequired(true);
const io = new NodeIO().registerExtensions([EXTMeshoptCompression, KHRMeshQuantization]).registerDependencies({ 'meshopt.encoder': MeshoptEncoder });
fs.mkdirSync(path.dirname(out), { recursive: true });
await io.write(out, doc);
fs.mkdirSync(path.join(build, 'stage3'), { recursive: true });
fs.writeFileSync(path.join(build, 'stage3', 'simplify_report.json'), JSON.stringify(report, null, 1));
const tb = report.reduce((a, r) => a + r.triangles_before, 0), ta = report.reduce((a, r) => a + r.triangles_after, 0);
console.log(`triangles ${tb} -> ${ta}; wrote ${out} (${(fs.statSync(out).size / 1e6).toFixed(2)} MB)`);
