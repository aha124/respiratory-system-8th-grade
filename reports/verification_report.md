# Verification report

Measured on the decoded `models/respiratory.glb` (what the app displays). Units: mm in the model; shown here in cm or degrees.
Frame: Y up, person faces +Z, person's right is -X.

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

### How each value was measured

- **Trachea length (top of trachea to carina, along its centerline)**: centerline through section centroids from the upper opening (below the cricoid) to the carina.
- **Trachea outer diameter, left-right**: median width of sections perpendicular to the tracheal axis, middle 60 % of length.
- **Trachea outer diameter, front-back**: same sections, front-back depth.
- **Tracheal cartilage rings (raised bands on the trachea surface)**: perimeter of sections every 0.1 mm along the trachea; the grooves between ring bands are perimeter minima (depth at least 0.8 mm, at least 4 mm apart); rings = grooves + 1.
- **Right main bronchus length, from the carina**: along the tube centerline from the carina level to the branch point of the upper lobe bronchus.
- **Right main bronchus length, from the tracheal branch point**: along the tube centerline from the point where the trachea centerline splits to the upper lobe branch point.
- **Left main bronchus length, from the carina**: along the tube centerline from the carina level to its division into upper and lower lobe bronchi.
- **Left main bronchus length, from the tracheal branch point**: along the tube centerline from the point where the trachea centerline splits to its division.
- **Right main bronchus angle from vertical**: angle between the tube centerline and the vertical (Y) axis.
- **Left main bronchus angle from vertical**: angle between the tube centerline and the vertical (Y) axis.
- **Right main bronchus steeper (more vertical) than left**: left angle minus right angle; must be positive.
- **Tracheal bifurcation (carina) vertebral level**: carina height compared with the heights of the vertebral bodies (front 15 mm of each vertebra, within 12 mm of the midline).
- **Right diaphragm dome higher than left**: highest diaphragm point on the person's right (x < -30 mm) minus highest point on the left (x > 30 mm).
- **Right lung apex above the medial third of the clavicle (clavicle center line)**: highest point of the upper lobe minus the mean height of the medial third of the clavicle.
- **Right lung apex above the top edge of the medial third of the clavicle**: highest point of the upper lobe minus the highest point of the medial third of the clavicle.
- **Left lung apex above the medial third of the clavicle (clavicle center line)**: highest point of the upper lobe minus the mean height of the medial third of the clavicle.
- **Left lung apex above the top edge of the medial third of the clavicle**: highest point of the upper lobe minus the highest point of the medial third of the clavicle.
- **Right lung lobe meshes**: count of separate lobe nodes in the GLB.
- **Left lung lobe meshes**: count of separate lobe nodes in the GLB.

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
