#!/bin/zsh
# Builds the compressed copies the page actually serves from the full-size
# JPEGs in images/ (the JPEGs stay as the originals and the no-AVIF/WebP fallback):
#   portrait.jpg  -> portrait-240/-480 .avif and .webp (the <picture> srcset)
#   <project>.jpg -> <project>-960.webp                (the <video> poster)
# Needs sips (macOS), avifenc and cwebp:  brew install libavif webp
# Run from the repo root after adding or replacing an image:
#   tools/make-images.sh                     # every image
#   tools/make-images.sh images/drone-bench.jpg
# Then set the poster's width/height on its <video> to the new file's size
# (the tests check they match).
set -euo pipefail
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

files=("$@")
(( ${#files} )) || files=(images/*.jpg)

for src in $files; do
  name=${src:t:r}
  if [[ $name == portrait ]]; then
    for w in 240 480; do
      sips -s format png --resampleWidth $w "$src" --out "$tmp/$name.png" >/dev/null
      avifenc -q 60 -s 4 "$tmp/$name.png" "images/$name-$w.avif" >/dev/null
      cwebp -quiet -q 80 -m 6 "$tmp/$name.png" -o "images/$name-$w.webp"
    done
  else
    sips -s format png --resampleWidth 960 "$src" --out "$tmp/$name.png" >/dev/null
    cwebp -quiet -q 80 -m 6 "$tmp/$name.png" -o "images/$name-960.webp"
  fi
  echo "$src: $(ls images/$name-*.* | tr '\n' ' ')"
done
