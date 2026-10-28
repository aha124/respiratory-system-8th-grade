#!/usr/bin/env bash
# Rebuild models/respiratory.glb and the reports from the original source data.
#
#   RAW=/path/for/downloads BUILD=build PYTHON=python3 bash pipeline/run_pipeline.sh
#
# Needs: git, curl, unzip, Node 18+ (npm install first), Python 3.13 with
# pipeline/requirements.txt installed (bpy 5.2.3 is Blender as a Python module).
set -euo pipefail
cd "$(dirname "$0")/.."
RAW=${RAW:-raw}
BUILD=${BUILD:-build}
PY=${PYTHON:-python3}
ZA_COMMIT=6c7f9016bd5899ac8edafd31b9900c151df42ed6
BP3D_URL=https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST
mkdir -p "$RAW" "$BUILD/bp3d"

# 1. Download sources ------------------------------------------------------
if [ ! -d "$RAW/z-anatomy/.git" ]; then
  git init -q "$RAW/z-anatomy"
  git -C "$RAW/z-anatomy" fetch -q --depth 1 https://github.com/LluisV/Z-Anatomy "$ZA_COMMIT"
  git -C "$RAW/z-anatomy" checkout -q FETCH_HEAD
fi
test "$(git -C "$RAW/z-anatomy" rev-parse HEAD)" = "$ZA_COMMIT"
fetch() {  # resumable download; the DBCLS server often drops long transfers
  for i in $(seq 1 20); do
    curl -sS -L -C - --speed-limit 5000 --speed-time 30 -o "$RAW/bp3d/$1" "$BP3D_URL/$1" && return 0
    echo "retrying $1 ($i)"; sleep 3
  done
  return 1
}
mkdir -p "$RAW/bp3d"
for f in README_e.html isa_parts_list_e.txt partof_parts_list_e.txt isa_element_parts.txt partof_element_parts.txt \
         isa_BP3D_4.0_obj_99.zip partof_BP3D_4.0_obj_99.zip; do
  if [ -s "$RAW/bp3d/$f" ] && { [ "${f##*.}" != zip ] || unzip -tq "$RAW/bp3d/$f" >/dev/null 2>&1; }; then continue; fi
  fetch "$f"
done
for t in isa partof; do
  [ -d "$RAW/bp3d/$t" ] || (mkdir -p "$RAW/bp3d/$t" && unzip -q "$RAW/bp3d/${t}_BP3D_4.0_obj_99.zip" -d "$RAW/bp3d/$t")
done
cp "$RAW"/bp3d/*_parts_list_e.txt "$BUILD/bp3d/"

# 2. Extract every Z-Anatomy mesh in world space ---------------------------
FBX="$RAW/z-anatomy/Resources/Models/FBX"
for f in VisceralSystem100 SkeletalSystem100 MuscularSystem100 CardioVascular41; do
  "$PY" -I pipeline/01_extract_zanatomy.py "$FBX/$f.fbx" "$BUILD/za_$f.npz"
done

# 3. Select, convert to Y-up mm, clean; add vocal folds ----------------------
"$PY" pipeline/02_select_clean.py "$BUILD"
"$PY" pipeline/02b_add_vocal_folds.py "$BUILD" "$RAW/bp3d/isa/isa_BP3D_4.0_obj_99"

# 4. Simplify + compress + check simplification error ----------------------
"$PY" pipeline/05_simplify_check.py "$BUILD"

# 5. Anatomical verification and inventory ----------------------------------
"$PY" pipeline/06_verify.py "$BUILD"
"$PY" pipeline/07_inventory.py "$BUILD" "$RAW/bp3d"
ls -l models/respiratory.glb
