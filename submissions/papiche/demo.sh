#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Démonstration en commandes, dans l'ordre du récit. Lecture seule : aucune donnée n'est modifiée.
# Usage : ./demo.sh          (une pause à chaque étape : Entrée pour continuer)
#         ./demo.sh --auto   (enchaîne seul, 4 s entre deux étapes)
cd "$(dirname "$0")"
PY="${VEILLE_PYTHON:-python3}"
[ -x "$HOME/.astro/bin/python3" ] && [ -z "${VEILLE_PYTHON:-}" ] && PY="$HOME/.astro/bin/python3"
MODE_AUTO=0; [ "${1:-}" = "--auto" ] && MODE_AUTO=1

etape() {   # etape "Titre" commande...
  local titre="$1"; shift
  printf '\n\033[1;32m━━ %s\033[0m\n\033[0;36m$ %s\033[0m\n' "$titre" "$*"
  "$@"
  if [ "$MODE_AUTO" = 1 ]; then sleep 4; else read -r -p $'\n⏎ étape suivante… ' _; fi
}

etape "1. État du service : modèle local, base vectorielle, volumes" ./veille status
etape "2. Question en français : la réponse cite sa source" \
  ./veille ask "Quelle est la dose de LALSTOP G46 WG sur vigne en France ?"
etape "3. Tableau produit × pays × usage (valeur d'origine + valeur normalisée)" \
  ./veille compare --product "LALSTOP G46 WG"
etape "4. Même produit, autre pays : comparaison immédiate" ./veille compare --product "PRESTOP"
etape "5. Codes EPPO : nom libre → code officiel, lien vérifiable sur gd.eppo.int" \
  "$PY" -I -c "
import sys; sys.path.insert(0, '.')
from veille_reglementaire import eppo_codes as e
for nom, genre in (('Vignes', 'crop'), ('grey mould', 'pest'), ('Botrytis cinerea (Pers.)', 'pest'), ('Plasmopara viticola', 'pest')):
    r = e.normalize(nom, genre); code = r['eppo']
    print(f'{nom:28} -> {code or \"null\":8} [{r[\"method\"]}]', e.lien_eppo(code) if code else '')
"
etape "6. Mesure : exactitude face à la source structurée, valeurs inventées" ./veille eval
etape "7. Quand l'IA ne tranche pas : dossiers à relire par un expert" ./veille review
etape "8. Produits sœurs : hypothèses à confirmer, jamais affirmées" ./veille sisters
etape "9. Sobriété : chaque requête sortante est journalisée" ./veille network
printf '\n\033[1;32mFin de la démonstration.\033[0m Page de présentation : index.html\n'
