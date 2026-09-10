"""Funscript discovery, conversion, ordering, and cleanup helpers."""

import json
import os
import re
import tempfile
from pathlib import Path

from .settings import SCRIPT_DIR

def find_script(video: Path) -> Path | None:
    
    candidates = [
        video.with_suffix(".funscript"),
        video.with_suffix(".vib.funscript"),
        SCRIPT_DIR / f"{video.stem}.funscript",
        SCRIPT_DIR / f"{video.stem}.vib.funscript",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None

def convertir_original_en_vibration_temporairement(
    script: Path,
    video: Path,
    amplification_percent: float = 0.0,
) -> Path:
    """
    Transforme le funscript linéaire en intensité de vibration par plateaux.

    Le fichier généré est temporaire :
      0 = arrêt, 1..100 = intensité de vibration.
    L'intensité dépend de la vitesse du mouvement du funscript original.

    Amplification :
      0 %   = calcul normal (x1)
      50 %  = environ x2
      100 % = environ x3
    """
    amplification_percent = max(0.0, min(100.0, float(amplification_percent)))
    amplification_factor = 1.0 + 2.0 * (amplification_percent / 100.0)

    donnees = json.loads(script.read_text(encoding="utf-8-sig"))
    actions_source = donnees.get("actions", [])
    actions = []

    for action in actions_source:
        try:
            at = max(0, int(action["at"]))
            pos = max(0, min(100, int(action["pos"])))
        except (KeyError, TypeError, ValueError):
            continue
        actions.append((at, pos))

    actions.sort(key=lambda item: item[0])
    if len(actions) < 2:
        raise ValueError("Le funscript original contient moins de deux actions valides.")

    
    uniques = []
    for action in actions:
        if uniques and uniques[-1][0] == action[0]:
            uniques[-1] = action
        else:
            uniques.append(action)

    sortie = [{"at": 0, "pos": 0}]

    def ajouter(at: int, pos: int) -> None:
        element = {"at": max(0, int(at)), "pos": max(0, min(100, int(pos)))}
        if sortie and sortie[-1]["at"] == element["at"]:
            sortie[-1] = element
        elif not sortie or sortie[-1] != element:
            sortie.append(element)

    for index in range(1, len(uniques)):
        debut, pos_debut = uniques[index - 1]
        fin, pos_fin = uniques[index]
        duree = fin - debut
        amplitude = abs(pos_fin - pos_debut)

        if duree <= 0:
            continue

        
        if amplitude < 2 or (duree >= 2500 and amplitude < 8):
            commande = 0
        else:
            vitesse = amplitude * 1000.0 / duree
            vitesse_amplifiee = vitesse * amplification_factor
            
            
            puissance = max(0.20, min(1.0, vitesse_amplifiee / 160.0))
            commande = int(round(puissance * 100.0))

        ajouter(debut, commande)
        ajouter(fin, commande)

    ajouter(uniques[-1][0], 0)

    resultat = dict(donnees)
    resultat["actions"] = sortie
    resultat["inverted"] = False
    resultat["range"] = 100
    resultat["runtime_vibration_conversion"] = True
    resultat["runtime_amplification_percent"] = amplification_percent
    resultat["runtime_amplification_factor"] = amplification_factor

    destination = Path(tempfile.gettempdir()) / (
        f"vibration-runtime-{os.getpid()}-{video.stem}.vib.funscript"
    )
    destination.write_text(
        json.dumps(resultat, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return destination

def natural_key(path: Path) -> list[object]:
    return [
        int(part) if part.isdigit() else part.casefold()
        for part in re.split(r"(\d+)", path.name)
    ]

def script_candidates_for_deletion(video: Path, selected_script: Path | None) -> list[Path]:
    """Retourne tous les scripts portant exactement le nom de la vidéo."""
    folders = [
        video.parent,
        video.parent / "rotation",
        video.parent / "Rotation",
        video.parent / "VibrationScript",
        SCRIPT_DIR,
    ]
    candidates: list[Path] = []
    if selected_script is not None:
        candidates.append(selected_script)
    for folder in folders:
        candidates.extend([
            folder / f"{video.stem}.funscript",
            folder / f"{video.stem}.vib.funscript",
        ])

    unique: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            resolved = candidate.absolute()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(candidate)
    return unique

