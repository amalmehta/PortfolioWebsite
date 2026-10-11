#!/bin/zsh
# Builds the AVIF and WebP copies the page serves, at a few widths, from the
# JPEGs in images/. Needs sips (macOS), avifenc (libavif) and cwebp (libwebp):
#   brew install libavif webp
# Run from the repo root after adding or replacing a screenshot:
#   tools/make-images.sh            # every image
#   tools/make-images.sh images/drone-bench.jpg
set -euo pipefail
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

files=("$@")
(( ${#files} )) || files=(images/*.jpg)

for src in $files; do
  name=${src:t:r}
  full=$(sips -g pixelWidth "$src" | awk '/pixelWidth/{print $2}')
  if [[ $name == portrait ]]; then widths=(240 480); else widths=(480 800 1400); fi
  for w in $widths; do
    (( w > full )) && w=$full
    sips -s format png --resampleWidth $w "$src" --out "$tmp/$name.png" >/dev/null
    avifenc -q 60 -s 4 "$tmp/$name.png" "images/$name-$w.avif" >/dev/null
    cwebp -quiet -q 78 -m 6 "$tmp/$name.png" -o "images/$name-$w.webp"
  done
  echo "$src -> ${widths[*]}"
done
