#!/usr/bin/env bash
# Fetch the four benchmark files (MuSiQue and 2WikiMultihopQA questions + corpora, as packaged by the HippoRAG 2 authors)
# and clone HippoRAG at the commit used here. Nothing is uploaded. Checks every file against the hashes seen during the run.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data graph
for f in musique musique_corpus 2wikimultihopqa 2wikimultihopqa_corpus; do
  [ -s "data/$f.json" ] || curl -fsSL -o "data/$f.json" "https://huggingface.co/datasets/osunlp/HippoRAG_2/resolve/main/$f.json"
done
sha256sum -c SHA256SUMS.data
[ -d graph/HippoRAG ] || git clone -q https://github.com/OSU-NLP-Group/HippoRAG graph/HippoRAG
git -C graph/HippoRAG checkout -q 2bfd831417202b49cda9da7973e141a456e16872
echo "data and HippoRAG ready"
