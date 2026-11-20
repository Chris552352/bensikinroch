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
    panneau,
    route_pseudo3d,
    texte_ombre,
    texte_bloc,
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
        self.font_xl = pygame.font.SysFont("dejavusans", 42, bold=True)
        self.font_l = pygame.font.SysFont("dejavusans", 27, bold=True)
        self.font = pygame.font.SysFont("dejavusans", 22)
        self.font_s = pygame.font.SysFont("dejavusans", 18)
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

        panneau(self.ecran, (28, 40, 334, 610))
        texte_ombre(self.ecran, self.font_s, "CAMEROUN  /  MOTO-TAXI", (50, 64), C.JAUNE)
        texte_ombre(self.ecran, self.font_l, "BENSIKIN ROCH", (50, 108), C.BLANC)
        texte_bloc(self.ecran, self.font_l, "Motard d'honneur du Cameroun", (50, 156, 288, 120))
        texte_bloc(self.ecran, self.font, "Respecte la route : on te prime. Tu enfreins : on te coupe.", (50, 280, 280, 120))
        texte_bloc(self.ecran, self.font_s, "La caisse peut passer sous zéro. L'honneur, lui, se gagne au guidon.", (50, 398, 280, 100))
        moto_roch(self.ecran, 195, 548, math.sin(self.t) * .2, True, True, False)
        texte_ombre(self.ecran, self.font_l, "Choisis ta journée", (390, 32), C.JAUNE)
        caisse = int(self.profil.get("caisse_globale", 0))
        col_c = C.JAUNE if caisse >= 0 else C.ROUGE
        carte(self.ecran, "Caisse du syndicat", 390, 80, 750, 100, col_c)
        texte_ombre(self.ecran, self.font_l, fcfa(caisse).replace("+", ""), (410, 126), col_c)
        texte_ombre(
            self.ecran, self.font_s,
            f"Journées : {self.profil.get('journees', 0)}   Honneur : {self.profil.get('honneur', 0)}",
            (720, 136), C.CREME,
        )

        y = 196
        for i, niv in enumerate(C.NIVEAUX):
            lock = i >= int(self.profil.get("debloque", 1))
            sel = i == self.curseur
            panneau(self.ecran, (390, y, 750, 72), C.JAUNE if sel else (66, 105, 88), sel)
            texte_ombre(self.ecran, self.font_l, f"{i + 1:02}", (408, y + 18), C.JAUNE if sel else C.CREME)
            texte_ombre(self.ecran, self.font, niv['nom'], (462, y + 7), C.BLANC if not lock else (177, 193, 185))
            statut = "Verrouillé" if lock else "Disponible"
            texte_ombre(self.ecran, self.font_s, f"{niv['surnom']}  ·  {statut}  ·  {niv['difficulte']}/5", (462, y + 40), C.CREME)
            y += 80

        extras = ["Comment on joue (l'honneur du bitume)", "Quitter le guidon"]
        for j, lab in enumerate(extras):
            idx = n_niveaux + j
            sel = self.curseur == idx
            panneau(self.ecran, (390, y, 750, 40), C.JAUNE if sel else (66, 105, 88), sel)
            texte_ombre(self.ecran, self.font_s, lab, (412, y + 8), C.JAUNE if sel else C.BLANC)
            y += 48

        texte_ombre(
            self.ecran, self.font_s,
            "↑ ↓  Choisir     ENTRÉE  Prendre le guidon     ·     La sécurité routière avant tout.",
            (40, 696), C.CREME,
        )

    def _comment(self, events):
        self.ecran.fill(C.VERT_FONCE)
        bande_drapeau(self.ecran)
        for e in events:
            if e.type == pygame.KEYDOWN:
                self.scene = "menu"
        texte_ombre(self.ecran, self.font_xl, "Le code Roch", (60, 36), C.JAUNE)
        panneau(self.ecran, (36, 100, 1108, 570))
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
        y = 118
        for lig in lignes:
            texte_ombre(self.ecran, self.font_s, lig, (60, y), C.CREME)
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
            self.ecran, C.LARGEUR / 2, 565, j.inclinaison, j.phare, j.casque_passager,
            j.niveau.get("moment") == "nuit",
        )
        self._hud(j)

    def _hud(self, j: Journee):
        panneau(self.ecran, (16, 16, 540, 116))
        panneau(self.ecran, (568, 16, 370, 116))
        panneau(self.ecran, (950, 16, 214, 116), C.JAUNE)
        texte_ombre(self.ecran, self.font, j.niveau["nom"], (34, 28), C.JAUNE)
        reste = max(0, int(j.duree - j.temps))
        texte_ombre(self.ecran, self.font_s, f"Journée · {reste} s restantes", (34, 62), C.CREME)
        col = C.JAUNE if j.caisse_jour >= 0 else (255, 140, 130)
        texte_ombre(self.ecran, self.font_l, fcfa(j.caisse_jour), (34, 88), col)
        texte_ombre(self.ecran, self.font_s, "HONNEUR DU BITUME", (590, 28), C.CREME)
        texte_ombre(self.ecran, self.font_s, f"Respect {j.journal.respects}  ·  Coupes {j.journal.fautes}", (590, 57), C.BLANC)
        texte_ombre(self.ecran, self.font_s, f"Feux grillés : {j.feux_grilles}", (590, 82), C.CREME)
        total = max(1, j.journal.respects + j.journal.fautes)
        ratio = j.journal.respects / total if (j.journal.respects + j.journal.fautes) else .5
        pygame.draw.rect(self.ecran, (43, 66, 56), (590, 113, 324, 6), border_radius=3)
        pygame.draw.rect(self.ecran, C.VERT if ratio >= .5 else C.ROUGE, (590, 113, int(324 * ratio), 6), border_radius=3)
        texte_ombre(self.ecran, self.font_xl, str(int(j.vitesse)), (976, 28), C.BLANC)
        texte_ombre(self.ecran, self.font_s, "km/h", (978, 86), C.JAUNE)
        if j.poursuite:
            panneau(self.ecran, (100, 144, 980, 48), C.ROUGE, True)
            texte_ombre(self.ecran, self.font_s, "POURSUITE POLICE · ESPACE pour te rendre · Fuir = fourrière + caisse coupée", (120, 156), C.JAUNE)

        obs = j.courant()
        if obs and not obs.resolu:
            y_alerte = 204 if j.poursuite else 148
            panneau(self.ecran, (100, y_alerte, 980, 120), C.JAUNE, True)
            texte_ombre(self.ecran, self.font, obs.modele["nom"].upper(), (124, y_alerte + 10), C.JAUNE)
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
            texte_bloc(self.ecran, self.font_s, obs.modele["consigne"], (124, y_alerte + 44, 930, 32), C.CREME)
            texte_ombre(self.ecran, self.font, touche, (124, y_alerte + 78), C.BLANC)

        for flash in j.flashs[-1:]:
            panneau(self.ecran, (24, 570, 460, 100), C.VERT if flash.ok else C.ROUGE)
            texte_bloc(self.ecran, self.font_s, flash.texte, (42, 582, 420, 78), C.CREME)

        pygame.draw.rect(self.ecran, (10, 25, 21), (0, 682, C.LARGEUR, 38))
        texte_ombre(
            self.ecran, self.font_s,
            "↑ gaz   ↓ frein   ESPACE stop   C casque   P phare   K klaxon   T téléphone=piège   ESC menu",
            (16, 692), C.CREME,
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
        carte(self.ecran, "Montant du jour · FCFA", 40, 180, 510, 120, col)
        texte_ombre(self.ecran, self.font_xl, fcfa(recette), (80, 230), col)

        carte(self.ecran, "Détail du syndicat", 40, 320, 510, 340, C.JAUNE)
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
        y = 370
        for d in details:
            texte_ombre(self.ecran, self.font_s, d, (60, y), C.CREME)
            y += 30

        carte(self.ecran, "Carnet du bitume · dernières épreuves", 574, 180, 566, 368, C.JAUNE)
        lignes = b.get("lignes", [])
        if not lignes:
            texte_bloc(self.ecran, self.font, "Le bitume attend tes premières épreuves.", (596, 250, 520, 100))
        y = 230
        for lig in lignes[-4:]:
            c = (114, 225, 165) if lig["ok"] else (255, 160, 146)
            texte_ombre(self.ecran, self.font_s, fcfa(int(lig['montant'])), (596, y), c)
            texte_bloc(self.ecran, self.font_s, lig['texte'], (756, y, 362, 70), C.CREME)
            y += 76
        panneau(self.ecran, (574, 566, 566, 94))
        texte_bloc(self.ecran, self.font_s, b.get("morale", ""), (596, 582, 520, 66), C.BLANC)
        texte_ombre(self.ecran, self.font_s, "ENTRÉE — retour au carrefour", (60, 684), C.JAUNE)
