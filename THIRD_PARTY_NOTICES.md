# Third-party notices

## HippoRAG

`openie_2wiki.py` reuses prompt text from https://github.com/OSU-NLP-Group/HippoRAG (the system prompt for triple extraction, copied verbatim) and imports its NER prompt module at run time. HippoRAG is released under the MIT licence:

MIT License

Copyright (c) 2025 OSU Natural Language Processing

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


## MuSiQue

The gold answers and answer aliases in `out/` rows come from MuSiQue (Trivedi et al., 2022, "MuSiQue: Multihop Questions via Single-hop Question Composition", https://github.com/StonyBrookNLP/musique), distributed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Changes: only the answer strings are kept, together with ids, scores and generated answers.

## 2WikiMultiHopQA

The gold answers in `out/` rows come from 2WikiMultiHopQA (Ho et al., 2020, https://github.com/Alab-NII/2wikimultihop, repository licence Apache-2.0). The passages behind it are from Wikipedia (CC BY-SA); contributors are listed in each article's history.
