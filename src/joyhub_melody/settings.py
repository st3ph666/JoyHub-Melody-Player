"""Application settings, translations, paths, patterns, and colors."""

import os
import sys
from pathlib import Path

VIDEO_DIR = Path(os.environ.get("JOYHUB_VIDEO_DIR", str(Path.home() / "Videos")))

SCRIPT_DIR = VIDEO_DIR / "MelodyScript"

PLAYER = Path.home() / ".cache/melody-player/melody-ble-direct-engine.py"

APP_VERSION = "v2.5.4"

APP_NAME = f"JoyHub Melody Player {APP_VERSION}"

PYTHON = Path(sys.executable)

CONFIG = Path.home() / ".config/melody-player-ble-direct-gui.json"

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v"}

VIBRATION_PATTERN_NAMES = (
    "progressif3",
    "regulier3",
    "double",
    "coeur",
    "rafale5",
    "pulse4",
    "pulse6",
    "pulse8",
    "court_long",
    "long_court",
    "triple_sec",
    "triple_large",
    "vague4",
    "vague6",
    "escalier4",
    "escalier6",
    "syncopé",
    "staccato",
    "lent2",
    "lent3",
    "rafale3",
    "rafale7",
    "respire4",
    "alterné",
    "surprise",
)

VIDEO_TYPES = (
    ("Vidéos", "*.mp4 *.mkv *.avi *.mov *.webm *.m4v"),
    ("Tous les fichiers", "*"),
)

LANGUAGE = "fr"

TRANSLATIONS = {
    "Vidéos": "Videos",
    "Tous les fichiers": "All files",
    "Aucun script sélectionné": "No script selected",
    "Choisis une vidéo pour commencer.": "Choose a video to begin.",
    "Aucun": "None",
    "VIBRATION FUNSCRIPT — clique ou glisse pour déplacer la vidéo": "VIBRATION FUNSCRIPT — click or drag to seek the video",
    "Pause / Reprendre": "Pause / Resume",
    "JoyHub Melody BLE direct — connexion mémorisée + schémas vibration + R4": "JoyHub Melody direct BLE — remembered connection + vibration patterns + R4",
    "Sélection": "Selection",
    "Vidéo": "Video",
    "Parcourir": "Browse",
    "Script": "Script",
    "Réglages": "Settings",
    "Vibration maximale": "Maximum vibration",
    "Maintien à zéro": "Zero hold",
    "Lissage": "Smoothing",
    "Vibration minimale": "Minimum vibration",
    "Amplification du funscript": "Funscript amplification",
    "Amplification vibration": "Vibration amplification",
    "Activer le contrôle PUMP / R4 (CONSTRICT)": "Enable PUMP / R4 control (CONSTRICT)",
    "Contrôle PUMP / R4": "PUMP / R4 control",
    "Ouvrir MPV en plein écran sur l’écran de droite": "Open MPV fullscreen on the right display",
    "Activer le PUMP / aspiration Melody": "Enable Melody PUMP / suction",
    "Durée du PUMP": "PUMP duration",
    "Durée du relâchement": "Release duration",
    "R4 répété toutes les": "Repeat R4 every",
    "Pause minimale entre PUMP": "Minimum pause between PUMPs",
    "Pause maximale entre PUMP": "Maximum pause between PUMPs",
    "Schéma vibration 1": "Vibration pattern 1",
    "Schéma vibration 2": "Vibration pattern 2",
    "Schéma vibration 3": "Vibration pattern 3",
    "Choisir aléatoirement parmi les 1 à 3 schémas sélectionnés": "Randomly choose among the 1 to 3 selected patterns",
    "Supprimer la vidéo et ses funscripts à la fin ou en passant à la suivante": "Delete the video and its funscripts when finished or skipping to the next",
    "Passer automatiquement à la vidéo suivante": "Automatically play the next video",
    "▶  Lancer la vidéo": "▶  Play video",
    "⏭  Lire le dossier": "⏭  Play folder",
    "⏩  Vidéo suivante": "⏩  Next video",
    "🧪  Test aspiration Melody 10 s": "🧪  Test Melody suction 10 s",
    "■  Arrêter": "■  Stop",
    "Choisis une vidéo avec son funscript": "Choose a video with its funscript",
    "Aucune vidéo en lecture.": "No video is currently playing.",
    "Durée de la vidéo inconnue.": "Unknown video duration.",
    "Choisir une vidéo": "Choose a video",
    "Funscript original trouvé. Conversion vibration automatique prête.": "Original funscript found. Automatic vibration conversion is ready.",
    "Aucun MelodyScript correspondant.": "No matching MelodyScript.",
    "MelodyScript introuvable": "MelodyScript not found",
    "Python introuvable": "Python not found",
    "Erreur du moteur intégré": "Embedded engine error",
    "Erreur de lancement": "Launch error",
    "Fichier introuvable": "File not found",
    "La vidéo ou le MelodyScript n'existe plus.": "The video or MelodyScript no longer exists.",
    "Erreur de conversion": "Conversion error",
    "Aucune vidéo actuelle à passer.": "There is no current video to skip.",
    "La vidéo actuelle n’est plus dans son dossier.": "The current video is no longer in its folder.",
    "Aucune vidéo suivante disponible.": "No next video is available.",
    "Passage à la vidéo suivante…": "Moving to the next video…",
    "Vidéo introuvable": "Video not found",
    "Choisis d’abord une vidéo valide.": "Choose a valid video first.",
    "Erreur": "Error",
    "La vidéo sélectionnée n’est plus dans le dossier.": "The selected video is no longer in the folder.",
    "Aucune vidéo lisible": "No playable video",
    "Aucune vidéo à partir de la sélection ne possède un funscript correspondant.": "No video from the selection onward has a matching funscript.",
    "Toutes les vidéos du dossier ont été traitées.": "All videos in the folder have been processed.",
    "La lecture du dossier est terminée.": "Folder playback is complete.",
    "Terminé": "Done",
    "Lecture terminée naturellement.": "Playback finished naturally.",
    "Lecture fermée avant la fin : aucun fichier supprimé.": "Playback was closed before completion: no files were deleted.",
    "Arrêt demandé… aucun fichier ne sera supprimé.": "Stop requested… no files will be deleted.",
    "Contrôle MPV indisponible : socket IPC absent.": "MPV control unavailable: IPC socket missing.",
    "Suppression partielle": "Partial deletion",
    "Aucune vidéo suivante.": "No next video.",
}

COLORS = {
    "bg": "#111318",
    "panel": "#191c22",
    "panel_alt": "#20242c",
    "border": "#2c313b",
    "text": "#f2f4f8",
    "muted": "#9aa3b2",
    "accent": "#7c5cff",
    "accent_hover": "#9278ff",
    "success": "#39d98a",
    "warning": "#ffb84d",
    "danger": "#ff5c72",
    "track": "#343a46",
}

def tr(text: str) -> str:
    if LANGUAGE == "en":
        return TRANSLATIONS.get(text, text)
    return text

def normalize_pattern(value: str) -> str:
    """Return the engine sentinel regardless of the UI language."""
    return "Aucun" if value in ("Aucun", "None") else value
