# The Respiratory System in 3D

An interactive 3D model of the human respiratory system for 8th grade life science. Every surface comes from one real adult body (Z-Anatomy, built on BodyParts3D), kept at real size in millimeters. Nothing was modeled by hand for this project. The whole download is about 1.6 MB (model 0.62 MB), so it loads fine on a school Chromebook.

Students can rotate, zoom and pan; tap any part for its name, Latin name, job and facts; toggle the skeleton, heart and vessels, and esophagus; make the lungs see-through; follow the path of air from nose to alveoli; run a simplified breathing animation; and take a 10-question "Find the ___" quiz scored on first tries.

## Run it

Any static file server works. From this folder:

```
python3 -m http.server 8000
```

Then open http://localhost:8000. Opening `index.html` straight from disk will not work because browsers block `fetch` on `file://`. All libraries are in `vendor/`, so no internet is needed after the files are on the server (GitHub Pages works too).

## What's in the repo

| Path | What it is |
|---|---|
| `index.html`, `css/style.css`, `js/app.js` | The viewer (three.js 0.170.0, GLTFLoader + meshopt decoder, OrbitControls, CSS2D labels) |
| `models/respiratory.glb` | 113 meshes, millimeters, Y up, meshopt compressed. License in `models/LICENSE.md` |
| `data/parts.json` | Every name and piece of text: parts, facts, sources, walkthrough, quiz, notices |
| `pipeline/` | Scripts that rebuild the GLB and the reports from the original downloads |
| `reports/` | Verification report, source inventory, full candidate lists |
| `vendor/three/` | three.js files (MIT, license included) |

## Sources and licenses

**3D data**

- Z-Anatomy, by Lluís Vinent Juanico and the Z-Anatomy project. CC BY-SA 4.0. Repository https://github.com/LluisV/Z-Anatomy, branch `PC-Version`, commit `6c7f9016bd5899ac8edafd31b9900c151df42ed6` (2024-12-25). Files used: `Resources/Models/FBX/VisceralSystem100.fbx`, `SkeletalSystem100.fbx`, `MuscularSystem100.fbx`, `CardioVascular41.fbx`. The included `Resources/Models/License.txt` says these are derived from BodyParts3D.
- BodyParts3D version 4.0, © The Database Center for Life Science (DBCLS), CC BY-SA 2.1 Japan. https://dbarchive.biosciencedbc.jp/en/bodyparts3d/ (files dated 2013-05-22). Used for FMA IDs (`isa_parts_list_e.txt`, `partof_parts_list_e.txt`), for the vocal folds (`isa_BP3D_4.0_obj_99.zip`: FJ2805 right vocal ligament FMA55245, FJ2787 left vocal ligament FMA55246, FJ2806 right vocalis FMA46592, FJ2788 left vocalis FMA46593), and to place them (FJ2808 thyroid, FJ2440 cricoid, FJ2775/FJ2792 arytenoid cartilages).
- three.js 0.170.0, MIT License.

**Attribution text** (shown in the app under "About & credits"; reuse it with the model):

> 3D anatomy: Z-Anatomy (Lluís Vinent Juanico, CC BY-SA 4.0), based on BodyParts3D © The Database Center for Life Science (CC BY-SA 2.1 Japan). Processed for teaching by this project, CC BY-SA 4.0.

Because of the share-alike terms, `models/respiratory.glb` is CC BY-SA 4.0. The code (HTML, CSS, JS, pipeline) carries no license yet; pick one before publishing.

**Fact sources** (every fact in `data/parts.json` lists its own sources, and the app shows them under each part):

- OpenStax, *Anatomy and Physiology 2e*, sections 7.4 (thoracic cage), 19.1 (heart anatomy), 22.1 (organs and structures of the respiratory system), 22.2 (the lungs), 22.3 (the process of breathing), 23.3 (mouth, pharynx, esophagus). https://openstax.org/books/anatomy-and-physiology-2e
- StatPearls (NCBI Bookshelf): Anatomy, Thorax, Lungs (NBK470197); Anatomy, Thorax, Bronchial (NBK537353); Anatomy, Thorax: Diaphragm (NBK519558).
- Radiopaedia: Lingula (lung); Bronchus intermedius.
- Breatnach E, Abbott GC, Fraser RG. Dimensions of the normal human trachea. AJR 1984;142:903-6 (PMID 6609569). Cited only in the verification notes.

Facts that describe this particular body (for example "the right dome is 1.9 cm higher") cite the verification report below.

## Data choices and gaps

Z-Anatomy is the only geometry source, apart from the vocal folds. BodyParts3D 4.0 alone was not usable: it has no lung surface meshes (its "lobes" are only bronchi and blood vessels), no pharynx and no nasal cavity. Z-Anatomy fills those gaps, but it has re-posed and symmetrized the BodyParts3D body (its bones sit 62 to 100 mm away from BodyParts3D's, and not by one shift). So the two can't be mixed freely without moving structures one by one, which the brief forbids.

What could not be sourced, and what was done instead:

1. **Vocal folds.** Not in Z-Anatomy. BodyParts3D has the vocal ligaments and vocalis muscles, but in its own frame. The pipeline fits one rigid transform (no scaling) that maps the BodyParts3D thyroid, cricoid and arytenoid cartilages onto Z-Anatomy's. The fit came out as a pure shift (rotation 0.43°) with a mean surface distance of 0.44 mm, which shows Z-Anatomy's larynx is BodyParts3D's larynx moved as a block. The same transform carries the vocal folds. The app labels them with this provenance. Their soft mucosal covering is not in either dataset.
2. **Tracheal cartilage rings.** Neither dataset has separate ring meshes, but the Z-Anatomy trachea carries the rings as raised bands on its surface (17 counted, 5.7 mm apart). They are visible and counted, not separately clickable.
3. **Superior and middle nasal conchae.** They are part of the ethmoid bone mesh, so they are shown and labeled together with it. The inferior conchae are separate.
4. **Cuneiform cartilages, costal cartilage tips of ribs 11 and 12.** Not in Z-Anatomy; not shown, and the app says so.
5. **Bronchioles and alveoli.** Far below scan resolution. Shown only as a 2D illustration in a separate close-up panel labeled "Illustration, not to scale."
6. **TotalSegmentator fallback.** Not used. Every required structure except the vocal folds exists in Z-Anatomy, and a CT from another person would put a second body into the model.

**Provenance caveat.** The lung lobes, pharynx, nasal cavity lining, main and lobar bronchi, esophagus and diaphragm in Z-Anatomy are quad meshes, while BodyParts3D meshes are triangle meshes. That points to the Z-Anatomy team having rebuilt these surfaces on the BodyParts3D body rather than copying scan-derived meshes unchanged. The bronchi in particular are smooth 17 mm tubes. The layout follows the real body, but these surfaces are a modeler's reconstruction. `reports/source_inventory.md` lists the quad share of every node. The app's About dialog says this in plain words.

**Merges.** Left and right pairs were merged only where students learn them as one thing: inferior conchae, arytenoid cartilages, corniculate cartilages, vocal folds. The four heart chambers became one "heart" node; ascending aorta, arch and thoracic aorta became "aorta"; pulmonary artery and vein branches are grouped per side. Every lobe, every rib, every costal cartilage, every thoracic vertebra, every lobar and segmental bronchus is its own selectable node.

**Colors.** Lobes get different tints so students can tell them apart, and the app says real lungs are all one color. Vessels use the textbook red/blue code for oxygen-rich and oxygen-poor blood, and the app says so.

## Pipeline

Run everything with `bash pipeline/run_pipeline.sh` (environment variables `RAW`, `BUILD`, `PYTHON`). It needs git, curl, unzip, Node 18+ (`npm install` first) and Python 3.13 with `pip install -r pipeline/requirements.txt` (`bpy` is Blender as a Python module and reads the FBX files). The DBCLS server often drops long downloads, so the script resumes them. A full run takes several minutes and reproduces `models/respiratory.glb` and everything in `reports/`.

1. **Download.** Z-Anatomy at the pinned commit; BodyParts3D 4.0 term lists and both OBJ archives.
2. **Extract** (`01_extract_zanatomy.py`, Blender `bpy`). Every mesh object of the four FBX files, in world space, with its parent hierarchy and face statistics. The full candidate list with names, parents and sizes is `reports/zanatomy_objects.tsv` (2,475 objects); BodyParts3D candidates with FMA IDs are in `reports/bp3d_candidates.tsv`.
3. **Select and clean** (`02_select_clean.py`, list in `structures.json`). One transform for everything: Blender Z-up meters to three.js Y-up millimeters (x, y, z) → 1000·(x, z, −y). The person faces +Z and their right side is at −X. Cleaning merges vertices with identical positions, drops zero-area and duplicate triangles, makes winding consistent and points closed surfaces outward. The script asserts every output vertex is an original vertex. This step found and fixed one real processing problem: Z-Anatomy's left-side parts are mirrored copies of the right side, and they came in inside-out (all left ribs and costal cartilages, the left clavicle, the left arytenoid and corniculate cartilages, the left inferior concha).
4. **Vocal folds** (`02b_add_vocal_folds.py`), as described above.
5. **Simplify and compress** (`03_build_glb.mjs`, `05_simplify_check.py`). meshoptimizer simplification with an absolute error target of 0.2 mm (small parts) or 0.4 mm (large parts), then quantization (one quantization volume for the whole scene, so all meshes share one transform) and EXT_meshopt_compression. The check decodes the GLB exactly like the viewer and measures the two-sided Hausdorff distance to the cleaned source. Limits are 1 mm for the airway, larynx, vocal folds, bronchi and pulmonary vessels, and 2 mm for everything else. Any mesh over its limit gets a tighter target and the build reruns. All 113 pass on the first round. Triangles go from 644,293 to about 94,000.
6. **Verify** (`06_verify.py`), measured on the decoded GLB. Report below and in `reports/verification_report.md`.
7. **Inventory** (`07_inventory.py`).

## Verification report

Measured on the decoded `models/respiratory.glb`, which is exactly what the app displays. Status FLAG means outside the reference range; the note says whether that is the source body or processing.

| Check | Measured | Reference | Result | Notes |
|---|---|---|---|---|
| Trachea length (top of trachea to carina, along its centerline) | 11.0 cm | 10-12 cm | **PASS** |  |
| Trachea outer diameter, left-right | 2.2 cm | about 2-2.5 cm | **PASS** |  |
| Trachea outer diameter, front-back | 1.5 cm | about 2-2.5 cm | **FLAG** | Source variation, not processing: the stage-2 (pre-simplification) trachea gives the same value, and the simplified mesh is within 1 mm of it. The Z-Anatomy trachea is flatter front-to-back than left-to-right, which matches the flat back wall (trachealis) of a real trachea; published CT/X-ray adult ranges are wider than the 2-2.5 cm rule of thumb (Breatnach et al. 1984). |
| Tracheal cartilage rings (raised bands on the trachea surface) | 17.0 rings | 16-20 rings | **PASS** | 16 grooves, median ring spacing 5.7 mm, groove depth about 0.46 mm. Rings are surface relief on one trachea mesh, not separate meshes. |
| Right main bronchus length, from the carina | 0.9 cm | about 2.5 cm (checked as 2.0-3.0 cm) | **FLAG** | Source modeling, not processing: Z-Anatomy draws the main and lobar bronchi as smooth 17 mm-wide tubes that start at one shared branch point inside the lower trachea. The tube walls only separate 14 mm lower, which is where this check places the carina, so the right main bronchus looks short from there. Measured from the branch point (next row) it is 2.6 cm. The bronchus meshes are unchanged by simplification (they have under 600 triangles each). |
| Right main bronchus length, from the tracheal branch point | 2.6 cm | about 2.5 cm (checked as 2.0-3.0 cm) | **PASS** |  |
| Left main bronchus length, from the carina | 4.8 cm | about 5 cm (checked as 4.0-6.0 cm) | **PASS** |  |
| Left main bronchus length, from the tracheal branch point | 6.8 cm | about 5 cm (checked as 4.0-6.0 cm) | **FLAG** | Same cause as above, in the other direction: measured from the shared branch point inside the trachea, the left bronchus includes about 2 cm that lies inside the trachea. Measured from the carina it is 4.8 cm (pass). |
| Right main bronchus angle from vertical | 32.2 deg | about 20-30 deg | **FLAG** | Source variation, 2 degrees outside the textbook range. The tube is straight and unchanged by processing. The key teaching fact holds: the right main bronchus is steeper than the left (row below). |
| Left main bronchus angle from vertical | 42.6 deg | about 35-50 deg | **PASS** |  |
| Right main bronchus steeper (more vertical) than left | 10.3 deg difference | right angle < left angle | **PASS** |  |
| Tracheal bifurcation (carina) vertebral level | 1356.2 mm (T4/T5 disc) | T4/T5 (checked as mid-T4 body to mid-T5 body) | **PASS** | carina is at the T4/T5 disc |
| Right diaphragm dome higher than left | 18.9 mm | right dome higher (often by about 1-2 cm) | **PASS** | right dome 1262.0 mm, left dome 1243.1 mm |
| Right lung apex above the medial third of the clavicle (clavicle center line) | 2.6 cm | about 2-3 cm above the medial (inner) third | **PASS** |  |
| Right lung apex above the top edge of the medial third of the clavicle | 1.3 cm | about 2-3 cm above the medial (inner) third | **FLAG** | Depends on the landmark: the sternal (inner) end of the clavicle is its thickest part, so its top edge sits about 1.3 cm above the bone's center line. Measured to the center line (row above) the apex is 2.6 cm higher, inside the range. |
| Left lung apex above the medial third of the clavicle (clavicle center line) | 2.7 cm | about 2-3 cm above the medial (inner) third | **PASS** |  |
| Left lung apex above the top edge of the medial third of the clavicle | 1.5 cm | about 2-3 cm above the medial (inner) third | **FLAG** | Same reason as the right side; 2.7 cm when measured to the clavicle's center line. |
| Right lung lobe meshes | 3.0 lobes | 3 (upper, middle, lower) | **PASS** |  |
| Left lung lobe meshes | 2.0 lobes | 2 (upper, lower) | **PASS** |  |


**Summary of flags.** None of the flags come from processing. The meshes involved are unchanged by simplification (errors under 0.5 mm), and the stage-2 originals give the same numbers.

- The trachea is 1.5 cm front-to-back against a 2 to 2.5 cm rule of thumb. That's the source body; real tracheas are flatter at the back, and published adult ranges are wide.
- Whether the main bronchus lengths pass depends on where you start measuring. Z-Anatomy builds the bronchi as wide tubes joined at one point inside the trachea, 14 mm above where their walls separate. From that branch point, the right bronchus is 2.6 cm (pass); from the wall separation, 0.9 cm. For the left it is the reverse: 4.8 cm from the carina (pass), 6.8 cm from the branch point.
- The right main bronchus angle is 32°, 2° steeper than the 20 to 30° textbook range allows. The teaching point (right steeper than left, by 10°) holds.
- The lung apex is 2.6 to 2.7 cm above the clavicle's center line (pass) but 1.3 to 1.5 cm above its top edge, because the inner end of the clavicle is its thickest part.

**Processing errors found and fixed along the way:** inside-out mirrored left-side meshes (fixed in cleaning). Three errors in the measurement code were also fixed before this report: vertex-average centroids that inflated trachea length to 12.4 cm, vertebral-body detection that included the pedicles, and a peak-based ring counter that double-counted. The ring counter now counts the grooves between rings.

### Simplification error (two-sided Hausdorff distance, cleaned source mesh vs. exported mesh)

All 113 meshes are within their limits. Worst cases:

| Structure | Limit | Measured max | 99th percentile | Triangles (source → exported) |
|---|---|---|---|---|
| costal_cartilage_left_6 | 2 mm | 1.156 mm | 0.478 mm | 8120 → 190 |
| seg_left_upper_b3 | 1 mm | 0.576 mm | 0.228 mm | 3456 → 432 |
| costal_cartilage_left_9 | 2 mm | 1.137 mm | 0.5 mm | 1964 → 246 |
| costal_cartilage_right_6 | 2 mm | 1.126 mm | 0.501 mm | 8120 → 224 |
| nasal_cavity | 1 mm | 0.496 mm | 0.22 mm | 9796 → 2530 |
| seg_right_middle_b5 | 1 mm | 0.485 mm | 0.272 mm | 3168 → 464 |
| seg_right_upper_b3 | 1 mm | 0.478 mm | 0.225 mm | 4896 → 676 |
| seg_right_lower_b8 | 1 mm | 0.47 mm | 0.219 mm | 2880 → 366 |

### Vocal fold placement (BodyParts3D → Z-Anatomy)

Rigid fit of the BodyParts3D thyroid, cricoid and arytenoid cartilages onto the Z-Anatomy ones: rotation 0.429°, translation [3.03, 69.71, -101.24] mm, no scaling. Surface distance after the fit: mean 0.436 mm, 90th percentile 0.86 mm, max 2.035 mm.

## Content rules followed

Text is written for an 8th grade reader: short sentences, everyday words first, then the science term. Each part lists 2 to 4 facts and the sources they come from. On screen the app says that the model shows one real adult body and that people vary, that left and right mean the person's own sides, that breathing is a simplified animation, that bronchioles and alveoli are an illustration not to scale, and why lobes and vessels are colored the way they are.
