#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Γεννήτρια HTML υπογραφής email (για Roundcube κ.ά.)
Εκτέλεση:  python signature_generator.py
Απαιτεί μόνο την τυπική βιβλιοθήκη της Python (tkinter).
"""

import html
import os
import tempfile
import tkinter as tk
import webbrowser
from tkinter import colorchooser, filedialog, messagebox, ttk

DEFAULT_LOGO = "https://ndpf.gr/wp-content/uploads/2026/11/EMBLHMA_transparent-scaled.png"
DEFAULT_ACCENT = "#1f3a6e"

STYLES = [
    "Κλασική",
    "Κάθετη γραμμή",
    "Λογότυπο από πάνω",
    "Μοντέρνα (χρώμα τίτλου)",
]


def esc(text: str) -> str:
    return html.escape(text.strip(), quote=True)


def build_signature(d: dict) -> str:
    """Δημιουργεί τον HTML κώδικα της υπογραφής από τα δεδομένα της φόρμας."""
    style = d["style"]
    accent = d["accent"].strip() or DEFAULT_ACCENT
    use_emoji = d["emoji"]
    width = d["logo_width"].strip() or "80"

    # --- Λίστα γραμμών: (στυλ, εσωτερικό HTML) ---
    name_style = "font-size: 15px; font-weight: bold"
    unit_style = ""
    if style == STYLES[3]:
        name_style += f"; color: {accent}"
        unit_style = "color: #555555"

    items = []
    if d["name"].strip():
        items.append((name_style, esc(d["name"])))
    if d["unit"].strip():
        items.append((unit_style, esc(d["unit"])))
    if d["phone"].strip():
        items.append(("", esc(d["phone"])))
    if d["email"].strip():
        mail = esc(d["email"])
        icon = "✉️<span> </span>" if use_emoji else "<b>E:</b><span> </span>"
        items.append(("", f'{icon}<a style="color: #000000" href="mailto:{mail}">{mail}</a>'))
    if d["website"].strip():
        url = d["website"].strip()
        href = url if url.lower().startswith(("http://", "https://")) else "https://" + url
        label = url.split("://", 1)[-1]
        icon = "🌐<span> </span>" if use_emoji else "<b>W:</b><span> </span>"
        items.append(("", f'{icon}<a style="color: #000000" href="{esc(href)}">{esc(label)}</a>'))

    if not items:
        return ""

    has_logo = bool(d["logo"].strip())

    def logo_tag(extra_style: str = "") -> str:
        st = f' style="{extra_style}"' if extra_style else ""
        return f'<img src="{esc(d["logo"])}" alt="Λογότυπο" width="{esc(width)}"{st} />'

    table_open = (
        '<table style="color: #000000; font-size: 14px; font-family: Arial, sans-serif" '
        'cellspacing="0" cellpadding="0">\n<tbody>\n'
    )
    table_close = "\n</tbody>\n</table>\n<p> </p>"

    def div_lines() -> str:
        out = []
        for st, inner in items:
            attr = f' style="{st}"' if st else ""
            out.append(f"<div{attr}>{inner}</div>")
        return "\n".join(out)

    # --- 1. Κλασική (όπως το αρχικό παράδειγμα) ---
    if style == STYLES[0]:
        body = []
        for i, (st, inner) in enumerate(items):
            attr = f' style="{st}"' if st else ""
            cell = f"<td{attr}>{inner}</td>"
            if i == 0 and has_logo:
                cell = f'<td rowspan="{len(items)}">{logo_tag()}</td>\n' + cell
            body.append(f"<tr>\n{cell}\n</tr>")
        return table_open + "\n".join(body) + table_close

    # --- 2. Κάθετη γραμμή & 4. Μοντέρνα ---
    if style in (STYLES[1], STYLES[3]):
        thickness = "3px" if style == STYLES[3] else "2px"
        cells = ""
        if has_logo:
            cells += (
                '<td style="padding-right: 14px; vertical-align: middle">'
                f'{logo_tag("display: block")}</td>\n'
            )
        cells += (
            f'<td style="border-left: {thickness} solid {accent}; padding-left: 14px; '
            f'vertical-align: middle">\n{div_lines()}\n</td>'
        )
        return table_open + f"<tr>\n{cells}\n</tr>" + table_close

    # --- 3. Λογότυπο από πάνω ---
    rows = ""
    if has_logo:
        rows += f'<tr>\n<td style="padding-bottom: 8px">{logo_tag("display: block")}</td>\n</tr>\n'
    rows += (
        f'<tr>\n<td style="border-top: 1px solid {accent}; padding-top: 8px">\n'
        f"{div_lines()}\n</td>\n</tr>"
    )
    return table_open + rows + table_close


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Γεννήτρια υπογραφής email")
        self.geometry("780x760")
        self.minsize(660, 640)

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)
        frm.columnconfigure(1, weight=1)

        fields = [
            ("name", "Βαθμός / Ονοματεπώνυμο:", "Υπλγός (ΠΛΗ) Πολύδωρας Ιωάννης"),
            ("unit", "Υπηρεσία / Τμήμα:", "Γρ.Υποστήριξης Πληρ.Συστημάτων Τ.Α.Εθ.Α."),
            ("phone", "Τηλέφωνο:", "Τηλ.: 210 6571964"),
            ("email", "Email:", "webmaster@ndpf.gr"),
            ("website", "Ιστοσελίδα:", "www.ndpf.gr"),
            ("logo", "URL λογότυπου:", DEFAULT_LOGO),
            ("logo_width", "Πλάτος λογότυπου (px):", "80"),
        ]

        self.vars = {}
        for r, (key, label, default) in enumerate(fields):
            ttk.Label(frm, text=label).grid(row=r, column=0, sticky="w", pady=3, padx=(0, 8))
            var = tk.StringVar(value=default)
            ttk.Entry(frm, textvariable=var).grid(row=r, column=1, sticky="ew", pady=3)
            self.vars[key] = var

        r = len(fields)

        # Στυλ
        ttk.Label(frm, text="Στυλ υπογραφής:").grid(row=r, column=0, sticky="w", pady=3)
        self.style_var = tk.StringVar(value=STYLES[0])
        combo = ttk.Combobox(frm, textvariable=self.style_var, values=STYLES, state="readonly")
        combo.grid(row=r, column=1, sticky="ew", pady=3)
        combo.bind("<<ComboboxSelected>>", lambda e: self.generate())
        r += 1

        # Χρώμα
        ttk.Label(frm, text="Χρώμα έμφασης:").grid(row=r, column=0, sticky="w", pady=3)
        color_row = ttk.Frame(frm)
        color_row.grid(row=r, column=1, sticky="w", pady=3)
        self.accent_var = tk.StringVar(value=DEFAULT_ACCENT)
        ttk.Entry(color_row, textvariable=self.accent_var, width=10).pack(side="left")
        self.swatch = tk.Label(color_row, width=3, bg=DEFAULT_ACCENT, relief="solid", borderwidth=1)
        self.swatch.pack(side="left", padx=6)
        ttk.Button(color_row, text="Επιλογή…", command=self.pick_color).pack(side="left")
        ttk.Label(color_row, text="  (δεν επηρεάζει τη «Κλασική»)").pack(side="left")
        self.accent_var.trace_add("write", lambda *a: self.update_swatch())
        r += 1

        # Emoji
        self.emoji_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            frm,
            text="Χρήση emoji (✉️ 🌐) – αλλιώς ετικέτες E: / W:",
            variable=self.emoji_var,
            command=self.generate,
        ).grid(row=r, column=1, sticky="w", pady=3)
        r += 1

        # Κουμπιά
        btns = ttk.Frame(frm)
        btns.grid(row=r, column=0, columnspan=2, pady=10, sticky="w")
        ttk.Button(btns, text="Δημιουργία κώδικα", command=self.generate).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text="Αντιγραφή", command=self.copy).pack(side="left", padx=6)
        ttk.Button(btns, text="Αποθήκευση .html", command=self.save).pack(side="left", padx=6)
        ttk.Button(btns, text="Προεπισκόπηση στον browser", command=self.preview).pack(side="left", padx=6)
        r += 1

        ttk.Label(
            frm,
            text="HTML κώδικας (επικολλήστε τον στο «Πηγαίος κώδικας» της υπογραφής στο Roundcube):",
        ).grid(row=r, column=0, columnspan=2, sticky="w")
        r += 1

        text_frame = ttk.Frame(frm)
        text_frame.grid(row=r, column=0, columnspan=2, sticky="nsew")
        frm.rowconfigure(r, weight=1)

        self.output = tk.Text(text_frame, wrap="none", height=14, font=("Consolas", 10))
        ys = ttk.Scrollbar(text_frame, orient="vertical", command=self.output.yview)
        xs = ttk.Scrollbar(text_frame, orient="horizontal", command=self.output.xview)
        self.output.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        self.output.grid(row=0, column=0, sticky="nsew")
        ys.grid(row=0, column=1, sticky="ns")
        xs.grid(row=1, column=0, sticky="ew")
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        self.generate()

    # --- βοηθητικά ---
    def update_swatch(self):
        try:
            self.swatch.configure(bg=self.accent_var.get())
        except tk.TclError:
            pass  # μη έγκυρο χρώμα όσο πληκτρολογείται

    def pick_color(self):
        color = colorchooser.askcolor(color=self.accent_var.get(), title="Χρώμα έμφασης")[1]
        if color:
            self.accent_var.set(color)
            self.generate()

    def data(self) -> dict:
        d = {k: v.get() for k, v in self.vars.items()}
        d["style"] = self.style_var.get()
        d["accent"] = self.accent_var.get()
        d["emoji"] = self.emoji_var.get()
        return d

    def generate(self):
        code = build_signature(self.data())
        self.output.delete("1.0", "end")
        self.output.insert("1.0", code)
        return code

    def current_code(self) -> str:
        return self.output.get("1.0", "end").strip()

    def copy(self):
        code = self.current_code()
        if not code:
            messagebox.showwarning("Προσοχή", "Δεν υπάρχει κώδικας για αντιγραφή.")
            return
        self.clipboard_clear()
        self.clipboard_append(code)
        self.update()
        messagebox.showinfo("Έτοιμο", "Ο κώδικας αντιγράφηκε στο πρόχειρο.")

    def save(self):
        code = self.current_code()
        if not code:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML", "*.html"), ("Όλα τα αρχεία", "*.*")],
            initialfile="signature.html",
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
            messagebox.showinfo("Αποθηκεύτηκε", f"Το αρχείο αποθηκεύτηκε:\n{path}")

    def preview(self):
        code = self.current_code()
        if not code:
            return
        page = (
            '<!DOCTYPE html><html><head><meta charset="utf-8">'
            f"<title>Προεπισκόπηση</title></head><body>{code}</body></html>"
        )
        fd, path = tempfile.mkstemp(suffix=".html")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(page)
        webbrowser.open("file://" + path)


if __name__ == "__main__":
    App().mainloop()