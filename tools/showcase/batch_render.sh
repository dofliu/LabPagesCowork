#!/usr/bin/env bash
# 批次出片：bash tools/showcase/batch_render.sh <papers|projects> <workroot> <mood> id1 id2 ...
# 每支：渲染 → 合成配樂 → 串接 → 轉網頁版（assets/<papers|showcase>/<id>.mp4/.jpg）。可平行：xargs -P2
set -euo pipefail
KIND=$1; ROOTW=$2; MOOD=$3; shift 3
cd "$(dirname "$0")/../.."
DIR=$([ "$KIND" = papers ] && echo papers || echo showcase)
for ID in "$@"; do
  P=tools/showcase/$KIND/$ID; W=$ROOTW/$ID; mkdir -p "$W"
  echo "[$(date +%T)] start $ID"
  python3 tools/showcase/render_scenes.py "$P/storyboard.json" --workdir "$W" > "$W/render.log" 2>&1
  DUR=$(python3 -c "import json;s=json.load(open('$P/storyboard.json'));print(sum(x['duration'] for x in s['scenes'])-s.get('xfade',.6)*(len(s['scenes'])-1))")
  python3 tools/showcase/make_music.py --out "$W/bgm.wav" --duration "$DUR" --mood "$MOOD" --seed "$ID" > /dev/null
  python3 tools/showcase/assemble_video.py "$P/storyboard.json" --workdir "$W" --out "$W/master.mp4" --music "$W/bgm.wav" --loudness -18 > /dev/null
  python3 tools/showcase/make_web.py "$W/master.mp4" --id "$ID" --dir "$DIR" --cover-at 4.5
  echo "[$(date +%T)] done $ID"
done
