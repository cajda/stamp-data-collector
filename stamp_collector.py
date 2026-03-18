import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
import os

try:
    from PIL import Image, ImageTk
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

COUNTRIES = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Argentina",
    "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain",
    "Bangladesh", "Belarus", "Belgium", "Belize", "Benin", "Bhutan",
    "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei",
    "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada",
    "Cape Verde", "Central African Republic", "Chad", "Chile", "China",
    "Colombia", "Comoros", "Congo", "Costa Rica", "Croatia", "Cuba",
    "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica",
    "Dominican Republic", "Ecuador", "Egypt", "El Salvador",
    "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia", "Fiji",
    "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana",
    "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana",
    "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia",
    "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan",
    "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kuwait", "Kyrgyzstan",
    "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya",
    "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi",
    "Malaysia", "Maldives", "Mali", "Malta", "Mauritania", "Mauritius",
    "Mexico", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco",
    "Mozambique", "Myanmar", "Namibia", "Nepal", "Netherlands",
    "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea",
    "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama",
    "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland",
    "Portugal", "Qatar", "Romania", "Russia", "Rwanda",
    "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Sierra Leone",
    "Singapore", "Slovakia", "Slovenia", "Somalia", "South Africa",
    "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan",
    "Suriname", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan",
    "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga",
    "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Uganda",
    "Ukraine", "United Arab Emirates", "United Kingdom", "United States",
    "Uruguay", "Uzbekistan", "Venezuela", "Vietnam", "Yemen",
    "Zambia", "Zimbabwe",
]

CONDITIONS = [
    "Mint NH", "Mint H", "Very Fine", "Fine", "Very Good",
    "Good", "Used", "CTO", "Poor", "Damaged",
]

CATALOGS = ["Scott (Sn)", "Stanley Gibbons (Sg)", "Michel (Mi)"]

FIELDS = [
    ("Code:",         "code",         "entry_int"),
    ("Country:",      "country",      "combo_country"),
    ("Denomination:", "denomination", "entry"),
    ("Condition:",    "condition",    "combo_condition"),
    ("Perforations:", "perforations", "entry_perf"),
    ("Watermark:",    "watermark",    "entry_int"),
]
FIELD_KEYS = [f[1] for f in FIELDS] + ["catalog_type", "catalog_number", "colors", "watermark_image", "stamp_image", "notes", "created"]
REQUIRED_FIELDS = ("code", "country", "condition", "colors")


class StampApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stamp Collector")
        self.geometry("960x580")
        self.minsize(720, 460)

        self.current_file = None
        self.stamps = []
        self.selected_index = None

        self._build_menu()
        self._build_ui()
        self._update_title()

    # ── Menu ──────────────────────────────────────────────────────────────────

    def _build_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New",        command=self.file_new,     accelerator="Ctrl+N")
        file_menu.add_command(label="Open...",    command=self.file_open,    accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save",       command=self.file_save,    accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.file_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export to CSV...", command=self.file_export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit",       command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="User Guide", command=self.help_user_guide, accelerator="F1")
        help_menu.add_separator()
        help_menu.add_command(label="About",      command=self.help_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)
        self.bind("<F1>", lambda e: self.help_user_guide())
        self.bind("<Control-n>", lambda e: self.file_new())
        self.bind("<Control-o>", lambda e: self.file_open())
        self.bind("<Control-s>", lambda e: self.file_save())

    def help_about(self):
        messagebox.showinfo(
            "About Stamp Collector",
            "Stamp Collector\nVersion 1.0\n\n"
            "A desktop application for managing\n"
            "a personal stamp collection.\n\n"
            "Data is stored in XML format and\n"
            "can be exported to CSV.",
        )

    def help_user_guide(self):
        guide_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "USER_GUIDE.md")
        win = tk.Toplevel(self)
        win.title("User Guide")
        win.geometry("680x520")
        win.minsize(400, 300)

        text = tk.Text(win, wrap=tk.WORD, padx=10, pady=10, relief=tk.FLAT)
        vsb = ttk.Scrollbar(win, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        try:
            with open(guide_path, encoding="utf-8") as f:
                text.insert("1.0", f.read())
        except FileNotFoundError:
            text.insert("1.0", f"User guide not found:\n{guide_path}")
        text.configure(state=tk.DISABLED)

    # ── UI layout ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # ── Left: stamp list ──
        left = ttk.Frame(paned)
        paned.add(left, weight=2)

        cols = ("code", "country", "denomination", "condition")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("code",         text="Code")
        self.tree.heading("country",      text="Country")
        self.tree.heading("denomination", text="Denomination")
        self.tree.heading("condition",    text="Condition")
        self.tree.column("code",         width=70,  minwidth=50)
        self.tree.column("country",      width=140, minwidth=80)
        self.tree.column("denomination", width=110, minwidth=70)
        self.tree.column("condition",    width=100, minwidth=70)

        vsb = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)


        # ── Right: detail form ──
        right = ttk.LabelFrame(paned, text="Stamp Details", padding=10)
        paned.add(right, weight=1)

        vcmd_int  = (self.register(lambda s: s == "" or s.isdigit()), "%P")
        vcmd_perf = (self.register(
            lambda s: s == "" or (all(c.isdigit() or c == "x" for c in s) and s.count("x") <= 1)
        ), "%P")

        self.vars = {}
        for row, (label, key, wtype) in enumerate(FIELDS):
            ttk.Label(right, text=label).grid(row=row, column=0, sticky=tk.W, pady=3)
            var = tk.StringVar()
            self.vars[key] = var
            if wtype == "entry":
                ttk.Entry(right, textvariable=var, width=30).grid(
                    row=row, column=1, sticky=tk.EW, padx=(8, 0), pady=3)
            elif wtype == "entry_int":
                ttk.Entry(right, textvariable=var, width=30,
                          validate="key", validatecommand=vcmd_int).grid(
                    row=row, column=1, sticky=tk.EW, padx=(8, 0), pady=3)
            elif wtype == "entry_perf":
                ttk.Entry(right, textvariable=var, width=30,
                          validate="key", validatecommand=vcmd_perf).grid(
                    row=row, column=1, sticky=tk.EW, padx=(8, 0), pady=3)
            elif wtype == "combo_country":
                ttk.Combobox(right, textvariable=var, values=COUNTRIES, width=28).grid(
                    row=row, column=1, sticky=tk.EW, padx=(8, 0), pady=3)
            elif wtype == "combo_condition":
                ttk.Combobox(right, textvariable=var, values=CONDITIONS, width=28).grid(
                    row=row, column=1, sticky=tk.EW, padx=(8, 0), pady=3)

        catalog_row = len(FIELDS)
        ttk.Label(right, text="Catalog:").grid(row=catalog_row, column=0, sticky=tk.W, pady=3)
        catalog_frame = ttk.Frame(right)
        catalog_frame.grid(row=catalog_row, column=1, sticky=tk.EW, padx=(8, 0), pady=3)
        catalog_type_var = tk.StringVar()
        self.vars["catalog_type"] = catalog_type_var
        ttk.Combobox(catalog_frame, textvariable=catalog_type_var,
                     values=CATALOGS, width=18).pack(side=tk.LEFT)
        ttk.Label(catalog_frame, text="No:").pack(side=tk.LEFT, padx=(8, 4))
        catalog_number_var = tk.StringVar()
        self.vars["catalog_number"] = catalog_number_var
        ttk.Entry(catalog_frame, textvariable=catalog_number_var, width=10).pack(side=tk.LEFT)

        wm_img_row = len(FIELDS) + 1
        ttk.Label(right, text="Watermark image:").grid(row=wm_img_row, column=0, sticky=tk.W, pady=3)
        wm_img_frame = ttk.Frame(right)
        wm_img_frame.grid(row=wm_img_row, column=1, sticky=tk.EW, padx=(8, 0), pady=3)
        self.watermark_image_var = tk.StringVar()
        wm_entry = ttk.Entry(wm_img_frame, textvariable=self.watermark_image_var,
                             width=20, state="readonly")
        wm_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(wm_img_frame, text="Browse…",
                   command=self._browse_watermark_image).pack(side=tk.LEFT, padx=(4, 0))
        ttk.Button(wm_img_frame, text="Clear",
                   command=self._clear_watermark_image).pack(side=tk.LEFT, padx=(2, 0))

        self._wm_photo = None
        self.wm_preview = ttk.Label(right)
        self.wm_preview.grid(row=wm_img_row + 1, column=1, sticky=tk.W, padx=(8, 0), pady=(0, 3))

        colors_row = len(FIELDS) + 3
        ttk.Label(right, text="Color(s):").grid(row=colors_row, column=0, sticky=tk.W, pady=3)
        colors_var = tk.StringVar()
        self.vars["colors"] = colors_var
        ttk.Entry(right, textvariable=colors_var, width=30).grid(
            row=colors_row, column=1, sticky=tk.EW, padx=(8, 0), pady=3)

        stamp_img_row = len(FIELDS) + 4
        ttk.Label(right, text="Stamp image:").grid(row=stamp_img_row, column=0, sticky=tk.W, pady=3)
        stamp_img_frame = ttk.Frame(right)
        stamp_img_frame.grid(row=stamp_img_row, column=1, sticky=tk.EW, padx=(8, 0), pady=3)
        self.stamp_image_var = tk.StringVar()
        ttk.Entry(stamp_img_frame, textvariable=self.stamp_image_var,
                  width=20, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(stamp_img_frame, text="Browse…",
                   command=self._browse_stamp_image).pack(side=tk.LEFT, padx=(4, 0))
        ttk.Button(stamp_img_frame, text="Clear",
                   command=self._clear_stamp_image).pack(side=tk.LEFT, padx=(2, 0))

        self._stamp_photo = None
        self.stamp_preview = ttk.Label(right)
        self.stamp_preview.grid(row=stamp_img_row + 1, column=1, sticky=tk.W, padx=(8, 0), pady=(0, 3))

        notes_row = len(FIELDS) + 6
        ttk.Label(right, text="Notes:").grid(row=notes_row, column=0, sticky=tk.NW, pady=3)
        notes_wrap = ttk.Frame(right)
        notes_wrap.grid(row=notes_row, column=1, sticky=tk.NSEW, padx=(8, 0), pady=3)
        self.notes_text = tk.Text(notes_wrap, width=28, height=6, wrap=tk.WORD)
        notes_vsb = ttk.Scrollbar(notes_wrap, orient=tk.VERTICAL, command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=notes_vsb.set)
        self.notes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        notes_vsb.pack(side=tk.RIGHT, fill=tk.Y)

        right.columnconfigure(1, weight=1)
        right.rowconfigure(notes_row, weight=1)

        created_row = notes_row + 1
        ttk.Label(right, text="Created:").grid(row=created_row, column=0, sticky=tk.W, pady=3)
        self.created_var = tk.StringVar()
        ttk.Label(right, textvariable=self.created_var, foreground="gray").grid(
            row=created_row, column=1, sticky=tk.W, padx=(8, 0), pady=3)

        form_btns = ttk.Frame(right)
        form_btns.grid(row=notes_row + 2, column=0, columnspan=2, pady=(8, 0), sticky=tk.EW)
        ttk.Button(form_btns, text="New stamp", command=self.action_new).pack(side=tk.LEFT, padx=2)
        ttk.Button(form_btns, text="Delete",    command=self.action_delete).pack(side=tk.LEFT, padx=2)
        ttk.Button(form_btns, text="Clear form",  command=self.action_clear_form).pack(side=tk.RIGHT, padx=2)
        ttk.Button(form_btns, text="Save record", command=self.action_save_record).pack(side=tk.RIGHT, padx=2)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(
            side=tk.BOTTOM, fill=tk.X, padx=6, pady=(0, 3))

    # ── Watermark image helpers ───────────────────────────────────────────────

    def _browse_watermark_image(self):
        path = filedialog.askopenfilename(
            title="Select Watermark Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self.watermark_image_var.set(path)
            self._update_wm_preview(path)

    def _clear_watermark_image(self):
        self.watermark_image_var.set("")
        self._update_wm_preview("")

    def _update_wm_preview(self, path):
        if not path or not os.path.isfile(path):
            self.wm_preview.configure(image="", text="")
            self._wm_photo = None
            return
        if _PIL_AVAILABLE:
            try:
                img = Image.open(path)
                img.thumbnail((120, 120))
                self._wm_photo = ImageTk.PhotoImage(img)
                self.wm_preview.configure(image=self._wm_photo, text="")
                return
            except Exception:
                pass
        # Fallback: show filename only
        self._wm_photo = None
        self.wm_preview.configure(image="", text=os.path.basename(path))

    # ── Stamp image helpers ───────────────────────────────────────────────────

    def _browse_stamp_image(self):
        path = filedialog.askopenfilename(
            title="Select Stamp Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self.stamp_image_var.set(path)
            self._update_stamp_preview(path)

    def _clear_stamp_image(self):
        self.stamp_image_var.set("")
        self._update_stamp_preview("")

    def _update_stamp_preview(self, path):
        if not path or not os.path.isfile(path):
            self.stamp_preview.configure(image="", text="")
            self._stamp_photo = None
            return
        if _PIL_AVAILABLE:
            try:
                img = Image.open(path)
                img.thumbnail((120, 120))
                self._stamp_photo = ImageTk.PhotoImage(img)
                self.stamp_preview.configure(image=self._stamp_photo, text="")
                return
            except Exception:
                pass
        self._stamp_photo = None
        self.stamp_preview.configure(image="", text=os.path.basename(path))

    # ── Tree helpers ──────────────────────────────────────────────────────────

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for i, s in enumerate(self.stamps):
            self.tree.insert("", tk.END, iid=str(i), values=(
                s.get("code", ""), s.get("country", ""),
                s.get("denomination", ""), s.get("condition", ""),
            ))

    def _on_tree_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        self.selected_index = int(sel[0])
        self._load_to_form(self.stamps[self.selected_index])

    def _load_to_form(self, stamp):
        for key, var in self.vars.items():
            var.set(stamp.get(key, ""))
        self.notes_text.delete("1.0", tk.END)
        self.notes_text.insert("1.0", stamp.get("notes", ""))
        self.created_var.set(stamp.get("created", ""))
        wm_img = stamp.get("watermark_image", "")
        self.watermark_image_var.set(wm_img)
        self._update_wm_preview(wm_img)
        st_img = stamp.get("stamp_image", "")
        self.stamp_image_var.set(st_img)
        self._update_stamp_preview(st_img)

    def _read_form(self):
        stamp = {key: var.get().strip() for key, var in self.vars.items()}
        stamp["watermark_image"] = self.watermark_image_var.get().strip()
        stamp["stamp_image"] = self.stamp_image_var.get().strip()
        stamp["notes"] = self.notes_text.get("1.0", tk.END).strip()
        return stamp

    # ── Record actions ────────────────────────────────────────────────────────

    def action_new(self):
        self.selected_index = None
        self.tree.selection_remove(self.tree.selection())
        self.action_clear_form()

    def action_clear_form(self):
        for var in self.vars.values():
            var.set("")
        self.notes_text.delete("1.0", tk.END)
        self.created_var.set("")
        self._clear_watermark_image()
        self._clear_stamp_image()

    def action_save_record(self):
        stamp = self._read_form()
        missing = [f for f in REQUIRED_FIELDS if not stamp.get(f)]
        if missing:
            labels = {"code": "Code", "country": "Country",
                      "condition": "Condition", "colors": "Color(s)"}
            names = ", ".join(labels[f] for f in missing)
            messagebox.showwarning("Validation", f"Required field(s) missing: {names}")
            return
        perf = stamp.get("perforations", "")
        if perf:
            parts = perf.split("x")
            if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
                messagebox.showwarning("Validation", "Perforations must be in the format NxM (e.g. 11x14).")
                return
        if self.selected_index is not None:
            # Preserve the original creation timestamp on edit
            stamp["created"] = self.stamps[self.selected_index].get("created", "")
            self.stamps[self.selected_index] = stamp
        else:
            stamp["created"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.stamps.append(stamp)
            self.selected_index = len(self.stamps) - 1
        self.created_var.set(stamp["created"])
        self._refresh_tree()
        self.tree.selection_set(str(self.selected_index))
        self.tree.see(str(self.selected_index))
        self.status_var.set(f"Saved: {stamp['code']}")

    def action_delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Delete", "Select a stamp first.")
            return
        idx = int(sel[0])
        code = self.stamps[idx].get("code", "?")
        if messagebox.askyesno("Delete", f"Delete stamp '{code}'?"):
            del self.stamps[idx]
            self.selected_index = None
            self._refresh_tree()
            self.action_clear_form()
            self.status_var.set(f"Deleted: {code}")

    # ── File operations ───────────────────────────────────────────────────────

    def file_new(self):
        if self.stamps and not messagebox.askyesno("New", "Discard current data and start a new collection?"):
            return
        self.stamps = []
        self.current_file = None
        self._refresh_tree()
        self.action_clear_form()
        self._update_title()
        self.status_var.set("New collection.")

    def file_open(self):
        path = filedialog.askopenfilename(
            title="Open Stamp Collection",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            self.stamps = _load_xml(path)
            self.current_file = path
            self._refresh_tree()
            self.action_clear_form()
            self._update_title()
            self.status_var.set(
                f"Loaded {len(self.stamps)} stamp(s) from {os.path.basename(path)}")
        except Exception as exc:
            messagebox.showerror("Error", f"Could not open file:\n{exc}")

    def file_save(self):
        if self.current_file:
            self._write_file(self.current_file)
        else:
            self.file_save_as()

    def file_save_as(self):
        path = filedialog.asksaveasfilename(
            title="Save Stamp Collection",
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
        )
        if not path:
            return
        self.current_file = path
        self._write_file(path)
        self._update_title()

    def file_export_csv(self):
        if not self.stamps:
            messagebox.showinfo("Export CSV", "Nothing to export.")
            return
        path = filedialog.asksaveasfilename(
            title="Export to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=FIELD_KEYS)
                writer.writeheader()
                writer.writerows(self.stamps)
            self.status_var.set(f"Exported {len(self.stamps)} stamp(s) to {os.path.basename(path)}")
        except Exception as exc:
            messagebox.showerror("Error", f"Could not export CSV:\n{exc}")

    def _write_file(self, path):
        try:
            xml_str = _build_xml(self.stamps)
            with open(path, "w", encoding="utf-8") as f:
                f.write(xml_str)
            self.status_var.set(f"Saved to {os.path.basename(path)}")
        except Exception as exc:
            messagebox.showerror("Error", f"Could not save file:\n{exc}")

    def _update_title(self):
        name = os.path.basename(self.current_file) if self.current_file else "Untitled"
        self.title(f"Stamp Collector — {name}")


# ── XML helpers ───────────────────────────────────────────────────────────────

def _build_xml(stamps):
    root = ET.Element("stamps")
    for stamp in stamps:
        elem = ET.SubElement(root, "stamp")
        for key in FIELD_KEYS:
            child = ET.SubElement(elem, key)
            child.text = stamp.get(key, "")
    raw = ET.tostring(root, encoding="unicode")
    return minidom.parseString(raw).toprettyxml(indent="  ")


def _load_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()
    stamps = []
    for elem in root.findall("stamp"):
        stamp = {}
        for key in FIELD_KEYS:
            child = elem.find(key)
            stamp[key] = (child.text or "") if child is not None else ""
        stamps.append(stamp)
    return stamps


if __name__ == "__main__":
    app = StampApp()
    app.mainloop()