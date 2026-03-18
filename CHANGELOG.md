# Changelog

## [2.0] — 2026-03-18

### Added
- **Catalog reference field** — select catalog type (Scott `Sn`, Stanley Gibbons `Sg`, Michel `Mi`) and enter the corresponding catalog number.
- **Watermark image attachment** — browse and attach an image file to document the watermark; thumbnail preview shown in the form (requires Pillow).
- **Stamp image attachment** — browse and attach a scan or photo of the stamp; thumbnail preview shown in the form (requires Pillow).
- Optional Pillow dependency for image thumbnail rendering; application degrades gracefully when Pillow is not installed.
- Renamed application to **Stamp Data Collector**.

### Changed
- `FIELD_KEYS` extended to include `catalog_type`, `catalog_number`, `colors`, `watermark_image`, and `stamp_image` — XML and CSV exports now include these fields.
- About dialog updated to reflect version 2.0.
- USER_GUIDE.md updated to document new fields.

---

## [1.0] — initial release

- Basic stamp collection manager with Tkinter GUI.
- Fields: code, country, denomination, condition, perforations, watermark, colors, notes.
- XML native format with CSV export.
- Input validation for code, watermark (digits only) and perforations (`NxM` format).
