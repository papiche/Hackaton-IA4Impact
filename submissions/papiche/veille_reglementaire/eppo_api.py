# SPDX-License-Identifier: AGPL-3.0-or-later
"""API officielle EPPO Global Database (api.eppo.int, v2). La clé vient de EPPO_API_KEY, jamais du dépôt.

Deux services suffisent : « name2codes » (nom exact -> code) et « names » (tous les noms d'un code, toutes langues).
Chaque réponse est gardée sur disque : un même appel n'est jamais refait, la source n'est pas sollicitée pour rien.
"""
from __future__ import annotations
import hashlib, json, os
from urllib.parse import quote
from . import config, polite_http

URL_API = "https://api.eppo.int/gd/v2"
LANGUES_UTILES = ("la", "fr", "en", "pt")


def cle_api() -> str | None:
    return os.environ.get("EPPO_API_KEY") or None


def disponible() -> bool:
    return cle_api() is not None


def _fichier_cache(chemin: str):
    return config.CACHE / f"eppo_api_{hashlib.sha256(chemin.encode()).hexdigest()}.json"


def _appeler(chemin: str):
    fichier = _fichier_cache(chemin)
    if fichier.exists():
        return json.loads(fichier.read_text(encoding="utf-8"))
    reponse = polite_http.send_request(f"{URL_API}{chemin}", headers={"X-Api-Key": cle_api()})
    reponse.raise_for_status()
    fichier.write_text(reponse.text, encoding="utf-8")
    return reponse.json()


def codes_du_nom(nom: str) -> list[str]:
    """Codes dont le nom exact (latin ou autre) est `nom`. Vide si l'API est indisponible ou ne connaît pas le nom."""
    if not disponible() or not nom.strip():
        return []
    try:
        return [r["eppocode"] for r in _appeler(f"/tools/name2codes?name={quote(nom.strip())}")]
    except Exception:
        return []


def noms_du_code(code: str) -> list[str]:
    """Noms officiels d'un code dans les langues utiles (latin, français, anglais, portugais), sans doublon."""
    if not disponible():
        return []
    try:
        noms = [n["fullname"] for n in _appeler(f"/taxons/taxon/{quote(code)}/names") if n["lang_iso"] in LANGUES_UTILES]
    except Exception:
        return []
    return list(dict.fromkeys(noms))
