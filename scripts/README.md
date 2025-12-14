# Scripts

## Gallery foto's optimaliseren (AVIF/WebP/JPEG)

Deze repo gebruikt `images/inner_images/` als bron en zet geoptimaliseerde varianten in `images/inner_images_opt/`.

**Vereisten (macOS):**
- `sips` (standaard aanwezig op macOS)
- `cwebp` (Homebrew: `brew install webp`)
- `avifenc` (Homebrew: `brew install libavif`)

**Run (vanaf repo-root):**
```bash
python3 scripts/optimize-gallery-images.py
```

Optioneel:
```bash
python3 scripts/optimize-gallery-images.py --overwrite
python3 scripts/optimize-gallery-images.py --widths 320,640,960,1600
```

Na toevoegen van nieuwe foto’s in `images/inner_images/`:
1. Draai het script om de varianten te genereren.
2. Voeg de nieuwe foto toe in `fotos.html` (volg het bestaande `<picture>`/`srcset` patroon).

