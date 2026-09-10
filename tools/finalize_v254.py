#!/usr/bin/env python3
from __future__ import annotations

import ast
import io
import re
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "src" / "joyhub_melody"
PYPROJECT = ROOT / "pyproject.toml"
README = ROOT / "README.md"

FRENCH = re.compile(r"[àâçéèêëîïôûùüÿœ]|\b(afin|ajoute|aucun|avec|avant|choisir|commande|connexion|dossier|début|défile|écran|fichier|fenêtre|grille|lancement|lecture|même|moteur|nom|pour|priorité|retourne|script|sélection|supprime|uniquement|vidéo|vibration|lorsque|automatique|arrêt|réglage|langue|transforme|fichier|intensité|vitesse|mouvement)\b", re.I)


def strip_french_docstrings(source: str) -> str:
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    ranges = []

    def visit(body):
        if body and isinstance(body[0], ast.Expr):
            value = body[0].value
            if isinstance(value, ast.Constant) and isinstance(value.value, str) and FRENCH.search(value.value):
                ranges.append((body[0].lineno, body[0].end_lineno or body[0].lineno))
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                visit(node.body)

    visit(tree.body)
    for start, end in sorted(ranges, reverse=True):
        indent = re.match(r"\s*", lines[start - 1]).group(0)
        for index in range(start - 1, end):
            lines[index] = "\n" if lines[index].endswith("\n") else ""
        # A removed docstring is followed by real code in this project.
    return "".join(lines)


def strip_french_comments(source: str) -> str:
    tokens = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.COMMENT and not token.string.startswith("#!") and FRENCH.search(token.string):
            token = tokenize.TokenInfo(token.type, "", token.start, token.end, token.line)
        tokens.append(token)
    return tokenize.untokenize(tokens)


def main() -> None:
    for path in PACKAGE.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        text = strip_french_docstrings(text)
        text = strip_french_comments(text)
        path.write_text(text, encoding="utf-8")

    PYPROJECT.write_text('''[project]\nname = "joyhub-melody-player"\nversion = "2.5.4"\ndescription = "Linux BLE funscript player for JoyHub Melody"\nrequires-python = ">=3.11"\ndependencies = [\n    "bleak>=0.22",\n    "buttplug>=0.2",\n]\n\n[tool.uv]\npackage = false\npython-preference = "only-system"\n''', encoding="utf-8")

    if README.exists():
        text = README.read_text(encoding="utf-8")
        if "`buttplug`" not in text:
            marker = "Do not run `uv sync` with `sudo`."
            replacement = "Python dependencies (`bleak` and `buttplug`) are installed automatically by `uv sync`.\n\n" + marker
            text = text.replace(marker, replacement, 1)
            README.write_text(text, encoding="utf-8")

    # Remove one-time migration helpers after successful finalization.
    (ROOT / "tools" / "refactor_v254.py").unlink(missing_ok=True)
    (ROOT / ".github" / "workflows" / "refactor-v254.yml").unlink(missing_ok=True)
    Path(__file__).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
