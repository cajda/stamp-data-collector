# Stamp Collector — User Guide

## Overview

Stamp Collector is a desktop application for managing a personal stamp collection. Data is stored in XML format and can also be exported to CSV.

---

## Getting Started

Run the application:

```
python stamp_collector.py
```

---

## File Menu

| Action | Description |
|---|---|
| **New** (Ctrl+N) | Start a new empty collection (prompts if unsaved data exists) |
| **Open...** (Ctrl+O) | Load a collection from an XML file |
| **Save** (Ctrl+S) | Save to the current file (prompts for location if new) |
| **Save As...** | Save to a new XML file |
| **Export to CSV...** | Export the entire collection to a CSV file |

---

## Managing Stamps

### Adding a stamp
1. Click **New stamp** (bottom-left) to clear the form.
2. Fill in the fields on the right panel.
3. Click **Save record** to add it to the list.

### Editing a stamp
1. Select a stamp in the list — the form fills automatically.
2. Make your changes.
3. Click **Save record** to apply them.

### Deleting a stamp
1. Select a stamp in the list.
2. Click **Delete** and confirm the prompt.

---

## Field Reference

| Field | Required | Format / Rules |
|---|---|---|
| **Code** | Yes | Integers only (e.g. `1234`) |
| **Country** | Yes | Select from the dropdown list |
| **Denomination** | No | Free text (e.g. `2c`, `0.50`) |
| **Condition** | Yes | Select from the dropdown list |
| **Perforations** | No | Two integers separated by `x` (e.g. `11x14`) |
| **Watermark** | No | Integer code only (e.g. `7`) |
| **Color(s)** | Yes | Free text (e.g. `red`, `blue and green`) |
| **Notes** | No | Free text, multi-line |

### Condition values
`Mint NH`, `Mint H`, `Very Fine`, `Fine`, `Very Good`, `Good`, `Used`, `CTO`, `Poor`, `Damaged`

---

## Input Rules

- **Code** and **Watermark** fields only accept digits — letters and symbols are blocked at input.
- **Perforations** only accepts digits and the letter `x`, with at most one `x`. On saving, the value must follow the `NxM` pattern (e.g. `11x14`). The field may be left empty.
- Required fields (**Code**, **Country**, **Condition**, **Color(s)**) must be filled before a record can be saved.

---

## File Formats

### XML
The native format. Each stamp is stored as a `<stamp>` element with child elements for each field.

### CSV
Exported via **File → Export to CSV...**. Produces a standard comma-separated file with a header row. Column order: `code, country, denomination, condition, perforations, watermark, colors, notes, created`.
