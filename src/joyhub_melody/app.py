"""Tkinter application for JoyHub Melody Player."""

import json
import os
import socket
import subprocess
import tempfile
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .settings import *  # noqa: F403,F401
from .engine import ensure_internal_engine
from .funscript import (
    convertir_original_en_vibration_temporairement,
    find_script,
    natural_key,
    script_candidates_for_deletion,
)

class VibrationPlayerGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1000x760")
        self.minsize(680, 480)
        self.configure(bg=COLORS["bg"])

        
        
        try:
            self.attributes("-zoomed", True)
        except tk.TclError:
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

        self.language = "fr"
        self.language_display = tk.StringVar(value="Français")
        self.video_path = tk.StringVar()
        self.script_path = tk.StringVar(value=self.t("Aucun script sélectionné"))
        self.status = tk.StringVar(value=self.t("Choisis une vidéo pour commencer."))
        self.max_power = tk.DoubleVar(value=1.00)
        self.zero_hold = tk.IntVar(value=150)
        self.smoothing = tk.DoubleVar(value=0.20)
        self.min_power = tk.DoubleVar(value=0.08)
        self.amplification = tk.DoubleVar(value=0.0)
        self.fullscreen = tk.BooleanVar(value=True)
        self.pump_enabled = tk.BooleanVar(value=False)
        self.pump_seconds = tk.DoubleVar(value=1.5)
        self.release_seconds = tk.DoubleVar(value=2.0)
        self.r4_interval_seconds = tk.DoubleVar(value=3.0)
        self.pause_min_seconds = tk.DoubleVar(value=12.0)
        self.pause_max_seconds = tk.DoubleVar(value=20.0)
        self.vibration_pattern = tk.StringVar(value="progressif3")
        self.vibration_pattern_2 = tk.StringVar(value="Aucun")
        self.vibration_pattern_3 = tk.StringVar(value="Aucun")
        self.random_patterns_enabled = tk.BooleanVar(value=False)
        self.delete_after_end_var = tk.BooleanVar(value=False)
        self.play_next_var = tk.BooleanVar(value=True)

        self.process: subprocess.Popen[str] | None = None
        self.playlist: list[Path] = []
        self.playlist_active = False
        self.delete_after_natural_end = False
        self.stop_requested = False
        self.manual_next_requested = False
        self.current_video: Path | None = None
        self.current_script: Path | None = None
        self.runtime_script: Path | None = None
        self.graph_actions: list[tuple[int, int]] = []
        self.graph_duration_ms = 0
        self.graph_position_ms = 0
        self.progress_file = Path(tempfile.gettempdir()) / f"vibration-player-progress-{os.getpid()}.json"
        self.mpv_socket = Path(tempfile.gettempdir()) / f"vibration-player-mpv-{os.getpid()}.sock"

        self.configure_styles()
        self.load_config()
        global LANGUAGE
        self.language = self.language if self.language in ("fr", "en") else "fr"
        LANGUAGE = self.language
        self.language_display.set("English" if self.language == "en" else "Français")
        # Refresh initial UI strings after the saved language has been loaded.
        self.script_path.set(self.t("Aucun script sélectionné"))
        self.status.set(self.t("Choisis une vidéo pour commencer."))
        if normalize_pattern(self.vibration_pattern_2.get()) == "Aucun":
            self.vibration_pattern_2.set(self.t("Aucun"))
        if normalize_pattern(self.vibration_pattern_3.get()) == "Aucun":
            self.vibration_pattern_3.set(self.t("Aucun"))
        try:
            ensure_internal_engine()
        except OSError:
            pass
        self.build_ui()
        self.after(150, self.update_graph_position)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def t(self, text: str) -> str:
        """Translate UI text using this window's selected language."""
        if self.language == "en":
            return TRANSLATIONS.get(text, text)
        return text

    def change_language(self, _event=None) -> None:
        global LANGUAGE
        selected = self.language_display.get()
        self.language = "en" if selected == "English" else "fr"
        LANGUAGE = self.language
        if normalize_pattern(self.vibration_pattern_2.get()) == "Aucun":
            self.vibration_pattern_2.set(self.t("Aucun"))
        if normalize_pattern(self.vibration_pattern_3.get()) == "Aucun":
            self.vibration_pattern_3.set(self.t("Aucun"))
        self.save_config()

        # Rebuild all visible widgets so every label/button immediately follows
        # the selected language without restarting the player.
        for child in list(self.winfo_children()):
            child.destroy()
        if not self.video_path.get():
            self.script_path.set(self.t("Aucun script sélectionné"))
            self.status.set(self.t("Choisis une vidéo pour commencer."))
        self.build_ui()

    def configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            ".",
            background=COLORS["bg"],
            foreground=COLORS["text"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["border"],
            darkcolor=COLORS["border"],
            font=("Noto Sans", 10),
        )

        style.configure("Root.TFrame", background=COLORS["bg"])
        style.configure(
            "Card.TFrame",
            background=COLORS["panel"],
            borderwidth=1,
            relief="solid",
        )
        style.configure(
            "Header.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["text"],
            font=("Noto Sans", 22, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["muted"],
            font=("Noto Sans", 10),
        )
        style.configure(
            "CardTitle.TLabel",
            background=COLORS["panel"],
            foreground=COLORS["text"],
            font=("Noto Sans", 12, "bold"),
        )
        style.configure(
            "CardText.TLabel",
            background=COLORS["panel"],
            foreground=COLORS["muted"],
        )
        style.configure(
            "Value.TLabel",
            background=COLORS["panel"],
            foreground=COLORS["accent_hover"],
            font=("Noto Sans", 10, "bold"),
        )
        style.configure(
            "Status.TLabel",
            background=COLORS["panel_alt"],
            foreground=COLORS["muted"],
            padding=(12, 9),
        )

        # High-contrast controls for dark themes.
        style.configure(
            "TCombobox",
            fieldbackground=COLORS["panel_alt"],
            background=COLORS["panel_alt"],
            foreground=COLORS["text"],
            arrowcolor=COLORS["text"],
            bordercolor=COLORS["accent"],
            lightcolor=COLORS["accent"],
            darkcolor=COLORS["accent"],
            padding=7,
        )
        style.map(
            "TCombobox",
            fieldbackground=[
                ("readonly", COLORS["panel_alt"]),
                ("disabled", COLORS["panel"]),
            ],
            foreground=[
                ("readonly", COLORS["text"]),
                ("disabled", COLORS["muted"]),
            ],
            selectbackground=[("readonly", COLORS["accent"])],
            selectforeground=[("readonly", "#ffffff")],
        )
        style.configure(
            "Dark.TCheckbutton",
            background=COLORS["panel"],
            foreground=COLORS["text"],
            indicatorcolor=COLORS["panel_alt"],
            padding=(2, 5),
        )
        style.map(
            "Dark.TCheckbutton",
            background=[("active", COLORS["panel"])],
            foreground=[("active", "#ffffff"), ("disabled", COLORS["muted"])],
            indicatorcolor=[
                ("selected", COLORS["accent"]),
                ("!selected", COLORS["panel_alt"]),
            ],
        )

        style.configure(
            "Dark.TEntry",
            fieldbackground=COLORS["panel_alt"],
            foreground=COLORS["text"],
            insertcolor=COLORS["text"],
            bordercolor=COLORS["border"],
            padding=9,
        )
        style.map(
            "Dark.TEntry",
            fieldbackground=[("readonly", COLORS["panel_alt"])],
            foreground=[("readonly", COLORS["text"])],
        )

        style.configure(
            "Accent.TButton",
            background=COLORS["accent"],
            foreground="#ffffff",
            borderwidth=0,
            focusthickness=0,
            padding=(16, 11),
            font=("Noto Sans", 10, "bold"),
        )
        style.map(
            "Accent.TButton",
            background=[
                ("active", COLORS["accent_hover"]),
                ("disabled", COLORS["panel_alt"]),
            ],
            foreground=[("disabled", "#6e7582")],
        )

        style.configure(
            "Secondary.TButton",
            background=COLORS["panel_alt"],
            foreground=COLORS["text"],
            borderwidth=1,
            padding=(14, 10),
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#2a2f39")],
        )

        style.configure(
            "Danger.TButton",
            background="#382028",
            foreground="#ff8797",
            borderwidth=0,
            padding=(14, 10),
            font=("Noto Sans", 10, "bold"),
        )
        style.map(
            "Danger.TButton",
            background=[("active", "#4a2530")],
        )

        style.configure(
            "Dark.Horizontal.TScale",
            background=COLORS["panel"],
            troughcolor=COLORS["track"],
            bordercolor=COLORS["panel"],
            lightcolor=COLORS["accent"],
            darkcolor=COLORS["accent"],
        )

        style.configure(
            "Dark.TCheckbutton",
            background=COLORS["panel"],
            foreground=COLORS["text"],
            indicatorbackground=COLORS["panel_alt"],
            indicatorforeground=COLORS["accent"],
            padding=4,
        )
        style.map(
            "Dark.TCheckbutton",
            background=[("active", COLORS["panel"])],
            foreground=[("active", COLORS["text"])],
        )

    def build_ui(self) -> None:
        
        
        shell = ttk.Frame(self, style="Root.TFrame")
        self.ui_shell = shell
        shell.pack(fill="both", expand=True)

        
        graph_frame = tk.Frame(
            shell,
            bg="#050609",
            height=110,
            highlightbackground="#3b4050",
            highlightthickness=1,
        )
        graph_frame.pack(side="bottom", fill="x")
        graph_frame.pack_propagate(False)

        graph_header = tk.Frame(graph_frame, bg="#050609", height=28)
        graph_header.pack(side="top", fill="x")
        graph_header.pack_propagate(False)

        graph_title = tk.Label(
            graph_header,
            text=self.t("VIBRATION FUNSCRIPT — clique ou glisse pour déplacer la vidéo"),
            bg="#050609",
            fg="#aeb6c5",
            font=("Noto Sans", 8, "bold"),
            anchor="w",
            padx=10,
        )
        graph_title.pack(side="left", fill="x", expand=True)

        for label, command in (
            ("−10 s", lambda: self.seek_relative(-10)),
            ("Pause / Reprendre", self.toggle_pause),
            ("+10 s", lambda: self.seek_relative(10)),
        ):
            tk.Button(
                graph_header,
                text=self.t(label),
                command=command,
                bg="#20242d",
                fg="#f2f4f8",
                activebackground="#353b49",
                activeforeground="#ffffff",
                relief="flat",
                borderwidth=0,
                padx=10,
                pady=2,
                cursor="hand2",
                font=("Noto Sans", 8, "bold"),
            ).pack(side="left", padx=(0, 4), pady=3)

        self.graph_canvas = tk.Canvas(
            graph_frame,
            bg="#090b10",
            highlightthickness=0,
            borderwidth=0,
            height=86,
        )
        self.graph_canvas.pack(side="bottom", fill="both", expand=True)
        self.graph_canvas.bind(
            "<Configure>",
            lambda _event: self.draw_funscript_graph()
        )
        self.graph_canvas.bind("<Button-1>", self.seek_from_graph)
        self.graph_canvas.bind("<B1-Motion>", self.seek_from_graph)
        self.graph_canvas.bind("<Button-3>", self.toggle_pause)
        self.graph_canvas.bind("<MouseWheel>", self.graph_mousewheel)
        self.graph_canvas.bind("<Button-4>", self.graph_mousewheel)
        self.graph_canvas.bind("<Button-5>", self.graph_mousewheel)

        content_frame = ttk.Frame(shell, style="Root.TFrame")
        content_frame.pack(side="top", fill="both", expand=True)
        content_frame.rowconfigure(0, weight=1)
        content_frame.columnconfigure(0, weight=1)

        canvas = tk.Canvas(
            content_frame,
            bg=COLORS["bg"],
            highlightthickness=0,
            borderwidth=0,
        )
        scrollbar = ttk.Scrollbar(
            content_frame,
            orient="vertical",
            command=canvas.yview
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        root = ttk.Frame(canvas, style="Root.TFrame", padding=24)
        root.columnconfigure(0, weight=1)
        window_id = canvas.create_window((0, 0), window=root, anchor="nw")

        def update_scrollregion(_event=None) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        def fit_width(event) -> None:
            canvas.itemconfigure(window_id, width=event.width)

        def mousewheel(event) -> None:
            if getattr(event, "delta", 0):
                canvas.yview_scroll(int(-event.delta / 120), "units")
            elif getattr(event, "num", None) == 4:
                canvas.yview_scroll(-3, "units")
            elif getattr(event, "num", None) == 5:
                canvas.yview_scroll(3, "units")

        root.bind("<Configure>", update_scrollregion)
        canvas.bind("<Configure>", fit_width)
        canvas.bind_all("<MouseWheel>", mousewheel)
        canvas.bind_all("<Button-4>", mousewheel)
        canvas.bind_all("<Button-5>", mousewheel)

        
        self.bind("<F11>", self.toggle_app_fullscreen)
        self.bind("<Escape>", self.leave_app_fullscreen)

        header = ttk.Frame(root, style="Root.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header, text="JoyHub Melody Player", style="Header.TLabel"
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text=APP_VERSION,
            style="Subtitle.TLabel",
        ).grid(row=0, column=1, rowspan=2, sticky="ne", padx=(20, 0))
        self.language_combo = ttk.Combobox(
            header,
            textvariable=self.language_display,
            values=("Français", "English"),
            state="readonly",
            width=10,
        )
        self.language_combo.grid(row=0, column=2, rowspan=2, sticky="ne", padx=(10, 0))
        self.language_combo.bind("<<ComboboxSelected>>", self.change_language)
        ttk.Label(
            header,
            text=self.t("JoyHub Melody BLE direct — connexion mémorisée + schémas vibration + R4"),
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        file_card = ttk.Frame(root, style="Card.TFrame", padding=18)
        file_card.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        file_card.columnconfigure(1, weight=1)

        ttk.Label(
            file_card, text=self.t("Sélection"), style="CardTitle.TLabel"
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

        ttk.Label(
            file_card, text=self.t("Vidéo"), style="CardText.TLabel"
        ).grid(row=1, column=0, sticky="w", pady=6)

        ttk.Entry(
            file_card,
            textvariable=self.video_path,
            state="readonly",
            style="Dark.TEntry",
        ).grid(row=1, column=1, sticky="ew", padx=10, pady=6)

        ttk.Button(
            file_card,
            text=self.t("Parcourir"),
            style="Secondary.TButton",
            command=self.choose_video,
        ).grid(row=1, column=2, pady=6)

        ttk.Label(
            file_card, text=self.t("Script"), style="CardText.TLabel"
        ).grid(row=2, column=0, sticky="nw", pady=6)

        self.script_label = ttk.Label(
            file_card,
            textvariable=self.script_path,
            style="CardText.TLabel",
            wraplength=580,
        )
        self.script_label.grid(
            row=2, column=1, columnspan=2, sticky="w", padx=10, pady=6
        )

        settings = ttk.Frame(root, style="Card.TFrame", padding=18)
        settings.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        settings.columnconfigure(1, weight=1)

        ttk.Label(
            settings, text=self.t("Réglages"), style="CardTitle.TLabel"
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

        self.add_scale(
            settings, 1, "Vibration maximale", self.max_power, 0.10, 1.00,
            lambda v: f"{float(v) * 100:.0f} %"
        )
        self.add_scale(
            settings, 2, "Maintien à zéro", self.zero_hold, 0, 1000,
            lambda v: f"{int(float(v))} ms"
        )
        self.add_scale(
            settings, 3, "Lissage", self.smoothing, 0.00, 0.95,
            lambda v: f"{float(v):.2f}"
        )
        self.add_scale(
            settings, 4, "Vibration minimale", self.min_power, 0.00, 0.50,
            lambda v: f"{float(v) * 100:.0f} %"
        )
        self.add_scale(
            settings, 5, "Amplification vibration", self.amplification, 0, 100,
            lambda v: (
                f"{float(v):.0f} %  "
                f"(x{1.0 + 2.0 * float(v) / 100.0:.2f})"
            )
        )

        ttk.Checkbutton(
            settings,
            text=self.t("Ouvrir MPV en plein écran sur l’écran de droite"),
            variable=self.fullscreen,
            style="Dark.TCheckbutton",
        ).grid(row=6, column=1, sticky="w", padx=10, pady=(10, 2))

        ttk.Checkbutton(
            settings,
            text=self.t("Activer le contrôle PUMP / R4 (CONSTRICT)"),
            variable=self.pump_enabled,
            style="Dark.TCheckbutton",
        ).grid(row=7, column=1, sticky="w", padx=10, pady=(8, 8))

        ttk.Label(
            settings, text=self.t("Contrôle PUMP / R4"), style="CardTitle.TLabel"
        ).grid(row=8, column=0, columnspan=3, sticky="w", pady=(12, 8))

        self.add_scale(
            settings, 9, "Durée du PUMP", self.pump_seconds, 0.50, 5.00,
            lambda v: f"{float(v):.1f} s"
        )

        self.add_scale(
            settings, 10, "Durée du relâchement", self.release_seconds, 0.50, 8.00,
            lambda v: f"{float(v):.1f} s"
        )

        self.add_scale(
            settings, 11, "R4 répété toutes les", self.r4_interval_seconds, 0.50, 10.00,
            lambda v: f"{float(v):.1f} s"
        )

        self.add_scale(
            settings, 12, "Pause minimale entre PUMP", self.pause_min_seconds, 2.0, 60.0,
            lambda v: f"{float(v):.0f} s"
        )

        self.add_scale(
            settings, 13, "Pause maximale entre PUMP", self.pause_max_seconds, 2.0, 90.0,
            lambda v: f"{float(v):.0f} s"
        )

        ttk.Label(
            settings, text=self.t("Schéma vibration 1"), style="CardText.TLabel"
        ).grid(row=14, column=0, sticky="w", pady=(12, 6))

        self.pattern_combo = ttk.Combobox(
            settings,
            textvariable=self.vibration_pattern,
            state="readonly",
            values=VIBRATION_PATTERN_NAMES,
            width=30,
        )
        self.pattern_combo.grid(row=14, column=1, sticky="w", padx=10, pady=(12, 6))

        ttk.Label(
            settings, text=self.t("Schéma vibration 2"), style="CardText.TLabel"
        ).grid(row=15, column=0, sticky="w", pady=6)

        self.pattern_combo_2 = ttk.Combobox(
            settings,
            textvariable=self.vibration_pattern_2,
            state="readonly",
            values=(self.t("Aucun"),) + VIBRATION_PATTERN_NAMES,
            width=30,
        )
        self.pattern_combo_2.grid(row=15, column=1, sticky="w", padx=10, pady=6)

        ttk.Label(
            settings, text=self.t("Schéma vibration 3"), style="CardText.TLabel"
        ).grid(row=16, column=0, sticky="w", pady=6)

        self.pattern_combo_3 = ttk.Combobox(
            settings,
            textvariable=self.vibration_pattern_3,
            state="readonly",
            values=(self.t("Aucun"),) + VIBRATION_PATTERN_NAMES,
            width=30,
        )
        self.pattern_combo_3.grid(row=16, column=1, sticky="w", padx=10, pady=6)

        ttk.Checkbutton(
            settings,
            text=self.t("Choisir aléatoirement parmi les 1 à 3 schémas sélectionnés"),
            variable=self.random_patterns_enabled,
            style="Dark.TCheckbutton",
        ).grid(row=17, column=1, sticky="w", padx=10, pady=(6, 2))

        ttk.Checkbutton(
            settings,
            text=self.t("Supprimer la vidéo et ses funscripts à la fin ou en passant à la suivante"),
            variable=self.delete_after_end_var,
            style="Dark.TCheckbutton",
        ).grid(row=18, column=1, sticky="w", padx=10, pady=(8, 2))

        ttk.Checkbutton(
            settings,
            text=self.t("Passer automatiquement à la vidéo suivante"),
            variable=self.play_next_var,
            style="Dark.TCheckbutton",
        ).grid(row=19, column=1, sticky="w", padx=10, pady=(6, 2))

        actions = ttk.Frame(root, style="Root.TFrame")
        actions.grid(row=3, column=0, sticky="ew", pady=(0, 14))
        actions.columnconfigure(0, weight=1)

        self.launch_button = ttk.Button(
            actions,
            text=self.t("▶  Lancer la vidéo"),
            command=self.launch,
            state="disabled",
            style="Accent.TButton",
        )
        self.launch_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.folder_button = ttk.Button(
            actions,
            text=self.t("⏭  Lire le dossier"),
            command=self.launch_folder_playlist,
            state="disabled",
            style="Secondary.TButton",
        )
        self.folder_button.grid(row=0, column=1, padx=(0, 8))

        self.next_button = ttk.Button(
            actions,
            text=self.t("⏩  Vidéo suivante"),
            command=self.next_video,
            state="disabled",
            style="Secondary.TButton",
        )
        self.next_button.grid(row=0, column=2, padx=(0, 8))

        ttk.Button(
            actions,
            text=self.t("🧪  Test aspiration Melody 10 s"),
            command=self.test_pump,
            style="Secondary.TButton",
        ).grid(row=0, column=3, padx=(0, 8))

        ttk.Button(
            actions,
            text=self.t("■  Arrêter"),
            command=self.stop,
            style="Danger.TButton",
        ).grid(row=0, column=4)

        self.status_label = ttk.Label(
            root,
            textvariable=self.status,
            style="Status.TLabel",
            anchor="w",
        )
        self.status_label.grid(row=4, column=0, sticky="ew")

        self.after(100, self.draw_funscript_graph)

    def clear_funscript_graph(self) -> None:
        self.graph_actions = []
        self.graph_duration_ms = 0
        self.graph_position_ms = 0
        if hasattr(self, "graph_canvas"):
            self.draw_funscript_graph()

    def load_funscript_graph(self, script: Path) -> None:
        try:
            data = json.loads(script.read_text(encoding="utf-8-sig"))
            actions = data.get("actions", [])
            parsed = []
            for action in actions:
                at = int(action.get("at", 0))
                pos = max(0, min(100, int(action.get("pos", 50))))
                parsed.append((at, pos))
            parsed.sort()
            self.graph_actions = parsed
            self.graph_duration_ms = parsed[-1][0] if parsed else 0
            self.graph_position_ms = 0
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            self.graph_actions = []
            self.graph_duration_ms = 0
            self.graph_position_ms = 0
        if hasattr(self, "graph_canvas"):
            self.draw_funscript_graph()

    def draw_funscript_graph(self) -> None:
        if not hasattr(self, "graph_canvas"):
            return
        c = self.graph_canvas
        c.delete("all")
        w = max(c.winfo_width(), 2)
        h = max(c.winfo_height(), 2)
        
        for fraction in (0.25, 0.50, 0.75):
            y_grid = h * fraction
            c.create_line(
                0, y_grid, w, y_grid,
                fill="#262b36",
                width=1,
                dash=(3, 5),
            )
        for fraction in (0.25, 0.50, 0.75):
            x_grid = w * fraction
            c.create_line(
                x_grid, 0, x_grid, h,
                fill="#171b23",
                width=1,
            )

        duration = self.graph_duration_ms
        if self.graph_actions and duration > 0:
            points = []
            for at, pos in self.graph_actions:
                x = (at / duration) * w
                y = h - 5 - (pos / 100.0) * (h - 10)
                points.extend((x, y))
            if len(points) >= 4:
                c.create_line(
                    *points,
                    fill="#b39cff",
                    width=2,
                    smooth=False,
                )

            x_cursor = (
                min(max(self.graph_position_ms / duration, 0.0), 1.0) * w
            )
            c.create_line(
                x_cursor, 0, x_cursor, h,
                fill="#ff263f",
                width=4,
            )
        else:
            c.create_text(
                12,
                h / 2,
                text=self.t("Choisis une vidéo avec son funscript"),
                fill="#c4cad6",
                anchor="w",
                font=("Noto Sans", 10, "bold"),
            )
            c.create_line(
                3, 0, 3, h,
                fill="#ff263f",
                width=4,
            )

    def send_mpv_command(self, command: list) -> bool:

        if self.process is None or self.process.poll() is not None:
            self.set_status(self.t("Aucune vidéo en lecture."), "warning")
            return False
        if not self.mpv_socket.exists():
            self.set_status(self.t("Contrôle MPV indisponible : socket IPC absent."), "danger")
            return False
        payload = json.dumps({"command": command}).encode("utf-8") + b"\n"
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.settimeout(0.5)
                client.connect(str(self.mpv_socket))
                client.sendall(payload)
            return True
        except OSError as exc:
            self.set_status((f"MPV control error: {exc}" if LANGUAGE == "en" else f"Erreur de contrôle MPV : {exc}"), "danger")
            return False

    def seek_relative(self, seconds: float) -> None:
        self.send_mpv_command(["seek", float(seconds), "relative+exact"])

    def toggle_pause(self, _event=None):
        self.send_mpv_command(["cycle", "pause"])
        return "break"

    def seek_from_graph(self, event):
        duration_ms = self.graph_duration_ms
        width = max(self.graph_canvas.winfo_width(), 1)
        if duration_ms <= 0:
            self.set_status(self.t("Durée de la vidéo inconnue."), "warning")
            return "break"
        ratio = min(max(event.x / width, 0.0), 1.0)
        seconds = (duration_ms * ratio) / 1000.0
        if self.send_mpv_command(["seek", seconds, "absolute+exact"]):
            self.graph_position_ms = int(seconds * 1000)
            self.draw_funscript_graph()
        return "break"

    def graph_mousewheel(self, event):
        if getattr(event, "num", None) == 4 or getattr(event, "delta", 0) > 0:
            self.seek_relative(5)
        else:
            self.seek_relative(-5)
        return "break"

    def update_graph_position(self) -> None:
        if self.process is not None and self.process.poll() is None:
            try:
                data = json.loads(
                    self.progress_file.read_text(encoding="utf-8")
                )
                self.graph_position_ms = int(
                    float(data.get("time_pos", 0.0)) * 1000
                )
                duration_ms = int(
                    float(data.get("duration", 0.0)) * 1000
                )
                if duration_ms > 0:
                    self.graph_duration_ms = duration_ms
                self.draw_funscript_graph()
            except (OSError, ValueError, TypeError, json.JSONDecodeError):
                pass

        
        self.after(80, self.update_graph_position)

    def add_scale(
        self, parent, row, label, variable, minimum, maximum, formatter
    ) -> None:
        ttk.Label(
            parent, text=self.t(label), style="CardText.TLabel"
        ).grid(row=row, column=0, sticky="w", pady=8)

        scale = ttk.Scale(
            parent,
            variable=variable,
            from_=minimum,
            to=maximum,
            orient="horizontal",
            style="Dark.Horizontal.TScale",
        )
        scale.grid(row=row, column=1, sticky="ew", padx=10, pady=8)

        value_label = ttk.Label(
            parent, width=9, anchor="e", style="Value.TLabel"
        )
        value_label.grid(row=row, column=2, sticky="e")

        def update(*_) -> None:
            value_label.configure(text=formatter(variable.get()))

        variable.trace_add("write", update)
        update()

    def set_status(self, text: str, kind: str = "neutral") -> None:
        colors = {
            "neutral": COLORS["muted"],
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "danger": COLORS["danger"],
        }
        self.status.set(text)
        ttk.Style(self).configure(
            "Status.TLabel",
            background=COLORS["panel_alt"],
            foreground=colors.get(kind, COLORS["muted"]),
            padding=(12, 9),
        )

    def toggle_app_fullscreen(self, _event=None) -> None:
        enabled = bool(self.attributes("-fullscreen"))
        self.attributes("-fullscreen", not enabled)

    def leave_app_fullscreen(self, _event=None) -> None:
        if bool(self.attributes("-fullscreen")):
            self.attributes("-fullscreen", False)
        try:
            self.attributes("-zoomed", True)
        except tk.TclError:
            pass

    def choose_video(self) -> None:
        initial = VIDEO_DIR if VIDEO_DIR.is_dir() else Path.home()
        chosen = filedialog.askopenfilename(
            title=self.t("Choisir une vidéo"),
            initialdir=str(initial),
            filetypes=((self.t("Vidéos"), "*.mp4 *.mkv *.avi *.mov *.webm *.m4v"), (self.t("Tous les fichiers"), "*")),
        )
        if not chosen:
            return

        video = Path(chosen)
        script = find_script(video)
        self.video_path.set(str(video))

        if script:
            self.load_funscript_graph(script)
            self.script_path.set(f"✓  {script}")
            self.script_label.configure(foreground=COLORS["success"])
            self.set_status(self.t("Funscript original trouvé. Conversion vibration automatique prête."), "success")
            self.launch_button.configure(state="normal")
            self.folder_button.configure(state="normal")
            self.next_button.configure(state="normal")
        else:
            self.clear_funscript_graph()
            self.script_path.set(
                (f"✕  No matching script in {SCRIPT_DIR}" if LANGUAGE == "en" else f"✕  Aucun script correspondant dans {SCRIPT_DIR}")
            )
            self.script_label.configure(foreground=COLORS["danger"])
            self.set_status(self.t("Aucun MelodyScript correspondant."), "danger")
            self.launch_button.configure(state="disabled")
            self.folder_button.configure(state="disabled")
            self.next_button.configure(state="disabled")
            messagebox.showwarning(
                self.t("MelodyScript introuvable"),
                (
                    "No funscript with the same base name as the video was found.\n\n"
                    f"Folder searched:\n{SCRIPT_DIR}\n\n"
                    f"Names searched:\n{video.stem}.vib.funscript\n{video.stem}.funscript"
                    if LANGUAGE == "en" else
                    "Aucun funscript portant le même nom que la vidéo n'a été trouvé.\n\n"
                    f"Dossier recherché :\n{SCRIPT_DIR}\n\n"
                    f"Noms recherchés :\n{video.stem}.vib.funscript\n{video.stem}.funscript"
                ),
            )


    def test_pump(self) -> None:

        if not PYTHON.is_file():
            messagebox.showerror(
                self.t("Python introuvable"),
                (f"Python environment not found:\n{PYTHON}" if LANGUAGE == "en" else f"Environnement Python introuvable :\n{PYTHON}")
            )
            return

        try:
            ensure_internal_engine()
        except OSError as exc:
            messagebox.showerror(
                self.t("Erreur du moteur intégré"),
                (f"Unable to prepare the test engine:\n{exc}" if LANGUAGE == "en" else f"Impossible de préparer le moteur de test :\n{exc}")
            )
            return

        self.stop()

        command = [
            str(PYTHON),
            str(PLAYER),
            "--test-pump",
            "--test-pump-seconds", "10",
            "--device", "JoyHub Melody",
            "--max-power", f"{self.max_power.get():.3f}",
            "--verbose",
            "--progress-file", str(self.progress_file),
        ]

        try:
            self.process = subprocess.Popen(command)
        except OSError as exc:
            messagebox.showerror(self.t("Erreur de lancement"), str(exc))
            return

        self.set_status(
            (f"Melody suction test running for 10 seconds — PID {self.process.pid}" if LANGUAGE == "en" else f"Test aspiration Melody en cours pendant 10 secondes — PID {self.process.pid}"),
            "warning",
        )
        self.after(100, self.check_process)


    def launch(self, video: Path | None = None, script: Path | None = None) -> None:
        if video is None:
            video = Path(self.video_path.get())
        if script is None:
            script_text = self.script_path.get().removeprefix("✓  ")
            script = Path(script_text)

        if not video.is_file() or not script.is_file():
            messagebox.showerror(
                self.t("Fichier introuvable"),
                self.t("La vidéo ou le MelodyScript n'existe plus.")
            )
            return

        if not PYTHON.is_file():
            messagebox.showerror(
                self.t("Python introuvable"),
                (f"Python environment not found:\n{PYTHON}" if LANGUAGE == "en" else f"Environnement Python introuvable :\n{PYTHON}")
            )
            return

        try:
            ensure_internal_engine()
        except OSError as exc:
            messagebox.showerror(
                self.t("Erreur du moteur intégré"),
                (f"Unable to prepare the playback engine:\n{exc}" if LANGUAGE == "en" else f"Impossible de préparer le moteur de lecture :\n{exc}")
            )
            return

        if not self.playlist_active:
            self.stop()
        self.stop_requested = False
        self.current_video = video
        self.current_script = script

        
        
        try:
            runtime_script = convertir_original_en_vibration_temporairement(
                script,
                video,
                self.amplification.get(),
            )
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            messagebox.showerror(
                self.t("Erreur de conversion"),
                (f"Unable to convert the original funscript to vibration:\n{exc}" if LANGUAGE == "en" else f"Impossible de convertir le funscript original en vibration :\n{exc}"),
            )
            return

        self.runtime_script = runtime_script
        self.load_funscript_graph(runtime_script)
        try:
            self.progress_file.unlink(missing_ok=True)
            self.mpv_socket.unlink(missing_ok=True)
        except OSError:
            pass
        self.save_config()

        command = [
            str(PYTHON),
            str(PLAYER),
            str(video),
            str(runtime_script),
            "--max-power", f"{self.max_power.get():.3f}",
            "--zero-hold-ms", str(int(self.zero_hold.get())),
            "--speed-smoothing", f"{self.smoothing.get():.3f}",
            "--min-running-power", f"{self.min_power.get():.3f}",
            "--min-change", "0.001",
            "--device", "JoyHub Melody",
            "--scan-seconds", "1.0",
            "--verbose",
            "--progress-file", str(self.progress_file),
            f"--mpv-arg=--input-ipc-server={self.mpv_socket}",
            "--mpv-arg=--screen=1",
            "--mpv-arg=--fs-screen=1",
        ]

        if self.pump_enabled.get():
            command.extend([
                "--pump",
                "--pump-seconds", f"{self.pump_seconds.get():.2f}",
                "--release-seconds", f"{self.release_seconds.get():.2f}",
                "--r4-interval", f"{self.r4_interval_seconds.get():.2f}",
                "--pause-min", f"{min(self.pause_min_seconds.get(), self.pause_max_seconds.get()):.2f}",
                "--pause-max", f"{max(self.pause_min_seconds.get(), self.pause_max_seconds.get()):.2f}",
                "--vibration-pattern", self.vibration_pattern.get(),
                "--vibration-pattern-2", normalize_pattern(self.vibration_pattern_2.get()),
                "--vibration-pattern-3", normalize_pattern(self.vibration_pattern_3.get()),
            ])
            if self.random_patterns_enabled.get():
                command.append("--random-vibration-patterns")

        if self.fullscreen.get():
            command.append("--mpv-arg=--fs")

        try:
            self.process = subprocess.Popen(command)
        except OSError as exc:
            messagebox.showerror(self.t("Erreur de lancement"), str(exc))
            return

        if LANGUAGE == "en":
            pump_text = (
                f" — PUMP {self.pump_seconds.get():.1f}s / R4 {self.r4_interval_seconds.get():.1f}s / pause {self.pause_min_seconds.get():.0f}-{self.pause_max_seconds.get():.0f}s / pattern {self.vibration_pattern.get()}"
                if self.pump_enabled.get() else " — pumping disabled"
            )
        else:
            pump_text = (
                f" — PUMP {self.pump_seconds.get():.1f}s / R4 {self.r4_interval_seconds.get():.1f}s / pause {self.pause_min_seconds.get():.0f}-{self.pause_max_seconds.get():.0f}s / motif {self.vibration_pattern.get()}"
                if self.pump_enabled.get() else " — pompage désactivé"
            )
        amplification_factor = 1.0 + 2.0 * self.amplification.get() / 100.0
        amplification_text = (
            (f" — amplification {self.amplification.get():.0f} % " if LANGUAGE == "fr" else f" — amplification {self.amplification.get():.0f}% ")
            + f"(x{amplification_factor:.2f})"
        )
        self.set_status(
            ((f"Playing: {video.name}" if LANGUAGE == "en" else f"Lecture en cours : {video.name}")
             + pump_text + amplification_text + f" — PID {self.process.pid}"),
            "success",
        )
        self.after(100, self.check_process)

    def next_video(self) -> None:
        video = self.current_video
        script = self.current_script

        if video is None:
            selected_text = self.video_path.get().strip()
            if selected_text:
                selected = Path(selected_text)
                if selected.is_file():
                    video = selected
                    script = find_script(selected)

        if video is None or not video.is_file():
            self.set_status(self.t("Aucune vidéo actuelle à passer."), "warning")
            return

        
        if not self.playlist_active:
            videos = sorted(
                [
                    path for path in video.parent.iterdir()
                    if path.is_file()
                    and path.suffix.casefold() in VIDEO_EXTENSIONS
                ],
                key=natural_key,
            )
            try:
                current_index = videos.index(video)
            except ValueError:
                self.set_status(
                    self.t("La vidéo actuelle n’est plus dans son dossier."),
                    "warning",
                )
                return

            self.playlist = [
                candidate
                for candidate in videos[current_index + 1:]
                if find_script(candidate)
            ]
            self.playlist_active = bool(self.playlist)

        deleted_count = 0
        if self.delete_after_end_var.get():
            deleted_count = len(self.delete_completed_files(video, script))

        if not self.playlist:
            self.playlist_active = False
            if self.process is not None and self.process.poll() is None:
                self.stop_requested = True
                self.process.terminate()

            if deleted_count:
                self.set_status(
                    ((f"{video.name} deleted ({deleted_count} file(s)). No next video." if LANGUAGE == "en"
                      else f"{video.name} supprimée ({deleted_count} fichier(s)). Aucune vidéo suivante.")),
                    "success",
                )
            else:
                self.set_status(self.t("Aucune vidéo suivante disponible."), "warning")
            return

        self.manual_next_requested = True
        self.stop_requested = False

        if deleted_count:
            self.set_status(
                ((f"{video.name} deleted ({deleted_count} file(s)). Moving to the next…" if LANGUAGE == "en"
                  else f"{video.name} supprimée ({deleted_count} fichier(s)). Passage à la suivante…")),
                "success",
            )
        else:
            self.set_status(self.t("Passage à la vidéo suivante…"), "neutral")

        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
        else:
            self.manual_next_requested = False
            self.current_video = None
            self.current_script = None
            self.after(50, self.play_next_in_playlist)

    def launch_folder_playlist(self) -> None:

        selected = Path(self.video_path.get())
        if not selected.is_file():
            messagebox.showerror(self.t("Vidéo introuvable"), self.t("Choisis d’abord une vidéo valide."))
            return

        videos = sorted(
            [
                path for path in selected.parent.iterdir()
                if path.is_file() and path.suffix.casefold() in VIDEO_EXTENSIONS
            ],
            key=natural_key,
        )
        try:
            start_index = videos.index(selected)
        except ValueError:
            messagebox.showerror(self.t("Erreur"), self.t("La vidéo sélectionnée n’est plus dans le dossier."))
            return

        playlist = [video for video in videos[start_index:] if find_script(video)]
        if not playlist:
            messagebox.showwarning(
                self.t("Aucune vidéo lisible"),
                self.t("Aucune vidéo à partir de la sélection ne possède un funscript correspondant."),
            )
            return

        self.stop()
        self.playlist = playlist
        self.playlist_active = True
        self.delete_after_natural_end = self.delete_after_end_var.get()
        self.stop_requested = False
        self.play_next_in_playlist()

    def play_next_in_playlist(self) -> None:
        while self.playlist:
            video = self.playlist.pop(0)
            script = find_script(video)
            if video.is_file() and script is not None and script.is_file():
                self.video_path.set(str(video))
                self.script_path.set(f"✓  {script}")
                self.script_label.configure(foreground=COLORS["success"])
                remaining = len(self.playlist) + 1
                self.set_status(
                    (f"Automatic playback: {video.name} — {remaining} remaining" if LANGUAGE == "en" else f"Lecture automatique : {video.name} — {remaining} restante(s)"),
                    "success",
                )
                self.launch(video, script)
                return

        self.playlist_active = False
        self.delete_after_natural_end = False
        self.current_video = None
        self.current_script = None
        self.set_status(self.t("Toutes les vidéos du dossier ont été traitées."), "success")
        messagebox.showinfo(self.t("Terminé"), self.t("La lecture du dossier est terminée."))

    def delete_completed_files(self, video: Path, script: Path | None) -> list[str]:

        deleted: list[str] = []
        errors: list[str] = []

        targets = [video, *script_candidates_for_deletion(video, script)]
        seen: set[Path] = set()
        for target in targets:
            try:
                resolved = target.resolve()
            except OSError:
                resolved = target.absolute()
            if resolved in seen:
                continue
            seen.add(resolved)

            if not target.is_file():
                continue
            try:
                target.unlink()
                deleted.append(str(target))
            except OSError as exc:
                errors.append(f"{target}: {exc}")

        if errors:
            messagebox.showwarning(
                self.t("Suppression partielle"),
                (("Some files could not be deleted:\n\n" if LANGUAGE == "en" else "Certains fichiers n’ont pas pu être supprimés :\n\n") + "\n".join(errors)),
            )
        return deleted

    def check_process(self) -> None:
        if self.process is None:
            return

        code = self.process.poll()
        if code is None:
            self.after(100, self.check_process)
            return

        finished_video = self.current_video
        finished_script = self.current_script
        self.process = None

        if self.manual_next_requested:
            self.manual_next_requested = False
            self.current_video = None
            self.current_script = None

            if self.playlist_active and self.playlist:
                self.after(50, self.play_next_in_playlist)
            else:
                self.playlist_active = False
                self.set_status(self.t("Aucune vidéo suivante disponible."), "warning")
            return

        
        if code == 20:
            deleted_count = 0

            if (
                self.playlist_active
                and self.delete_after_end_var.get()
                and not self.stop_requested
                and finished_video is not None
            ):
                deleted = self.delete_completed_files(finished_video, finished_script)
                deleted_count = len(deleted)

            if (
                self.playlist_active
                and self.play_next_var.get()
                and not self.stop_requested
            ):
                if deleted_count:
                    self.set_status(
                        ((f"Natural end: {finished_video.name if finished_video else 'video'} deleted ({deleted_count} file(s)). Moving to the next…" if LANGUAGE == "en"
                          else f"Fin naturelle : {finished_video.name if finished_video else 'vidéo'} supprimée ({deleted_count} fichier(s)). Passage à la suivante…")),
                        "success",
                    )
                else:
                    self.set_status(
                        ("Natural end. Moving to the next video…" if LANGUAGE == "en" else "Fin naturelle. Passage à la vidéo suivante…"),
                        "success",
                    )
                self.after(50, self.play_next_in_playlist)
            else:
                self.playlist_active = False
                self.playlist.clear()
                if deleted_count:
                    self.set_status(
                        ((f"Playback finished naturally. {deleted_count} file(s) deleted." if LANGUAGE == "en"
                          else f"Lecture terminée naturellement. {deleted_count} fichier(s) supprimé(s).")),
                        "success",
                    )
                else:
                    self.set_status(self.t("Lecture terminée naturellement."), "neutral")
        elif code == 0:
            self.set_status(
                self.t("Lecture fermée avant la fin : aucun fichier supprimé."),
                "warning",
            )
            if self.playlist_active:
                self.playlist_active = False
                self.playlist.clear()
        else:
            self.set_status(
                (f"Player stopped with code {code}. No files deleted." if LANGUAGE == "en" else f"Le lecteur s'est arrêté avec le code {code}. Aucun fichier supprimé."),
                "danger",
            )
            if self.playlist_active:
                self.playlist_active = False
                self.playlist.clear()

        self.current_video = None
        self.current_script = None

    def stop(self) -> None:
        self.stop_requested = True
        self.manual_next_requested = False
        self.playlist_active = False
        self.delete_after_natural_end = False
        self.playlist.clear()
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            self.set_status(self.t("Arrêt demandé… aucun fichier ne sera supprimé."), "warning")
        self.process = None

    def load_config(self) -> None:
        try:
            data = json.loads(CONFIG.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        self.max_power.set(float(data.get("max_power", 0.80)))
        self.zero_hold.set(int(data.get("zero_hold", 150)))
        self.smoothing.set(float(data.get("smoothing", 0.20)))
        self.min_power.set(float(data.get("min_power", 0.08)))
        self.amplification.set(float(data.get("amplification", 0.0)))
        self.fullscreen.set(bool(data.get("fullscreen", True)))
        self.pump_enabled.set(bool(data.get("pump_enabled", False)))
        self.pump_seconds.set(float(data.get("pump_seconds", 0.12)))
        self.release_seconds.set(float(data.get("release_seconds", 0.12)))
        self.vibration_pattern.set(str(data.get("vibration_pattern", "progressif3")))
        self.delete_after_end_var.set(
            bool(data.get("delete_after_end", False))
        )
        self.play_next_var.set(
            bool(data.get("play_next", True))
        )
        self.language = str(data.get("language", "fr"))

    def save_config(self) -> None:
        CONFIG.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "max_power": self.max_power.get(),
            "zero_hold": int(self.zero_hold.get()),
            "smoothing": self.smoothing.get(),
            "min_power": self.min_power.get(),
            "amplification": self.amplification.get(),
            "fullscreen": self.fullscreen.get(),
            "pump_enabled": self.pump_enabled.get(),
            "pump_seconds": self.pump_seconds.get(),
            "release_seconds": self.release_seconds.get(),
            "vibration_pattern": self.vibration_pattern.get(),
            "delete_after_end": self.delete_after_end_var.get(),
            "play_next": self.play_next_var.get(),
            "language": self.language,
        }
        CONFIG.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def on_close(self) -> None:
        self.save_config()
        self.stop()
        try:
            self.progress_file.unlink(missing_ok=True)
        except OSError:
            pass
        self.destroy()
