from __future__ import annotations

import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from turtlebot_llm_control.knowledge_store import KnowledgeEntry, KnowledgeStore


class KnowledgeEditorApp:
    """Tkinter GUI for editing the waypoint knowledge database.

    Layout (left panel)
    -------------------
    - Database path + Load button
    - Filter + Refresh
    - Entry list (Treeview)
    - New / Delete / Import Markdown buttons

    Layout (right panel)
    --------------------
    - Form fields: key, title, kind, location_key, x, y, yaw, tags
    - Arrival Speech text box  (what the robot says when it arrives)
    - [Test Arrival Speech] button
    - Wiki / Notes text box  (full knowledge content for RAG)
    - Save / Reload buttons
    - RAG Query panel with threaded Ollama lookup
    """

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("TurtleBot Knowledge Editor")
        self.store = KnowledgeStore()
        self.selected_key = ""
        self._llm = None           # lazy-loaded LLMDialogueEngine
        self._query_running = False

        self._build_layout()
        self.refresh_entries()
        # Initialise LLM in background so the window opens instantly.
        threading.Thread(target=self._init_llm, daemon=True).start()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_layout(self) -> None:
        self.root.geometry("1260x860")
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        left = ttk.Frame(self.root, padding=10)
        left.grid(row=0, column=0, sticky="nsew")
        left.rowconfigure(2, weight=1)
        left.columnconfigure(0, weight=1)

        right = ttk.Frame(self.root, padding=10)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(1, weight=1)
        # Give expanding weight to arrival_speech (row 9) and content (row 11).
        right.rowconfigure(9, weight=1)
        right.rowconfigure(11, weight=2)

        # ---- left: database path ----
        db_row = ttk.Frame(left)
        db_row.grid(row=0, column=0, sticky="ew")
        db_row.columnconfigure(1, weight=1)
        ttk.Label(db_row, text="Database").grid(row=0, column=0, sticky="w")
        self.db_path_var = tk.StringVar(value=str(self.store.db_path))
        ttk.Entry(db_row, textvariable=self.db_path_var).grid(
            row=0, column=1, sticky="ew", padx=4
        )
        ttk.Button(db_row, text="Load", command=self.reload_database).grid(
            row=0, column=2, padx=4
        )

        # ---- left: filter ----
        search_row = ttk.Frame(left)
        search_row.grid(row=1, column=0, sticky="ew", pady=(10, 6))
        search_row.columnconfigure(1, weight=1)
        ttk.Label(search_row, text="Filter").grid(row=0, column=0, sticky="w")
        self.filter_var = tk.StringVar()
        ttk.Entry(search_row, textvariable=self.filter_var).grid(
            row=0, column=1, sticky="ew", padx=4
        )
        ttk.Button(search_row, text="Refresh", command=self.refresh_entries).grid(
            row=0, column=2, padx=4
        )

        # ---- left: treeview ----
        self.tree = ttk.Treeview(
            left,
            columns=("title", "kind", "location", "tags"),
            show="headings",
            selectmode="browse",
            height=24,
        )
        self.tree.heading("title", text="Title")
        self.tree.heading("kind", text="Kind")
        self.tree.heading("location", text="Location")
        self.tree.heading("tags", text="Tags")
        self.tree.column("title", width=220, anchor="w")
        self.tree.column("kind", width=80, anchor="w")
        self.tree.column("location", width=130, anchor="w")
        self.tree.column("tags", width=160, anchor="w")
        self.tree.grid(row=2, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_select_entry)

        scroll = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.grid(row=2, column=1, sticky="ns")

        buttons = ttk.Frame(left)
        buttons.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(buttons, text="New", command=self.clear_form).grid(
            row=0, column=0, padx=2
        )
        ttk.Button(buttons, text="Delete", command=self.delete_entry).grid(
            row=0, column=1, padx=2
        )
        ttk.Button(
            buttons, text="Import Markdown", command=self.import_markdown
        ).grid(row=0, column=2, padx=2)

        # ---- right: plain form fields ----
        plain_fields = [
            ("Key",          "key_var"),
            ("Title",        "title_var"),
            ("Kind",         "kind_var"),
            ("Location key", "location_key_var"),
            ("X  (map)",     "x_var"),
            ("Y  (map)",     "y_var"),
            ("Yaw (rad)",    "yaw_var"),
            ("Tags",         "tags_var"),
        ]
        self.form_vars: dict[str, tk.StringVar] = {}
        for row_i, (label, var_name) in enumerate(plain_fields):
            ttk.Label(right, text=label).grid(
                row=row_i, column=0, sticky="w", pady=3
            )
            if var_name == "kind_var":
                var = tk.StringVar(value="place")
                widget = ttk.Combobox(
                    right,
                    textvariable=var,
                    values=["place", "artifact", "page", "route"],
                    state="readonly",
                    width=18,
                )
            else:
                var = tk.StringVar()
                widget = ttk.Entry(right, textvariable=var)
            widget.grid(row=row_i, column=1, sticky="ew", pady=3, padx=(6, 0))
            self.form_vars[var_name] = var

        # ---- right: arrival speech ----
        # Row 8 = label, rows 9 = text widget (gets weight)
        ttk.Label(right, text="Arrival Speech", font=("", 9, "bold")).grid(
            row=8, column=0, columnspan=2, sticky="w", pady=(10, 2), padx=(0, 0)
        )
        ttk.Label(
            right,
            text="What the robot says when it arrives at this waypoint. "
                 "Leave blank to auto-generate from the first paragraph of Wiki/Notes.",
            foreground="gray",
            wraplength=480,
            justify="left",
        ).grid(row=8, column=1, sticky="w", padx=(6, 0))

        self.arrival_text = tk.Text(right, wrap="word", height=4, font=("", 10))
        self.arrival_text.grid(
            row=9, column=0, columnspan=2, sticky="nsew", padx=(0, 0), pady=(2, 0)
        )
        arr_scroll = ttk.Scrollbar(right, orient="vertical", command=self.arrival_text.yview)
        self.arrival_text.configure(yscrollcommand=arr_scroll.set)
        arr_scroll.grid(row=9, column=2, sticky="ns", pady=(2, 0))

        # Test arrival button
        test_btn_frame = ttk.Frame(right)
        test_btn_frame.grid(row=10, column=0, columnspan=2, sticky="w", pady=(4, 4))
        ttk.Button(
            test_btn_frame,
            text="Preview Arrival Speech",
            command=self.preview_arrival_speech,
        ).grid(row=0, column=0, padx=(0, 6))
        ttk.Label(
            test_btn_frame,
            text="(shows exactly what the robot will say when it reaches this waypoint)",
            foreground="gray",
        ).grid(row=0, column=1)

        # ---- right: wiki / notes ----
        ttk.Label(right, text="Wiki / Notes", font=("", 9, "bold")).grid(
            row=11, column=0, sticky="nw", pady=(6, 2)
        )
        self.content_text = tk.Text(right, wrap="word", height=12, font=("", 10))
        self.content_text.grid(
            row=11, column=1, sticky="nsew", pady=(6, 2), padx=(6, 0)
        )
        con_scroll = ttk.Scrollbar(right, orient="vertical", command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=con_scroll.set)
        con_scroll.grid(row=11, column=2, sticky="ns", pady=(6, 2))

        # ---- right: save / reload ----
        form_buttons = ttk.Frame(right)
        form_buttons.grid(row=12, column=1, sticky="e", pady=(8, 0))
        ttk.Button(form_buttons, text="Save Entry", command=self.save_entry).grid(
            row=0, column=0, padx=4
        )
        ttk.Button(
            form_buttons, text="Reload List", command=self.refresh_entries
        ).grid(row=0, column=1, padx=4)

        # ---- right: RAG query panel ----
        query_box = ttk.LabelFrame(
            right, text="Ask a Question  (RAG — powered by local Ollama)", padding=10
        )
        query_box.grid(
            row=13, column=0, columnspan=3, sticky="nsew", pady=(14, 0)
        )
        query_box.columnconfigure(0, weight=1)
        query_box.rowconfigure(1, weight=1)

        self.query_var = tk.StringVar()
        q_row = ttk.Frame(query_box)
        q_row.grid(row=0, column=0, sticky="ew")
        q_row.columnconfigure(0, weight=1)
        ttk.Entry(q_row, textvariable=self.query_var, font=("", 11)).grid(
            row=0, column=0, sticky="ew"
        )
        self.query_btn = ttk.Button(q_row, text="Ask", command=self.run_query)
        self.query_btn.grid(row=0, column=1, padx=(6, 0))

        self.llm_status_var = tk.StringVar(value="Initialising Ollama…")
        ttk.Label(
            query_box, textvariable=self.llm_status_var, foreground="gray"
        ).grid(row=0, column=1, sticky="e", padx=(10, 0))

        self.answer_text = tk.Text(
            query_box, wrap="word", height=7, font=("", 10), state="disabled"
        )
        self.answer_text.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(8, 0))
        ans_scroll = ttk.Scrollbar(query_box, orient="vertical", command=self.answer_text.yview)
        self.answer_text.configure(yscrollcommand=ans_scroll.set)
        ans_scroll.grid(row=1, column=2, sticky="ns", pady=(8, 0))

    # ------------------------------------------------------------------
    # LLM (lazy, background thread)
    # ------------------------------------------------------------------

    def _init_llm(self) -> None:
        try:
            from turtlebot_llm_control.llm_dialogue import LLMDialogueEngine

            self._llm = LLMDialogueEngine(
                knowledge_db_path=str(self.store.db_path),
                warn=lambda _: None,
            )
            if self._llm.client is not None:
                status = "Ollama ready  (model: %s)" % self._llm.llm_model
            else:
                status = "Ollama unavailable — showing keyword summaries"
        except Exception as exc:
            self._llm = None
            status = "LLM engine error: %s" % exc
        self.root.after(0, self.llm_status_var.set, status)

    # ------------------------------------------------------------------
    # Database operations
    # ------------------------------------------------------------------

    def reload_database(self) -> None:
        self.store = KnowledgeStore(self.db_path_var.get().strip())
        self.refresh_entries()
        threading.Thread(target=self._init_llm, daemon=True).start()

    def clear_form(self) -> None:
        self.selected_key = ""
        for var in self.form_vars.values():
            var.set("")
        self.form_vars["kind_var"].set("place")
        self.arrival_text.delete("1.0", tk.END)
        self.content_text.delete("1.0", tk.END)
        self.tree.selection_remove(self.tree.selection())

    def refresh_entries(self) -> None:
        self.tree.delete(*self.tree.get_children())
        filt = self.filter_var.get().strip().lower()
        for entry in self.store.list_entries():
            haystack = " ".join(
                [entry.key, entry.title, entry.kind, entry.location_key, entry.tags, entry.content]
            ).lower()
            if filt and filt not in haystack:
                continue
            self.tree.insert(
                "",
                tk.END,
                iid=entry.key,
                values=(entry.title, entry.kind, entry.location_key or "-", entry.tags),
            )

    def on_select_entry(self, _event=None) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        entry = self.store.get_entry(sel[0])
        if entry is None:
            return
        self.selected_key = entry.key
        self.form_vars["key_var"].set(entry.key)
        self.form_vars["title_var"].set(entry.title)
        self.form_vars["kind_var"].set(entry.kind)
        self.form_vars["location_key_var"].set(entry.location_key)
        self.form_vars["x_var"].set("" if entry.x is None else str(entry.x))
        self.form_vars["y_var"].set("" if entry.y is None else str(entry.y))
        self.form_vars["yaw_var"].set("" if entry.yaw is None else str(entry.yaw))
        self.form_vars["tags_var"].set(entry.tags)
        self.arrival_text.delete("1.0", tk.END)
        self.arrival_text.insert("1.0", entry.arrival_speech)
        self.content_text.delete("1.0", tk.END)
        self.content_text.insert("1.0", entry.content)

    def save_entry(self) -> None:
        key = self.form_vars["key_var"].get().strip()
        title = self.form_vars["title_var"].get().strip()
        if not key or not title:
            messagebox.showerror("Missing data", "Key and Title are required.")
            return

        def _float(s: str):
            s = s.strip()
            return None if not s else float(s)

        entry = KnowledgeEntry(
            key=key,
            title=title,
            kind=self.form_vars["kind_var"].get().strip() or "place",
            location_key=self.form_vars["location_key_var"].get().strip(),
            x=_float(self.form_vars["x_var"].get()),
            y=_float(self.form_vars["y_var"].get()),
            yaw=_float(self.form_vars["yaw_var"].get()),
            tags=self.form_vars["tags_var"].get().strip(),
            arrival_speech=self.arrival_text.get("1.0", tk.END).strip(),
            content=self.content_text.get("1.0", tk.END).strip(),
        )
        self.store.upsert_entry(entry)
        self.selected_key = key
        self.refresh_entries()
        messagebox.showinfo("Saved", "Entry '%s' saved." % key)

    def delete_entry(self) -> None:
        key = self.form_vars["key_var"].get().strip() or self.selected_key
        if not key:
            return
        if not messagebox.askyesno("Delete", "Delete entry '%s'?" % key):
            return
        self.store.delete_entry(key)
        self.clear_form()
        self.refresh_entries()

    def import_markdown(self) -> None:
        path = filedialog.askopenfilename(
            title="Select a wiki / notes file",
            filetypes=[
                ("Markdown / text", "*.md *.markdown *.txt"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        text = Path(path).read_text(encoding="utf-8")
        self.content_text.delete("1.0", tk.END)
        self.content_text.insert("1.0", text)
        if not self.form_vars["title_var"].get().strip():
            self.form_vars["title_var"].set(Path(path).stem.replace("_", " ").title())
        if not self.form_vars["key_var"].get().strip():
            self.form_vars["key_var"].set(Path(path).stem.replace(" ", "_").lower())

    # ------------------------------------------------------------------
    # Arrival speech preview
    # ------------------------------------------------------------------

    def preview_arrival_speech(self) -> None:
        key = self.form_vars["key_var"].get().strip()

        # Build the speech from what is currently in the form (unsaved is fine).
        arrival = self.arrival_text.get("1.0", tk.END).strip()
        title = self.form_vars["title_var"].get().strip() or key or "this location"

        if not arrival:
            # Fall back to first paragraph of Wiki/Notes.
            content = self.content_text.get("1.0", tk.END).strip()
            if content:
                import re
                chunks = [c.strip() for c in re.split(r"\n\s*\n", content) if c.strip()]
                arrival = chunks[0] if chunks else content
                if len(arrival) > 400:
                    arrival = arrival[:400].rstrip() + "..."
                arrival = "We have arrived at %s. %s" % (title, arrival)
            else:
                arrival = "We have arrived at %s." % title

        top = tk.Toplevel(self.root)
        top.title("Arrival Speech Preview — %s" % title)
        top.geometry("540x220")
        top.resizable(True, True)
        tk.Label(top, text="The robot will say:", font=("", 10, "bold")).pack(
            anchor="w", padx=12, pady=(12, 2)
        )
        frame = ttk.Frame(top)
        frame.pack(fill="both", expand=True, padx=12, pady=4)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        txt = tk.Text(frame, wrap="word", font=("", 11), height=6)
        txt.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(frame, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=sb.set)
        sb.grid(row=0, column=1, sticky="ns")
        txt.insert("1.0", arrival)
        txt.config(state="disabled")
        ttk.Button(top, text="Close", command=top.destroy).pack(pady=6)

    # ------------------------------------------------------------------
    # RAG query (threaded so the UI stays responsive)
    # ------------------------------------------------------------------

    def run_query(self) -> None:
        query = self.query_var.get().strip()
        if not query or self._query_running:
            return
        self._query_running = True
        self.query_btn.config(state="disabled")
        self._set_answer("Querying Ollama…")
        threading.Thread(target=self._do_query, args=(query,), daemon=True).start()

    def _do_query(self, query: str) -> None:
        try:
            if self._llm is not None and self._llm.client is not None:
                answer = self._llm.generate_knowledge_response(query)
                answer = answer or "No relevant knowledge found in the database."
            else:
                answer = self.store.summarize_hits(query)
                if not answer:
                    answer = "No relevant knowledge found in the database."
                else:
                    answer = "[Keyword summary — Ollama not available]\n\n" + answer
        except Exception as exc:
            answer = "Error during query: %s" % exc
        self.root.after(0, self._finish_query, answer)

    def _finish_query(self, answer: str) -> None:
        self._set_answer(answer)
        self._query_running = False
        self.query_btn.config(state="normal")

    def _set_answer(self, text: str) -> None:
        self.answer_text.config(state="normal")
        self.answer_text.delete("1.0", tk.END)
        self.answer_text.insert("1.0", text)
        self.answer_text.config(state="disabled")


def main() -> None:
    root = tk.Tk()
    KnowledgeEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
