#!/bin/zsh
# Builds the compressed copies the page actually serves from the full-size
# JPEGs in images/ (the JPEGs stay as the originals and the no-AVIF/WebP fallback):
#   portrait.jpg  -> portrait-240/-480 .avif and .webp (the <picture> srcset)
#   <project>.jpg -> <project>-960.avif and .webp      (the card's <picture>, and the poster once it has a clip)
#   with --large, also <project>-<w>.avif and .webp, <w> up to 1600 (a Featured card's bigger srcset candidate)
# Needs sips (macOS), avifenc and cwebp:  brew install libavif webp
# Run from the repo root after adding or replacing an image:
#   tools/make-images.sh                     # every image
#   tools/make-images.sh images/drone-autonomy.jpg
#   tools/make-images.sh --large images/drone-autonomy.jpg   # a Featured project
# Then set the poster's width/height on its <video> to the new file's size
# (the tests check they match).
set -euo pipefail
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

large=0
if [[ ${1:-} == --large ]]; then large=1; shift; fi
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
    avifenc -q 60 -s 4 "$tmp/$name.png" "images/$name-960.avif" >/dev/null
    cwebp -quiet -q 80 -m 6 "$tmp/$name.png" -o "images/$name-960.webp"
    # The large copy is never upscaled: it's 1600 px wide, or the JPEG's own width if that's narrower.
    src_w=$(sips -g pixelWidth "$src" | awk '/pixelWidth/ {print $2}')
    w=$(( src_w < 1600 ? src_w : 1600 ))
    if (( large && w > 960 )); then
      sips -s format png --resampleWidth $w "$src" --out "$tmp/$name.png" >/dev/null
      avifenc -q 60 -s 4 "$tmp/$name.png" "images/$name-$w.avif" >/dev/null
      cwebp -quiet -q 80 -m 6 "$tmp/$name.png" -o "images/$name-$w.webp"
    fi
  fi
  echo "$src: $(ls images/$name-*.* | tr '\n' ' ')"
done
