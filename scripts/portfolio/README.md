# Portfolio design and PDF sources

The main page and seven project decks share Noto Sans KR, navy `#142846`, blue `#315d9f`, pale blue `#c4d9f4`, paper `#fbfcfe`, and pale panels `#f0f4fa`.

- Web styles and responsive type sizes: `css/style.css`.
- Home page and inline category groups: `index.html` (`#works`).
- Each field has a dedicated div in the same page: `#ai`, `#backend`, `#planning`.
- PDF content and reusable layouts: `scripts/portfolio/build_pdfs.py`.
- Source presentations: `project_template/originals/` (unchanged copies).
- Published PDF paths: existing filenames under `project_template/`.
- Font license: `assets/fonts/OFL.txt`.

The decks are portfolio editions: content is condensed and reorganized, original roles and metrics are retained, and the original presentations are preserved separately. Team contributions, individual contributions, measured results and future plans are distinguished. Reference/source appendix pages are intentionally omitted. No original files are deleted.

`project_template/neighborhood-safety-map.pdf` uses the same shared layout and navy palette as the other five decks. Its content and diagrams are defined in `build_safety_map_pdf.py`; the original is preserved under `project_template/originals/`. DB design and Node.js/Nginx setup contributions reflect the owner's confirmation. The shared builder includes this deck. To rebuild or validate only it, pass `neighborhood-safety-map.pdf` as an argument to the relevant script.

## Rebuild

Install the dependencies from `requirements.txt` in your Python environment, then run from the repository root:

```sh
python scripts/portfolio/build_pdfs.py
python scripts/portfolio/verify_pdfs.py
```

`verify_pdfs.py` renders every page into `work/portfolio/pdf-qa/`, checks text extraction and page geometry, and writes a QA manifest. Review the rendered pages after content or layout changes. Output is landscape 960 × 600 points with embedded Korean fonts, page numbers and PDF bookmarks. Type sizes: cover 39 pt, page heading 27 pt, panel heading 18–20 pt, body 10–12 pt, captions 8–9 pt.

If the main page text changes, refresh the small web font subsets:

```sh
python scripts/portfolio/prepare_web_fonts.py
```

Full font files support the PDF rebuild; only the approximately 112 KB web subsets are loaded by the main page.

## Preview

```sh
python -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/`. This is a buildless static site; no framework or bundler is required. Publishing remains through the repository's existing GitHub Pages process.

For a future Java project, add its card inside `#backend` in `index.html`, update its category count, and update the toolkit's related link. Keep the same role / problem / approach / result structure and verify mobile layout before publication.


The hero uses `assets/hero-navy.webp`, a compressed derivative of the existing `assets/bgimg.png`. Project thumbnails are ordinary links to the same PDF as the text links below each card. The main page presents only the seven PDF-backed projects; the web-exercise gallery is no longer displayed.

The safety-map deck includes the owner-supplied complete operating-structure diagram (`assets/safety-map-operating-structure.png`) as its own page, without cropping. It retains the separate database and deployment explanations.


The K-Beauty export strategy deck (`kbeauty-export-strategy.pdf`) is defined in `build_kbeauty_pdf.py` and included by the shared builder. Its source is the owner-provided `AI_seminar_team4_personal` repository and [team presentation](https://docs.google.com/presentation/d/1F7b5ldjC89YLH8Li3YxasQXIow5-31MTGk95QmoZMSQ/edit). Public code: https://github.com/joohyosung/AI_seminar_team4 . The supplied presentation remains linked, without modification. Personal development CV (19.66%), common team comparison (25.19%), and follow-up holdout (27.13%) have different evaluation protocols and must not be conflated. Team models, strategy and hypothetical business results remain explicitly distinguished from personal contributions. No source/reference appendix is added.
