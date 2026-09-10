#!/usr/bin/env python3
from __future__ import annotations

import ast
import io
import re
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "JoyHub-Melody-Player.py"
PACKAGE = ROOT / "src" / "joyhub_melody"
README = ROOT / "README.md"
REQUIREMENTS = ROOT / "requirements.txt"
PYPROJECT = ROOT / "pyproject.toml"
LAUNCHER = ROOT / "JoyHub-Melody-Player-v2.5.4.py"


def segment(lines: list[str], node: ast.AST) -> str:
    end = getattr(node, "end_lineno", node.lineno)
    return "".join(lines[node.lineno - 1:end]).rstrip() + "\n"


def comments_english_only(source: str) -> str:
    french = re.compile(r"[àâçéèêëîïôûùüÿœ]|\b(afin|ajoute|aucun|avec|avant|choisir|commande|connexion|dossier|début|défile|écran|fichier|fenêtre|grille|lancement|lecture|même|moteur|nom|pour|priorité|retourne|script|sélection|supprime|uniquement|vidéo|vibration|lorsque|automatique|arrêt|réglage|langue)\b", re.I)
    out = []
    stream = tokenize.generate_tokens(io.StringIO(source).readline)
    for token in stream:
        if token.type == tokenize.COMMENT and not token.string.startswith("#!"):
            text = token.string.lstrip("# ")
            if french.search(text):
                token = tokenize.TokenInfo(token.type, "", token.start, token.end, token.line)
        out.append(token)
    return tokenize.untokenize(out)


def update_readme(text: str) -> str:
    text = text.replace("v2.5.3", "v2.5.4")
    block = '''\n## uv deployment\n\nThe recommended deployment method is [`uv`](https://docs.astral.sh/uv/). The project uses the system Python so Tkinter remains provided by the Linux distribution.\n\n### Debian / Ubuntu\n\n```bash\nsudo apt update\nsudo apt install -y python3 python3-tk mpv bluetooth bluez\n```\n\nInstall `uv` using the official installation method, then clone and synchronize the project:\n\n```bash\ngit clone https://github.com/st3ph666/JoyHub-Melody-Player.git\ncd JoyHub-Melody-Player\nuv sync\nuv run python JoyHub-Melody-Player-v2.5.4.py\n```\n\nDo not run `uv sync` with `sudo`. Bluetooth access remains managed by the normal Linux user session and BlueZ.\n\n### Update an existing installation\n\n```bash\ngit pull\nuv sync\nuv run python JoyHub-Melody-Player-v2.5.4.py\n```\n\n## Source architecture\n\n```text\nJoyHub-Melody-Player-v2.5.4.py  # Compatibility launcher\nsrc/joyhub_melody/\n├── __init__.py                 # Version metadata\n├── settings.py                 # Paths, UI strings, patterns and colors\n├── engine.py                   # Embedded BLE engine bundle installer\n├── funscript.py                # Funscript discovery and conversion helpers\n├── app.py                      # Tkinter application\n└── main.py                     # Application entry point\n```\n\nSource-code comments are maintained in **English only**. The graphical interface remains bilingual French / English.\n\n'''
    if "## uv deployment" not in text:
        marker = "## Installation"
        if marker in text:
            text = text.replace(marker, block + marker, 1)
        else:
            text += block
    return text


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    lines = source.splitlines(keepends=True)
    tree = ast.parse(source)
    nodes = tree.body

    assignments = []
    funcs = {}
    class_node = None
    for node in nodes:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            assignments.append(node)
        elif isinstance(node, ast.FunctionDef):
            funcs[node.name] = node
        elif isinstance(node, ast.ClassDef) and node.name == "VibrationPlayerGUI":
            class_node = node

    if class_node is None:
        raise RuntimeError("VibrationPlayerGUI not found")

    assignment_by_name = {}
    for node in assignments:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target, ast.Name):
                assignment_by_name[target.id] = node

    settings_names = [
        "VIDEO_DIR", "SCRIPT_DIR", "PLAYER", "APP_VERSION", "APP_NAME", "PYTHON", "CONFIG",
        "VIDEO_EXTENSIONS", "VIBRATION_PATTERN_NAMES", "VIDEO_TYPES", "LANGUAGE", "TRANSLATIONS", "COLORS",
    ]
    engine_names = ["ENGINE_BUNDLE"]

    PACKAGE.mkdir(parents=True, exist_ok=True)

    settings = '''"""Application settings, translations, paths, patterns, and colors."""\n\nimport os\nimport sys\nfrom pathlib import Path\n\n'''
    for name in settings_names:
        settings += segment(lines, assignment_by_name[name]) + "\n"
    settings += segment(lines, funcs["tr"]) + "\n" + segment(lines, funcs["normalize_pattern"])
    settings = settings.replace('APP_VERSION = "v2.5.3"', 'APP_VERSION = "v2.5.4"')

    engine = '''"""Embedded Melody BLE engine installer."""\n\nimport base64\nimport zlib\n\nfrom .settings import PLAYER\n\n'''
    for name in engine_names:
        engine += segment(lines, assignment_by_name[name]) + "\n"
    engine += segment(lines, funcs["ensure_internal_engine"])

    funscript = '''"""Funscript discovery, conversion, ordering, and cleanup helpers."""\n\nimport json\nimport os\nimport re\nimport tempfile\nfrom pathlib import Path\n\nfrom .settings import SCRIPT_DIR\n\n'''
    for name in ("find_script", "convertir_original_en_vibration_temporairement", "natural_key", "script_candidates_for_deletion"):
        funscript += segment(lines, funcs[name]) + "\n"

    app = '''"""Tkinter application for JoyHub Melody Player."""\n\nimport json\nimport os\nimport socket\nimport subprocess\nimport tempfile\nfrom pathlib import Path\nimport tkinter as tk\nfrom tkinter import filedialog, messagebox, ttk\n\nfrom .settings import *  # noqa: F403,F401\nfrom .engine import ensure_internal_engine\nfrom .funscript import (\n    convertir_original_en_vibration_temporairement,\n    find_script,\n    natural_key,\n    script_candidates_for_deletion,\n)\n\n'''
    app += segment(lines, class_node)

    init = '''"""JoyHub Melody Player package."""\n\n__version__ = "2.5.4"\n'''
    main_module = '''"""Application entry point."""\n\nfrom .app import VibrationPlayerGUI\n\n\ndef main() -> int:\n    app = VibrationPlayerGUI()\n    app.mainloop()\n    return 0\n\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n'''
    launcher = '''#!/usr/bin/env python3\n"""Compatibility launcher for JoyHub Melody Player v2.5.4."""\n\nfrom pathlib import Path\nimport sys\n\nROOT = Path(__file__).resolve().parent\nSRC = ROOT / "src"\nif str(SRC) not in sys.path:\n    sys.path.insert(0, str(SRC))\n\nfrom joyhub_melody.main import main\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n'''

    (PACKAGE / "__init__.py").write_text(init, encoding="utf-8")
    (PACKAGE / "settings.py").write_text(comments_english_only(settings), encoding="utf-8")
    (PACKAGE / "engine.py").write_text(comments_english_only(engine), encoding="utf-8")
    (PACKAGE / "funscript.py").write_text(comments_english_only(funscript), encoding="utf-8")
    (PACKAGE / "app.py").write_text(comments_english_only(app), encoding="utf-8")
    (PACKAGE / "main.py").write_text(main_module, encoding="utf-8")
    LAUNCHER.write_text(launcher, encoding="utf-8")
    LAUNCHER.chmod(0o755)

    PYPROJECT.write_text('''[project]\nname = "joyhub-melody-player"\nversion = "2.5.4"\ndescription = "Linux BLE funscript player for JoyHub Melody"\nrequires-python = ">=3.11"\ndependencies = [\n    "bleak>=0.22.0",\n]\n\n[tool.uv]\npackage = false\npython-preference = "only-system"\n''', encoding="utf-8")

    if README.exists():
        README.write_text(update_readme(README.read_text(encoding="utf-8")), encoding="utf-8")

    # Keep requirements.txt for users who do not use uv.
    if REQUIREMENTS.exists():
        req = REQUIREMENTS.read_text(encoding="utf-8")
        if "bleak" not in req.lower():
            REQUIREMENTS.write_text("bleak>=0.22.0\n", encoding="utf-8")

    SOURCE.unlink()


if __name__ == "__main__":
    main()
