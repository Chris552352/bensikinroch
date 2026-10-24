"""Caisse, records et niveaux débloqués — persistés en JSON."""

from __future__ import annotations

import json
from pathlib import Path

from .constantes import CAISSE_DEPART, FICHIER_SAVE, NIVEAUX


def chemin_save() -> Path:
    return Path(__file__).resolve().parent.parent / FICHIER_SAVE


def defaut() -> dict:
    return {
        "caisse_globale": CAISSE_DEPART,
        "journees": 0,
        "meilleure_recette": None,
        "pire_dette": 0,
        "debloque": 1,
        "honneur": 0,
        "historique": [],
    }


def charger() -> dict:
    p = chemin_save()
    if not p.exists():
        return defaut()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        base = defaut()
        base.update(data)
        base["debloque"] = max(1, min(len(NIVEAUX), int(base.get("debloque", 1))))
        return base
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return defaut()


def enregistrer(data: dict) -> None:
    p = chemin_save()
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def appliquer_bilan(profil: dict, bilan: dict) -> dict:
    profil = dict(profil)
    recette = int(bilan["recette"])
    profil["caisse_globale"] = int(profil.get("caisse_globale", 0)) + recette
    profil["journees"] = int(profil.get("journees", 0)) + 1
    hist = list(profil.get("historique", []))
    hist.append(
        {
            "niveau": bilan["niveau"],
            "recette": recette,
            "honneur": bilan["honneur"],
            "fautes": bilan["fautes"],
            "titre": bilan["titre"],
        }
    )
    profil["historique"] = hist[-20:]

    best = profil.get("meilleure_recette")
    if best is None or recette > best:
        profil["meilleure_recette"] = recette
    if recette < int(profil.get("pire_dette", 0)):
        profil["pire_dette"] = recette

    if recette >= 0 and bilan["fautes"] <= 2:
        idx = next((i for i, n in enumerate(NIVEAUX) if n["nom"] == bilan["niveau"]), 0)
        profil["debloque"] = max(int(profil.get("debloque", 1)), min(len(NIVEAUX), idx + 2))

    profil["honneur"] = int(profil.get("honneur", 0)) + int(bilan["honneur"])
    return profil
