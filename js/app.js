// Respiratory system viewer. All names and teaching text live in data/parts.json;
// the geometry lives in models/respiratory.glb (millimeters, Y up, person faces +Z,
// person's right = -X). This file only wires them together.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';

const $ = (id) => document.getElementById(id);
const viewerEl = $('viewer');

// ---------------------------------------------------------------- theme
const THEME_KEY = 'resp3d-theme';
function storedTheme() { try { return localStorage.getItem(THEME_KEY); } catch { return null; } }
function applyTheme(t) {
  if (t) document.documentElement.dataset.theme = t; else delete document.documentElement.dataset.theme;
  const dark = getComputedStyle(document.documentElement).colorScheme === 'dark';
  $('btn-theme').textContent = dark ? 'Light mode' : 'Dark mode';
  if (renderer) scene.background = new THREE.Color(getComputedStyle(document.documentElement).getPropertyValue('--viewer-bg').trim());
}
$('btn-theme').addEventListener('click', () => {
  const dark = getComputedStyle(document.documentElement).colorScheme === 'dark';
  const next = dark ? 'light' : 'dark';
  try { localStorage.setItem(THEME_KEY, next); } catch { /* storage may be blocked */ }
  applyTheme(next);
});
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => applyTheme(storedTheme()));

// ---------------------------------------------------------------- three.js setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, 1, 5, 20000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
viewerEl.appendChild(renderer.domElement);
const labelRenderer = new CSS2DRenderer();
labelRenderer.domElement.style.position = 'absolute';
labelRenderer.domElement.style.inset = '0';
labelRenderer.domElement.style.pointerEvents = 'none';
viewerEl.appendChild(labelRenderer.domElement);
applyTheme(storedTheme());

scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8a99, 1.6));
const keyLight = new THREE.DirectionalLight(0xffffff, 1.6);
keyLight.position.set(0.4, 0.8, 1);
camera.add(keyLight);
scene.add(camera);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.screenSpacePanning = true;
controls.touches = { ONE: THREE.TOUCH.ROTATE, TWO: THREE.TOUCH.DOLLY_PAN };

function resize() {
  const w = viewerEl.clientWidth, h = viewerEl.clientHeight;
  renderer.setSize(w, h); labelRenderer.setSize(w, h);
  camera.aspect = w / h; camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(viewerEl);
resize();

// ---------------------------------------------------------------- state
let data, root;
const meshes = {};            // id -> THREE.Mesh
const groups = {};            // group name -> THREE.Object3D
const labels = [];            // CSS2DObjects tied to a part
let selected = null, focusSet = new Set();
let lungOpacity = 1;
let mode = 'explore';         // 'explore' | 'tour' | 'quiz'
const HIGHLIGHT = new THREE.Color(0xffc400);
const LUNG_IDS = ['right_upper_lobe', 'right_middle_lobe', 'right_lower_lobe', 'left_upper_lobe', 'left_lower_lobe'];

// ---------------------------------------------------------------- load
const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
const [json, gltf] = await Promise.all([
  fetch('data/parts.json').then((r) => r.json()),
  loader.loadAsync('models/respiratory.glb', (e) => {
    if (e.total) $('loading-pct').textContent = Math.round((100 * e.loaded) / e.total) + '%';
  }),
]);
data = json;
root = gltf.scene;
scene.add(root);
root.updateMatrixWorld(true);
root.traverse((o) => {
  if (o.isMesh) {
    meshes[o.name] = o;
    o.material = o.material.clone();
    o.userData.baseColor = o.material.color.clone();
  } else if (o.name.startsWith('group_')) {
    groups[o.name.slice(6)] = o;
  }
});
$('loading').remove();
fillStaticText();

// Bounding boxes in world space (mm).
const boxOf = (ids) => {
  const b = new THREE.Box3();
  ids.forEach((id) => meshes[id] && meshes[id].visible !== false && b.expandByObject(meshes[id]));
  return b;
};
const lungBox = boxOf(LUNG_IDS);
const airwayIds = Object.keys(meshes).filter((id) => meshes[id].userData.group === 'airway');
const homeBox = boxOf([...LUNG_IDS, ...airwayIds]);
const homeCenter = homeBox.getCenter(new THREE.Vector3());
const homeSize = homeBox.getSize(new THREE.Vector3());

// ---------------------------------------------------------------- camera
const VIEWS = {
  front: new THREE.Vector3(0, 0, 1), back: new THREE.Vector3(0, 0, -1),
  side: new THREE.Vector3(-1, 0, 0), // from the person's right side
  top: new THREE.Vector3(0, 1, 0.001), reset: new THREE.Vector3(0.35, 0.15, 1),
};
let camAnim = null;
function fitDistance(size) {
  const r = size.length() / 2;
  const fov = THREE.MathUtils.degToRad(camera.fov);
  const fit = r / Math.sin(Math.min(fov, 2 * Math.atan(Math.tan(fov / 2) * camera.aspect)) / 2);
  return fit * 1.1;
}
function flyTo(target, dir, dist, ms = 700) {
  const toPos = target.clone().add(dir.clone().normalize().multiplyScalar(dist));
  camAnim = { t0: performance.now(), ms, fromPos: camera.position.clone(), fromTgt: controls.target.clone(), toPos, toTgt: target.clone() };
}
function setView(name, box) {
  const b = box || homeBox;
  flyTo(b.getCenter(new THREE.Vector3()), VIEWS[name], fitDistance(b.getSize(new THREE.Vector3())));
}
camera.position.copy(homeCenter.clone().add(VIEWS.reset.clone().normalize().multiplyScalar(fitDistance(homeSize))));
controls.target.copy(homeCenter);
controls.minDistance = 30; controls.maxDistance = fitDistance(homeSize) * 4;
document.querySelectorAll('[data-view]').forEach((b) => b.addEventListener('click', () => setView(b.dataset.view)));
function focusOn(ids, viewName) {
  const b = boxOf(ids);
  if (b.isEmpty()) return;
  const dir = viewName ? VIEWS[viewName] : camera.position.clone().sub(controls.target);
  const size = b.getSize(new THREE.Vector3());
  flyTo(b.getCenter(new THREE.Vector3()), dir, Math.max(fitDistance(size) * 1.3, 90));
}

// ---------------------------------------------------------------- appearance
function setLungOpacity(v) {
  lungOpacity = v;
  $('lung-opacity').value = Math.round(v * 100);
  LUNG_IDS.forEach((id) => {
    const m = meshes[id].material;
    m.opacity = v; m.transparent = v < 1; m.depthWrite = v >= 1;
    meshes[id].renderOrder = v < 1 ? 2 : 0;
  });
}
$('lung-opacity').addEventListener('input', (e) => setLungOpacity(e.target.value / 100));

function paint() {
  for (const [id, m] of Object.entries(meshes)) {
    const hot = id === selected || focusSet.has(id);
    m.material.emissive.copy(hot ? HIGHLIGHT : new THREE.Color(0));
    m.material.emissiveIntensity = hot ? 0.45 : 0;
  }
}

// Layers
const layerState = {};
for (const layer of data.layers) {
  layerState[layer.id] = layer.on;
  const lab = document.createElement('label'); lab.className = 'check';
  lab.innerHTML = `<input type="checkbox" ${layer.on ? 'checked' : ''}> ${layer.label}`;
  lab.querySelector('input').addEventListener('change', (e) => setLayer(layer.id, e.target.checked));
  lab.querySelector('input').dataset.layer = layer.id;
  $('layers').appendChild(lab);
}
function setLayer(id, on) {
  layerState[id] = on;
  const layer = data.layers.find((l) => l.id === id);
  layer.groups.forEach((g) => groups[g] && (groups[g].visible = on));
  document.querySelector(`[data-layer="${id}"]`).checked = on;
  updateLabelVisibility();
}

// ---------------------------------------------------------------- labels
function anchorOf(mesh) {
  // the mesh vertex closest to the middle of its bounding box, in world space
  const c = new THREE.Box3().setFromObject(mesh).getCenter(new THREE.Vector3());
  const pos = mesh.geometry.attributes.position, v = new THREE.Vector3(), best = new THREE.Vector3();
  let bd = Infinity;
  for (let i = 0; i < pos.count; i += 3) {
    v.fromBufferAttribute(pos, i).applyMatrix4(mesh.matrixWorld);
    const d = v.distanceToSquared(c);
    if (d < bd) { bd = d; best.copy(v); }
  }
  return best;
}
function makeLabel(text, cls, onClick) {
  const el = document.createElement('div');
  el.className = 'label ' + (cls || '');
  el.textContent = text;
  if (onClick) { el.style.pointerEvents = 'auto'; el.addEventListener('click', onClick); }
  return new CSS2DObject(el);
}
for (const [id, p] of Object.entries(data.parts)) {
  if (!p.label || !meshes[id]) continue;
  const l = makeLabel(p.short, '', () => select(id));
  l.position.copy(anchorOf(meshes[id]));
  l.userData.part = id;
  scene.add(l); labels.push(l);
}
for (const lm of data.landmarks) {
  const l = makeLabel(lm.label, 'landmark', () => select(lm.part));
  l.position.fromArray(lm.position);
  l.userData.part = lm.part;
  scene.add(l); labels.push(l);
}
const sideY = homeCenter.y;
const rightMark = makeLabel("Person's RIGHT", 'side'); rightMark.position.set(homeBox.min.x - 40, sideY, homeCenter.z);
const leftMark = makeLabel("Person's LEFT", 'side'); leftMark.position.set(homeBox.max.x + 40, sideY, homeCenter.z);
scene.add(rightMark, leftMark); labels.push(rightMark, leftMark);
let labelsOn = window.innerWidth > 760; // phones start with labels off to avoid clutter
$('toggle-labels').checked = labelsOn;
function isShown(o) { for (let p = o; p; p = p.parent) if (p.visible === false) return false; return true; }
function updateLabelVisibility() {
  for (const l of labels) {
    const part = l.userData.part;
    l.visible = labelsOn && mode !== 'quiz' && (!part || isShown(meshes[part]));
  }
}
$('toggle-labels').addEventListener('change', (e) => { labelsOn = e.target.checked; updateLabelVisibility(); });

// Fade labels whose point is hidden behind another solid part.
const occRay = new THREE.Raycaster();
function updateOcclusion() {
  const solid = Object.values(meshes).filter((m) => isShown(m) && !(LUNG_IDS.includes(m.name) && lungOpacity < 0.6));
  for (const l of labels) {
    if (!l.visible || !l.userData.part) continue;
    const dir = l.position.clone().sub(camera.position), dist = dir.length();
    occRay.set(camera.position, dir.normalize()); occRay.far = dist - 3;
    const hit = occRay.intersectObjects(solid, false).find((h) => h.object.name !== l.userData.part);
    l.element.classList.toggle('behind', Boolean(hit));
  }
  // The person's left/right markers only make sense from the front or back.
  const look = controls.target.clone().sub(camera.position).normalize();
  rightMark.visible = leftMark.visible = labelsOn && mode !== 'quiz' && Math.abs(look.z) > 0.6;
}
setInterval(updateOcclusion, 250);

// ---------------------------------------------------------------- part list + info panel
const sel = $('part-select');
for (const [g, gname] of Object.entries(data.groups)) {
  const og = document.createElement('optgroup'); og.label = gname;
  Object.keys(data.parts).filter((id) => meshes[id]?.userData.group === g).forEach((id) => {
    const o = document.createElement('option'); o.value = id; o.textContent = data.parts[id].common; og.appendChild(o);
  });
  sel.appendChild(og);
}
sel.addEventListener('change', () => { if (sel.value) { select(sel.value); focusOn([sel.value]); } });

function sourceLinks(keys) {
  return keys.map((k) => data.sources[k]).filter(Boolean)
    .map((s) => `<a href="${s.url}" target="_blank" rel="noopener">${s.title}</a>`).join('; ');
}
function showInfo(id) {
  const p = data.parts[id], u = meshes[id].userData;
  $('info-name').textContent = p.common;
  $('info-latin').textContent = p.latin;
  $('info-function').textContent = p.function;
  $('info-facts').replaceChildren(...p.facts.map((f) => Object.assign(document.createElement('li'), { textContent: f })));
  $('info-sources').innerHTML = 'Sources: ' + sourceLinks(p.sources);
  const fma = u.fma_id ? `FMA ${u.fma_id}` : 'no FMA ID in the BodyParts3D lists';
  $('info-model').textContent = `Model data: ${u.source}; ${fma}. ${data.meta.one_body}`;
  $('info').hidden = false;
}
$('info-close').addEventListener('click', () => { $('info').hidden = true; select(null); });

function select(id) {
  if (mode === 'quiz') { if (id) quizAnswer(id); return; }
  selected = id; paint();
  if (id) { showInfo(id); sel.value = id; }
}

// ---------------------------------------------------------------- picking
const ray = new THREE.Raycaster();
let downAt = null;
renderer.domElement.addEventListener('pointerdown', (e) => { downAt = [e.clientX, e.clientY]; });
renderer.domElement.addEventListener('pointerup', (e) => {
  if (!downAt || Math.hypot(e.clientX - downAt[0], e.clientY - downAt[1]) > 6) return;
  const r = renderer.domElement.getBoundingClientRect();
  ray.setFromCamera(new THREE.Vector2(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1), camera);
  const all = Object.values(meshes).filter(isShown);
  // When the lungs are see-through, clicks go to what is inside them first.
  const seeThrough = lungOpacity < 0.6;
  let hits = ray.intersectObjects(seeThrough ? all.filter((m) => !LUNG_IDS.includes(m.name)) : all, false);
  if (!hits.length && seeThrough) hits = ray.intersectObjects(all, false);
  if (hits.length) select(hits[0].object.name);
});

// ---------------------------------------------------------------- breathing (simplified)
const BREATH_MM = 15, BREATH_PERIOD = 5000;   // diaphragm moves 1.5 cm; 12 breaths a minute
let breathing = false, breathT0 = 0;
const lungGroup = groups.lungs, diaGroup = groups.diaphragm;
lungGroup.matrixAutoUpdate = false; diaGroup.matrixAutoUpdate = false;
const pivot = new THREE.Vector3((lungBox.min.x + lungBox.max.x) / 2, lungBox.max.y, (lungBox.min.z + lungBox.max.z) / 2);
const lungH = lungBox.max.y - lungBox.min.y;
function setBreath(s) { // s in [0,1]: 0 = breathed out, 1 = breathed in
  const sy = 1 + (BREATH_MM * s) / lungH, sxz = 1 + 0.03 * s;
  lungGroup.matrix.makeTranslation(pivot.x, pivot.y, pivot.z)
    .multiply(new THREE.Matrix4().makeScale(sxz, sy, sxz))
    .multiply(new THREE.Matrix4().makeTranslation(-pivot.x, -pivot.y, -pivot.z));
  diaGroup.matrix.makeTranslation(0, -BREATH_MM * s, 0);
  lungGroup.matrixWorldNeedsUpdate = diaGroup.matrixWorldNeedsUpdate = true;
}
$('toggle-breath').addEventListener('change', (e) => {
  breathing = e.target.checked; breathT0 = performance.now();
  $('breath-badge').hidden = !breathing;
  if (!breathing) setBreath(0);
});

// ---------------------------------------------------------------- path of air walkthrough
let step = 0;
function showStep(i) {
  step = i;
  const s = data.walkthrough[i];
  $('tour-title').textContent = s.title; $('tour-text').textContent = s.text;
  $('tour-step').textContent = `${i + 1} / ${data.walkthrough.length}`;
  $('tour-prev').disabled = i === 0;
  $('tour-next').textContent = i === data.walkthrough.length - 1 ? 'Finish' : 'Next';
  focusSet = new Set(s.focus); selected = null; paint();
  for (const [id, on] of Object.entries(tourLayers)) setLayer(id, on);
  if (s.layers) for (const [id, on] of Object.entries(s.layers)) setLayer(id, on);
  setLungOpacity(s.lungOpacity ?? 1);
  if (s.focus.length) { focusOn(s.focus, s.view); $('closeup').hidden = true; }
  if (s.illustration) { openCloseup(s.illustration); $('closeup').scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
}
let tourLayers = {};
$('btn-tour').addEventListener('click', () => {
  if (mode === 'quiz') endQuiz();
  mode = 'tour'; tourLayers = { ...layerState };
  $('tour').hidden = false; $('info').hidden = true; showStep(0);
  $('tour').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
});
$('tour-prev').addEventListener('click', () => showStep(Math.max(0, step - 1)));
$('tour-next').addEventListener('click', () => (step < data.walkthrough.length - 1 ? showStep(step + 1) : closeTour()));
$('tour-close').addEventListener('click', closeTour);
function closeTour() {
  mode = 'explore'; $('tour').hidden = true; $('closeup').hidden = true;
  for (const [id, on] of Object.entries(tourLayers)) setLayer(id, on);
  setLungOpacity(1); focusSet = new Set(); paint(); setView('reset');
}

// ---------------------------------------------------------------- close-up illustration
function openCloseup(which) {
  $('closeup').hidden = false;
  document.querySelectorAll('[data-ill]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.ill === which)));
  $('ill-bronchioles').style.display = which === 'bronchioles' ? '' : 'none';
  $('ill-alveoli').style.display = which === 'alveoli' ? '' : 'none';
  const ill = data.illustration[which];
  $('closeup-caption').textContent = ill.caption;
  $('closeup-sources').innerHTML = 'Sources: ' + sourceLinks(ill.sources);
}
document.querySelectorAll('[data-ill]').forEach((b) => b.addEventListener('click', () => openCloseup(b.dataset.ill)));
$('btn-closeup').addEventListener('click', () => { openCloseup('alveoli'); $('closeup').scrollIntoView({ behavior: 'smooth', block: 'nearest' }); });
$('closeup-close').addEventListener('click', () => { $('closeup').hidden = true; });

// ---------------------------------------------------------------- quiz
let q = 0, score = 0, firstTry = true, savedLayers = null;
function startQuiz() {
  if (mode === 'tour') closeTour();
  mode = 'quiz'; q = 0; score = 0;
  savedLayers = { ...layerState };
  $('info').hidden = true; selected = null; focusSet = new Set(); paint();
  $('quiz-bar').hidden = false; updateLabelVisibility(); askQuestion();
}
function askQuestion() {
  const item = data.quiz[q];
  firstTry = true;
  $('quiz-prompt').textContent = `${q + 1}. ${item.prompt}`;
  $('quiz-feedback').textContent = 'Tap or click the part on the model.'; $('quiz-feedback').className = '';
  $('quiz-score').textContent = `Score: ${score} / ${q}`;
  $('quiz-next').hidden = true;
  for (const [id, on] of Object.entries(savedLayers)) setLayer(id, on);
  if (item.layers) for (const [id, on] of Object.entries(item.layers)) setLayer(id, on);
  setLungOpacity(item.lungOpacity ?? 1);
  setView(item.view || 'front');
  focusSet = new Set(); paint();
}
function quizAnswer(id) {
  const item = data.quiz[q];
  if (!$('quiz-next').hidden) return; // already answered
  if (item.answers.includes(id)) {
    if (firstTry) score++;
    $('quiz-feedback').textContent = firstTry ? 'Correct on the first try!' : `Yes, that's it. (Only first tries count toward the score.)`;
    $('quiz-feedback').className = 'good';
    focusSet = new Set(item.answers); paint();
    $('quiz-score').textContent = `Score: ${score} / ${q + 1}`;
    $('quiz-next').hidden = false;
    $('quiz-next').textContent = q === data.quiz.length - 1 ? 'See score' : 'Next';
  } else {
    firstTry = false;
    $('quiz-feedback').textContent = `Not quite: that's the ${data.parts[id].common}. Try again.`;
    $('quiz-feedback').className = 'bad';
  }
}
$('quiz-next').addEventListener('click', () => {
  if (q < data.quiz.length - 1) { q++; askQuestion(); return; }
  $('quiz-prompt').textContent = `You found ${score} of ${data.quiz.length} on the first try.`;
  $('quiz-feedback').textContent = score === data.quiz.length ? 'Perfect score!' : 'Explore the model and try again to beat your score.';
  $('quiz-feedback').className = '';
  $('quiz-next').hidden = true; $('quiz-score').textContent = '';
});
function endQuiz() {
  mode = 'explore'; $('quiz-bar').hidden = true;
  if (savedLayers) for (const [id, on] of Object.entries(savedLayers)) setLayer(id, on);
  setLungOpacity(1); focusSet = new Set(); paint(); updateLabelVisibility();
}
$('btn-quiz').addEventListener('click', startQuiz);
$('quiz-exit').addEventListener('click', () => { endQuiz(); setView('reset'); });

// ---------------------------------------------------------------- about + static text
function fillStaticText() {
  const m = json.meta;
  $('app-title').textContent = m.title;
  $('note-body').textContent = m.one_body;
  $('note-lr').textContent = m.left_right;
  $('card-body').textContent = m.one_body;
  $('card-lr').textContent = m.left_right;
  $('legend-lobes').textContent = m.lobe_colors;
  $('legend-vessels').textContent = m.vessel_colors;
  $('breath-badge').textContent = m.breathing_label;
  $('closeup-tag').textContent = m.illustration_label;
  $('about-body').textContent = m.one_body;
  $('about-lr').textContent = m.left_right;
  const li = (t) => Object.assign(document.createElement('li'), { textContent: t });
  $('about-missing').replaceChildren(...m.missing.map(li));
  $('about-attribution').replaceChildren(...m.attribution.map(li));
  $('about-sources').innerHTML = Object.values(json.sources)
    .map((s) => `<li><a href="${s.url}" target="_blank" rel="noopener">${s.title}</a></li>`).join('');
  document.querySelectorAll('[data-label]').forEach((t) => { t.textContent = json.illustration.labels[t.dataset.label]; });
}
$('btn-about').addEventListener('click', () => $('about').showModal());

// ---------------------------------------------------------------- loop
updateLabelVisibility();
renderer.setAnimationLoop((now) => {
  if (camAnim) {
    const k = Math.min(1, (now - camAnim.t0) / camAnim.ms), e = k * k * (3 - 2 * k);
    camera.position.lerpVectors(camAnim.fromPos, camAnim.toPos, e);
    controls.target.lerpVectors(camAnim.fromTgt, camAnim.toTgt, e);
    if (k === 1) camAnim = null;
  }
  if (breathing) setBreath((1 - Math.cos((2 * Math.PI * (now - breathT0)) / BREATH_PERIOD)) / 2);
  controls.update();
  renderer.render(scene, camera);
  labelRenderer.render(scene, camera);
});
window.__app = { meshes, data, select, setView, setLungOpacity, startQuiz }; // for automated checks
