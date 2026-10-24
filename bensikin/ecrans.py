"""Menus, HUD, bilan de journée — pygame."""

from __future__ import annotations

import math

import pygame

from . import constantes as C
from .dessin import (
    bande_drapeau,
    carte,
    dessiner_decor,
    dessiner_mobile,
    dessiner_obstacle,
    fcfa,
    moto_roch,
    route_pseudo3d,
    texte_ombre,
)
from .moteur import Journee
from .sauvegarde import appliquer_bilan, charger, enregistrer
from .visuel import Atlas


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(C.TITRE)
        self.ecran = pygame.display.set_mode((C.LARGEUR, C.HAUTEUR))
        self.horloge = pygame.time.Clock()
        self.atlas = Atlas()
        self.font_xl = pygame.font.SysFont("georgia", 40, bold=True)
        self.font_l = pygame.font.SysFont("georgia", 26, bold=True)
        self.font = pygame.font.SysFont("calibri", 20)
        self.font_s = pygame.font.SysFont("calibri", 16)
        self.scene = "menu"
        self.profil = charger()
        self.curseur = 0
        self.journee: Journee | None = None
        self.bilan = None
        self.t = 0.0

    def boucle(self) -> None:
        vivant = True
        while vivant:
            dt = self.horloge.tick(C.FPS) / 1000.0
            self.t += dt
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    vivant = False
            etat = pygame.key.get_pressed()
            if self.scene == "menu":
                self._menu(events)
            elif self.scene == "comment":
                self._comment(events)
            elif self.scene == "jeu":
                self._jeu(events, etat, dt)
            elif self.scene == "bilan":
                self._bilan(events)
            pygame.display.flip()
        pygame.quit()

    def _fond_menu(self):
        route_pseudo3d(self.ecran, math.sin(self.t) * 40, self.t * 40, 0.8, C.NIVEAUX[0], self.t)
        voile = pygame.Surface((C.LARGEUR, C.HAUTEUR), pygame.SRCALPHA)
        voile.fill((6, 18, 14, 145))
        self.ecran.blit(voile, (0, 0))
        moto_roch(self.ecran, 200, 560, math.sin(self.t) * 0.3, True, True, False)
        bande_drapeau(self.ecran)

    def _menu(self, events):
        self._fond_menu()
        n_niveaux = len(C.NIVEAUX)
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_DOWN, pygame.K_s):
                    self.curseur = (self.curseur + 1) % (n_niveaux + 2)
                elif e.key in (pygame.K_UP, pygame.K_z, pygame.K_w):
                    self.curseur = (self.curseur - 1) % (n_niveaux + 2)
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.curseur < n_niveaux:
                        if self.curseur < int(self.profil.get("debloque", 1)):
                            self.journee = Journee(C.NIVEAUX[self.curseur], self.profil)
                            self.scene = "jeu"
                    elif self.curseur == n_niveaux:
                        self.scene = "comment"
                    else:
                        pygame.event.post(pygame.event.Event(pygame.QUIT))

        texte_ombre(self.ecran, self.font_xl, "BENSIKIN ROCH", (360, 40), C.JAUNE)
        texte_ombre(self.ecran, self.font_l, "Motard d'honneur du Cameroun", (360, 90), C.BLANC)
        texte_ombre(
            self.ecran, self.font,
            "Respecte la route : on te prime. Tu enfreins : on te coupe. La caisse peut passer sous zéro.",
            (360, 126), C.CREME,
        )
        caisse = int(self.profil.get("caisse_globale", 0))
        col_c = C.JAUNE if caisse >= 0 else C.ROUGE
        carte(self.ecran, "Caisse du syndicat", 360, 168, 760, 66, col_c)
        texte_ombre(self.ecran, self.font_l, fcfa(caisse).replace("+", ""), (390, 198), col_c)
        texte_ombre(
            self.ecran, self.font_s,
            f"Journées : {self.profil.get('journees', 0)}   Honneur : {self.profil.get('honneur', 0)}   "
            f"Pire dette : {fcfa(int(self.profil.get('pire_dette', 0)))}",
            (620, 206), C.GRIS,
        )

        y = 250
        for i, niv in enumerate(C.NIVEAUX):
            lock = i >= int(self.profil.get("debloque", 1))
            sel = i == self.curseur
            fond = (20, 50, 38) if sel else (12, 28, 22)
            pygame.draw.rect(self.ecran, fond, (360, y, 760, 56), border_radius=10)
            pygame.draw.rect(self.ecran, C.JAUNE if sel else C.VERT, (360, y, 760, 56), 2, border_radius=10)
            etoiles = "★" * niv["difficulte"] + "☆" * (5 - niv["difficulte"])
            nom = niv["nom"] if not lock else f"Verrouillé — {niv['nom']}"
            texte_ombre(self.ecran, self.font, nom, (380, y + 6), C.JAUNE if not lock else C.GRIS)
            texte_ombre(self.ecran, self.font_s, f"{niv['surnom']}   {etoiles}", (380, y + 30), C.CREME)
            y += 60

        extras = ["Comment on joue (l'honneur du bitume)", "Quitter le guidon"]
        for j, lab in enumerate(extras):
            idx = n_niveaux + j
            sel = self.curseur == idx
            pygame.draw.rect(self.ecran, (20, 40, 32) if sel else (10, 20, 16), (360, y, 760, 38), border_radius=8)
            texte_ombre(self.ecran, self.font, lab, (390, y + 8), C.JAUNE if sel else C.BLANC)
            y += 44

        texte_ombre(
            self.ecran, self.font_s,
            "↑↓ choisir   ENTRÉE valider   — un jeu de sécurité routière, pas un simulateur de fuite.",
            (40, 690), C.GRIS,
        )

    def _comment(self, events):
        self.ecran.fill(C.VERT_FONCE)
        bande_drapeau(self.ecran)
        for e in events:
            if e.type == pygame.KEYDOWN:
                self.scene = "menu"
        texte_ombre(self.ecran, self.font_xl, "Le code Roch", (60, 36), C.JAUNE)
        lignes = [
            "Tu es Roch, bensikin. Ta journée n'est pas un score : c'est une caisse, en FCFA.",
            "Chaque élément de route est une épreuve. Tu respectes → PRIME. Tu piétines → COUPE.",
            "À la tombée, le syndicat sort le rendu. Le montant peut être négatif. La dette est réelle.",
            "",
            "HAUT / Z       accélérer (jamais un droit, toujours un risque)",
            "BAS / S        freiner : dos d'âne, marché, chèvre, école",
            "ESPACE         STOP franc — feu rouge, contrôle, panneau STOP",
            "GAUCHE/DROITE  tenir sa voie, esquiver nid-de-poule, refuser le contre-sens",
            "C casque au passager    P phare    K klaxon court    T téléphone (piège !)",
            "",
            "New Bell, Warda, Pont du Wouri, Nationale N3, Bépanda sous la pluie.",
            "Plus c'est dur, plus la prime gonfle — et plus la coupe arrache.",
            "Finis une journée propre (caisse ≥ 0, ≤ 2 fautes) pour débloquer la suite.",
            "",
            "Inspiré des vrais bitumes : dos d'âne de quartier, Fuso, mama au bassin, radar de village.",
            "Appuie sur une touche pour retourner au carrefour.",
        ]
        y = 100
        for lig in lignes:
            texte_ombre(self.ecran, self.font, lig, (60, y), C.CREME)
            y += 32

    def _lire_touches(self, events, etat) -> dict:
        edge = {"casque": False, "phare": False, "klaxon": False, "telephone": False}
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_c:
                    edge["casque"] = True
                if e.key == pygame.K_p:
                    edge["phare"] = True
                if e.key == pygame.K_k:
                    edge["klaxon"] = True
                if e.key == pygame.K_t:
                    edge["telephone"] = True
                if e.key == pygame.K_ESCAPE:
                    self.scene = "menu"
                    self.journee = None
        edge.update(
            {
                "accel": etat[pygame.K_UP] or etat[pygame.K_z] or etat[pygame.K_w],
                "frein": etat[pygame.K_DOWN] or etat[pygame.K_s],
                "stop": etat[pygame.K_SPACE],
                "gauche": etat[pygame.K_LEFT] or etat[pygame.K_q] or etat[pygame.K_a],
                "droite": etat[pygame.K_RIGHT] or etat[pygame.K_d],
            }
        )
        return edge

    def _jeu(self, events, etat, dt):
        j = self.journee
        if j is None:
            self.scene = "menu"
            return
        touches = self._lire_touches(events, etat)
        j.actualiser(dt, touches)
        if j.termine:
            self.bilan = j.bilan()
            self.profil = appliquer_bilan(self.profil, self.bilan)
            enregistrer(self.profil)
            self.scene = "bilan"
            return

        route_pseudo3d(
            self.ecran, j.joueur_x, j.distance, j.niveau["courbure"], j.niveau, self.t
        )
        objets = (
            [(d.z, "d", d) for d in j.decors]
            + [(o.z, "o", o) for o in j.obstacles]
            + [(m.z, "m", m) for m in j.mobiles]
        )
        courb = j.niveau["courbure"]
        for _z, typ, obj in sorted(objets, key=lambda it: -it[0]):
            if typ == "d":
                dessiner_decor(self.ecran, self.atlas, obj, j.joueur_x, courb, j.distance)
            elif typ == "m":
                dessiner_mobile(self.ecran, self.atlas, obj, j.joueur_x, courb, j.distance, self.t)
            else:
                dessiner_obstacle(self.ecran, self.atlas, obj, j.joueur_x, courb, j.distance)

        moto_roch(
            self.ecran, C.LARGEUR / 2, 600, j.inclinaison, j.phare, j.casque_passager,
            j.niveau.get("moment") == "nuit",
        )
        self._hud(j)

    def _hud(self, j: Journee):
        pygame.draw.rect(self.ecran, (8, 16, 14), (0, 0, C.LARGEUR, 72))
        w = C.LARGEUR // 3
        pygame.draw.rect(self.ecran, C.VERT, (0, 0, w, 4))
        pygame.draw.rect(self.ecran, C.ROUGE, (w, 0, w, 4))
        pygame.draw.rect(self.ecran, C.JAUNE, (2 * w, 0, C.LARGEUR - 2 * w, 4))

        texte_ombre(self.ecran, self.font, j.niveau["nom"], (16, 12), C.JAUNE)
        reste = max(0, int(j.duree - j.temps))
        texte_ombre(self.ecran, self.font_s, f"Fin de journée dans {reste} s   ·   {j.niveau['surnom']}", (16, 38), C.CREME)
        col = C.JAUNE if j.caisse_jour >= 0 else C.ROUGE
        texte_ombre(self.ecran, self.font_l, fcfa(j.caisse_jour), (16, 54), col)

        pygame.draw.circle(self.ecran, (16, 16, 18), (1080, 86), 58)
        pygame.draw.circle(self.ecran, C.JAUNE, (1080, 86), 58, 3)
        texte_ombre(self.ecran, self.font_l, f"{int(j.vitesse)}", (1048, 62), C.BLANC)
        texte_ombre(self.ecran, self.font_s, "km/h", (1062, 96), C.GRIS)

        total = max(1, j.journal.respects + j.journal.fautes)
        ratio = j.journal.respects / total if (j.journal.respects + j.journal.fautes) else 0.5
        pygame.draw.rect(self.ecran, (30, 30, 30), (400, 58, 280, 12), border_radius=6)
        pygame.draw.rect(
            self.ecran, C.VERT if ratio >= 0.5 else C.ROUGE,
            (400, 58, int(280 * ratio), 12), border_radius=6,
        )
        texte_ombre(
            self.ecran, self.font_s,
            f"Respect {j.journal.respects}   Coupes {j.journal.fautes}   Feux grillés {j.feux_grilles}",
            (400, 36), C.BLANC,
        )
        if j.poursuite:
            pygame.draw.rect(self.ecran, C.ROUGE, (180, 78, 820, 28), border_radius=6)
            texte_ombre(
                self.ecran, self.font,
                "POURSUITE POLICE — ESPACE pour te rendre   fuir = fourrière + caisse coupée",
                (200, 80), C.JAUNE,
            )

        obs = j.courant()
        if obs and not obs.resolu:
            pygame.draw.rect(self.ecran, (12, 10, 8), (180, 100, 820, 78), border_radius=12)
            pygame.draw.rect(self.ecran, C.ROUGE, (180, 100, 820, 78), 2, border_radius=12)
            texte_ombre(self.ecran, self.font, obs.modele["nom"].upper(), (200, 108), C.JAUNE)
            action = obs.modele["action"]
            touche = {
                "stop": "ESPACE = arrêt franc",
                "ralentir": "BAS = ralentir",
                "frein": "BAS = freiner",
                "casque": "C = casque au client",
                "phare": "P = allumer le phare",
                "klaxon": "K = klaxon court",
                "esquive": "GAUCHE/DROITE = esquiver le cratère",
                "droite": "DROITE = refuser le contre-sens",
                "ignorer": "Ne touche PAS à T (téléphone)",
            }.get(action, "")
            texte_ombre(self.ecran, self.font_s, obs.modele["consigne"], (200, 134), C.CREME)
            texte_ombre(self.ecran, self.font_s, touche, (200, 154), C.BLANC)

        y = 200
        for flash in reversed(j.flashs):
            texte_ombre(self.ecran, self.font_s, flash.texte[:88], (20, y), C.VERT if flash.ok else C.ROUGE)
            y += 22

        texte_ombre(
            self.ecran, self.font_s,
            "↑ gaz   ↓ frein   ESPACE stop   C casque   P phare   K klaxon   T téléphone=piège   ESC menu",
            (16, 694), C.GRIS,
        )

    def _bilan(self, events):
        b = self.bilan or {}
        self.ecran.fill((8, 16, 14))
        pygame.draw.rect(self.ecran, C.VERT, (0, 0, C.LARGEUR, 7))
        pygame.draw.rect(self.ecran, C.ROUGE, (0, 7, C.LARGEUR, 7))
        pygame.draw.rect(self.ecran, C.JAUNE, (0, 14, C.LARGEUR, 7))

        for e in events:
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                self.scene = "menu"
                self.journee = None

        texte_ombre(self.ecran, self.font_xl, "Rendu de la journée", (60, 40), C.JAUNE)
        texte_ombre(self.ecran, self.font, b.get("niveau", ""), (60, 92), C.CREME)
        texte_ombre(self.ecran, self.font_l, b.get("titre", ""), (60, 124), C.BLANC)

        recette = int(b.get("recette", 0))
        col = C.JAUNE if recette >= 0 else C.ROUGE
        carte(self.ecran, "Montant du jour (peut être négatif)", 60, 180, 520, 120, col)
        texte_ombre(self.ecran, self.font_xl, fcfa(recette), (80, 230), col)

        carte(self.ecran, "Détail du syndicat", 60, 320, 520, 280, C.VERT)
        details = [
            f"Courses clients     {b.get('courses', 0)}   ({fcfa(int(b.get('recette_courses', 0)))})",
            f"Primes de respect   {fcfa(int(b.get('primes', 0)))}",
            f"Coupes / amendes    - {int(b.get('coupes', 0)):,} FCFA".replace(",", " "),
            f"Éléments respectés  {b.get('respects', 0)}",
            f"Fautes              {b.get('fautes', 0)}",
            f"Feux grillés        {b.get('feux_grilles', 0)}",
            f"Note de conduite    {b.get('note', 0)} / 20",
            f"Honneur du jour     {b.get('honneur', 0)}",
            f"Caisse globale      {fcfa(int(self.profil.get('caisse_globale', 0))).replace('+', '')}",
        ]
        y = 365
        for d in details:
            texte_ombre(self.ecran, self.font, d, (80, y), C.CREME)
            y += 28

        carte(self.ecran, "Carnet du bitume", 620, 180, 500, 420, C.JAUNE)
        y = 230
        for lig in b.get("lignes", []):
            c = C.VERT if lig["ok"] else C.ROUGE
            texte_ombre(self.ecran, self.font_s, f"{fcfa(int(lig['montant']))}  {lig['texte'][:42]}", (640, y), c)
            y += 22
        texte_ombre(self.ecran, self.font, b.get("morale", ""), (640, 560), C.BLANC)
        texte_ombre(self.ecran, self.font_s, "ENTRÉE — retour au carrefour", (640, 600), C.GRIS)
