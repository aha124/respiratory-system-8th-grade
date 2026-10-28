# License for models/respiratory.glb

`respiratory.glb` is a derivative work of:

- **Z-Anatomy** by Lluís Vinent Juanico and the Z-Anatomy project, CC BY-SA 4.0.
  Source: https://github.com/LluisV/Z-Anatomy, commit `6c7f9016bd5899ac8edafd31b9900c151df42ed6`,
  files `Resources/Models/FBX/VisceralSystem100.fbx`, `SkeletalSystem100.fbx`, `MuscularSystem100.fbx`, `CardioVascular41.fbx`.
- **BodyParts3D**, © The Database Center for Life Science, CC BY-SA 2.1 Japan (Z-Anatomy is built on it; the vocal fold
  meshes FJ2805, FJ2787, FJ2806, FJ2788 come straight from BodyParts3D 4.0, `isa_BP3D_4.0_obj_99.zip`).
  Source: https://dbarchive.biosciencedbc.jp/en/bodyparts3d/

Changes made: selected structures, rotated to Y-up and converted to millimeters (one transform for all),
merged some left/right pairs, removed duplicate/degenerate faces, fixed face winding, simplified
(max error 1 mm small / 2 mm large structures), and meshopt-compressed. The vocal folds were placed with a
rigid transform fitted on the laryngeal cartilages.

The GLB is shared under **CC BY-SA 4.0** (https://creativecommons.org/licenses/by-sa/4.0/).

Attribution text to reuse:

> 3D anatomy: Z-Anatomy (Lluís Vinent Juanico, CC BY-SA 4.0), based on BodyParts3D © The Database Center for Life Science (CC BY-SA 2.1 Japan). Processed for teaching by this project, CC BY-SA 4.0.
