# SPDX-License-Identifier: AGPL-3.0-or-later
"""Client EPPO et appariement : aucun appel réseau, l'API est remplacée par un faux."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from veille_reglementaire import eppo_api, eppo_codes


class AppariementEppo(unittest.TestCase):
    def test_pluriel_et_accents(self):
        self.assertEqual(eppo_codes.normalize("Vignes", "crop")["eppo"], "VITVI")

    def test_nom_scientifique_avec_auteur(self):
        self.assertEqual(eppo_codes.normalize("Botrytis cinerea (Pers.)", "pest")["eppo"], "BOTRCI")

    def test_lien_fiche_officielle(self):
        self.assertEqual(eppo_codes.lien_eppo("VITVI"), "https://gd.eppo.int/taxon/VITVI")

    def test_api_acceptee_si_un_seul_code(self):
        ancien = eppo_api.codes_du_nom
        eppo_api.codes_du_nom = lambda nom: ["PLASVI"]
        try:
            self.assertEqual(eppo_codes.normalize("Plasmopara viticola", "pest")["eppo"], "PLASVI")
        finally:
            eppo_api.codes_du_nom = ancien

    def test_api_refusee_si_ambigue(self):
        ancien = eppo_api.codes_du_nom
        eppo_api.codes_du_nom = lambda nom: ["AAAAA", "BBBBB"]
        try:
            self.assertIsNone(eppo_codes.normalize("Organisme inconnu xyz", "pest")["eppo"])
        finally:
            eppo_api.codes_du_nom = ancien

    def test_sans_cle_api_indisponible(self):
        ancienne = os.environ.pop("EPPO_API_KEY", None)
        try:
            self.assertEqual(eppo_api.codes_du_nom("Vitis vinifera"), [])
        finally:
            if ancienne:
                os.environ["EPPO_API_KEY"] = ancienne


if __name__ == "__main__":
    unittest.main()
