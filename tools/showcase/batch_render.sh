#!/usr/bin/env bash
# 批次出片：bash tools/showcase/batch_render.sh <papers|projects> <workroot> <mood> id1 id2 ...
# 每支：渲染 → 合成配樂 → 串接 → 轉網頁版（assets/<papers|showcase>/<id>.mp4/.jpg）。可平行：xargs -P2
# 若 tools/showcase/<kind>/<id>/en/storyboard.json 存在，會接著出英文版 <id>.en.mp4/.en.jpg（同一首配樂）。
# 環境變數 LANGS 可限定：LANGS=en（只出英文）、LANGS=zh（只出中文）；預設兩種都出。
set -euo pipefail
KIND=$1; ROOTW=$2; MOOD=$3; shift 3
cd "$(dirname "$0")/../.."
DIR=$([ "$KIND" = papers ] && echo papers || echo showcase)
LANGS=${LANGS:-zh en}
for ID in "$@"; do
  P=tools/showcase/$KIND/$ID; W=$ROOTW/$ID; mkdir -p "$W"
  echo "[$(date +%T)] start $ID"
  DUR=$(python3 -c "import json;s=json.load(open('$P/storyboard.json'));print(sum(x['duration'] for x in s['scenes'])-s.get('xfade',.6)*(len(s['scenes'])-1))")
  [ -f "$W/bgm.wav" ] || python3 tools/showcase/make_music.py --out "$W/bgm.wav" --duration "$DUR" --mood "$MOOD" --seed "$ID" > /dev/null
  for L in $LANGS; do
    if [ "$L" = zh ]; then SB=$P/storyboard.json; WL=$W; LANGARG=""; else SB=$P/en/storyboard.json; WL=$W/en; LANGARG="--lang en"; fi
    [ -f "$SB" ] || { echo "  (no $L storyboard, skip)"; continue; }
    mkdir -p "$WL"
    python3 tools/showcase/render_scenes.py "$SB" --workdir "$WL" > "$WL/render.log" 2>&1
    python3 tools/showcase/assemble_video.py "$SB" --workdir "$WL" --out "$WL/master.mp4" --music "$W/bgm.wav" --loudness -18 > /dev/null
    python3 tools/showcase/make_web.py "$WL/master.mp4" --id "$ID" --dir "$DIR" --cover-at 4.5 $LANGARG
  done
  echo "[$(date +%T)] done $ID"
done
