"""Atlas : vrais panneaux du code de la route (usage camerounais) et décors de quartier."""

from __future__ import annotations

import pygame

from . import constantes as C


def _police(taille, gras=True):
    return pygame.font.SysFont("arial", taille, bold=gras)


def _surf(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def _centre_texte(s, font, msg, col, cy=None, cx=None):
    img = font.render(msg, True, col)
    r = img.get_rect(center=(s.get_width() // 2 if cx is None else cx, s.get_height() // 2 if cy is None else cy))
    s.blit(img, r)
    return img


def poteau(s, x, y0, y1, ep=6):
    pygame.draw.line(s, (90, 90, 92), (x, y0), (x, y1), ep)
    pygame.draw.line(s, (60, 60, 62), (x - 2, y0), (x - 2, y1), 2)


def panneau_stop():
    s = _surf(110, 200)
    poteau(s, 55, 78, 198)
    pts = [(55, 8), (92, 22), (106, 58), (92, 94), (55, 108), (18, 94), (4, 58), (18, 22)]
    pygame.draw.polygon(s, (20, 20, 20), [(p[0] + 2, p[1] + 2) for p in pts])
    pygame.draw.polygon(s, C.BLANC, pts)
    inner = [(55, 16), (86, 28), (98, 58), (86, 88), (55, 100), (24, 88), (12, 58), (24, 28)]
    pygame.draw.polygon(s, C.ROUGE, inner)
    _centre_texte(s, _police(22), "STOP", C.BLANC, 58)
    return s


def panneau_vitesse(lim: int):
    s = _surf(100, 190)
    poteau(s, 50, 88, 188)
    pygame.draw.circle(s, (20, 20, 20), (52, 50), 44)
    pygame.draw.circle(s, C.ROUGE, (50, 48), 42)
    pygame.draw.circle(s, C.BLANC, (50, 48), 32)
    _centre_texte(s, _police(28), str(lim), (20, 20, 24), 48)
    return s


def panneau_danger(ligne1: str, ligne2: str = ""):
    s = _surf(120, 200)
    poteau(s, 60, 100, 198)
    pygame.draw.polygon(s, (20, 20, 20), [(62, 6), (116, 98), (8, 98)])
    pygame.draw.polygon(s, C.ROUGE, [(60, 8), (112, 96), (8, 96)])
    pygame.draw.polygon(s, C.JAUNE, [(60, 22), (98, 88), (22, 88)])
    font = _police(14)
    _centre_texte(s, font, ligne1, (20, 20, 20), 62 if not ligne2 else 54)
    if ligne2:
        _centre_texte(s, font, ligne2, (20, 20, 20), 74)
    return s


def panneau_ecole():
    s = panneau_danger("ÉCOLE", "ENFANTS")
    return s


def panneau_interdit():
    s = _surf(100, 190)
    poteau(s, 50, 88, 188)
    pygame.draw.circle(s, C.ROUGE, (50, 48), 40)
    pygame.draw.circle(s, C.BLANC, (50, 48), 30)
    pygame.draw.rect(s, C.ROUGE, (22, 42, 56, 12), border_radius=2)
    return s


def panneau_ville(nom: str):
    s = _surf(170, 90)
    pygame.draw.rect(s, (18, 70, 48), (4, 8, 162, 54), border_radius=4)
    pygame.draw.rect(s, C.BLANC, (8, 12, 154, 46), border_radius=3)
    font = _police(16)
    _centre_texte(s, font, nom.upper()[:16], (20, 20, 20), 35)
    pygame.draw.rect(s, (90, 90, 90), (80, 62, 10, 28))
    return s


def panneau_direction(gauche: str, droite: str):
    s = _surf(150, 120)
    pygame.draw.rect(s, (70, 70, 74), (70, 58, 10, 60))
    pygame.draw.rect(s, (18, 90, 55), (8, 8, 134, 52), border_radius=4)
    font = _police(14)
    s.blit(font.render(f"← {gauche[:10]}", True, C.BLANC), (14, 14))
    s.blit(font.render(f"{droite[:10]} →", True, C.BLANC), (14, 34))
    return s


def panneau_casque():
    s = _surf(140, 200)
    poteau(s, 70, 110, 198)
    pygame.draw.rect(s, (20, 40, 90), (8, 8, 124, 100), border_radius=6)
    pygame.draw.rect(s, C.BLANC, (12, 12, 116, 92), border_radius=4)
    _centre_texte(s, _police(12), "CASQUE", (20, 20, 20), 28)
    _centre_texte(s, _police(12), "OBLIGATOIRE", C.ROUGE, 48)
    pygame.draw.ellipse(s, C.ROUGE, (48, 58, 44, 30))
    pygame.draw.rect(s, C.JAUNE, (58, 70, 24, 6))
    return s


def feu_tricolore(rouge=True):
    s = _surf(50, 220)
    poteau(s, 25, 118, 218, 8)
    pygame.draw.rect(s, (25, 25, 28), (8, 4, 34, 112), border_radius=8)
    pygame.draw.circle(s, C.ROUGE if rouge else (70, 20, 20), (25, 28), 12)
    pygame.draw.circle(s, (90, 80, 20), (25, 58), 12)
    pygame.draw.circle(s, (20, 90, 30), (25, 88), 12)
    if rouge:
        pygame.draw.circle(s, (255, 80, 80), (25, 28), 8)
    return s


def controle_gendarmerie():
    s = _surf(220, 180)
    pygame.draw.rect(s, (30, 50, 110), (20, 40, 90, 70))
    pygame.draw.polygon(s, C.ROUGE, [(20, 40), (65, 12), (110, 40)])
    pygame.draw.rect(s, C.JAUNE, (20, 40, 90, 8))
    _centre_texte(s, _police(10), "GENDARMERIE", C.BLANC, 70, 65)
    _centre_texte(s, _police(9), "CONTRÔLE", C.JAUNE, 88, 65)
    pygame.draw.rect(s, C.VERT, (130, 8, 18, 50))
    pygame.draw.rect(s, C.ROUGE, (148, 8, 18, 50))
    pygame.draw.rect(s, C.JAUNE, (166, 8, 18, 50))
    pygame.draw.line(s, C.ROUGE, (12, 120), (210, 78), 6)
    pygame.draw.circle(s, (40, 40, 20), (24, 132), 16)
    pygame.draw.circle(s, (40, 40, 20), (200, 88), 16)
    pygame.draw.rect(s, (35, 55, 100), (48, 100, 22, 48))
    pygame.draw.circle(s, (62, 40, 22), (59, 92), 8)
    pygame.draw.rect(s, C.ROUGE, (48, 84, 22, 6))
    return s


def boutique(nom: str, mur=(186, 140, 78)):
    s = _surf(200, 180)
    pygame.draw.rect(s, mur, (18, 58, 164, 110))
    pygame.draw.polygon(s, (92, 92, 98), [(10, 62), (100, 18), (190, 62)])
    pygame.draw.polygon(s, (70, 70, 74), [(14, 62), (100, 24), (186, 62)])
    pygame.draw.rect(s, (20, 20, 22), (18, 58, 164, 28))
    font = _police(11)
    img = font.render(nom[:22], True, C.JAUNE)
    s.blit(img, img.get_rect(center=(100, 72)))
    pygame.draw.rect(s, (40, 90, 50), (28, 98, 44, 70))
    pygame.draw.rect(s, (30, 70, 110), (84, 104, 36, 28))
    pygame.draw.rect(s, (30, 70, 110), (128, 104, 36, 28))
    pygame.draw.rect(s, (120, 40, 30), (84, 140, 80, 28))
    return s


def taxi_cote():
    """Taxi garé sur l'accotement, vu de profil."""
    s = _surf(140, 80)
    pygame.draw.rect(s, C.JAUNE, (12, 28, 116, 32), border_radius=6)
    pygame.draw.polygon(s, C.JAUNE, [(28, 28), (44, 10), (88, 10), (108, 28)])
    pygame.draw.rect(s, (120, 180, 210), (46, 14, 38, 16))
    pygame.draw.circle(s, (20, 20, 22), (38, 62), 12)
    pygame.draw.circle(s, (20, 20, 22), (108, 62), 12)
    pygame.draw.rect(s, C.ROUGE, (18, 36, 14, 6))
    return s


def taxi_arriere():
    """Vu de derrière, comme Roch : étroit, feux arrière, plaque."""
    s = _surf(70, 92)
    pygame.draw.rect(s, C.JAUNE, (12, 28, 46, 44), border_radius=3)
    pygame.draw.rect(s, (200, 160, 20), (16, 8, 38, 24), border_radius=3)
    pygame.draw.rect(s, (50, 110, 150), (20, 12, 30, 16))
    pygame.draw.rect(s, (30, 30, 32), (12, 66, 46, 6))
    pygame.draw.rect(s, C.ROUGE, (14, 50, 10, 8))
    pygame.draw.rect(s, C.ROUGE, (46, 50, 10, 8))
    pygame.draw.ellipse(s, (16, 16, 18), (10, 72, 20, 16))
    pygame.draw.ellipse(s, (16, 16, 18), (40, 72, 20, 16))
    pygame.draw.rect(s, C.BLANC, (24, 58, 22, 8))
    s.blit(_police(6).render("CM", True, (20, 20, 20)), (28, 58))
    return s


def taxi_avant():
    """Qui arrive en face : phares, pare-brise."""
    s = _surf(70, 92)
    pygame.draw.rect(s, C.JAUNE, (12, 30, 46, 42), border_radius=3)
    pygame.draw.rect(s, (200, 160, 20), (14, 8, 42, 26), border_radius=3)
    pygame.draw.polygon(s, (80, 150, 190), [(18, 32), (35, 10), (52, 32)])
    pygame.draw.rect(s, C.BLANC, (14, 48, 12, 8))
    pygame.draw.rect(s, C.BLANC, (44, 48, 12, 8))
    pygame.draw.ellipse(s, (16, 16, 18), (10, 72, 20, 16))
    pygame.draw.ellipse(s, (16, 16, 18), (40, 72, 20, 16))
    pygame.draw.rect(s, (25, 25, 25), (28, 52, 14, 6))
    return s


def call_box():
    s = _surf(90, 140)
    pygame.draw.polygon(s, C.ROUGE, [(8, 48), (45, 8), (82, 48)])
    pygame.draw.rect(s, (20, 20, 22), (28, 48, 10, 88))
    pygame.draw.rect(s, C.JAUNE, (18, 70, 54, 28), border_radius=3)
    _centre_texte(s, _police(9), "CALL", (20, 20, 20), 84)
    return s


def palmier():
    s = _surf(90, 160)
    pygame.draw.line(s, (90, 55, 25), (45, 158), (48, 50), 8)
    for a, b in ((-30, 28), (-12, 8), (8, 6), (28, 22), (0, 32)):
        pygame.draw.line(s, (18, 110, 48), (48, 50), (48 + a, 50 + b), 4)
    return s


def mama_bassin():
    s = _surf(70, 110)
    pygame.draw.circle(s, (70, 42, 24), (35, 28), 12)
    pygame.draw.polygon(s, (180, 40, 70), [(18, 40), (52, 40), (48, 88), (22, 88)])
    pygame.draw.ellipse(s, (220, 120, 30), (12, 8, 46, 18))
    pygame.draw.circle(s, C.JAUNE, (20, 12), 4)
    pygame.draw.circle(s, C.ROUGE, (35, 10), 4)
    pygame.draw.circle(s, (40, 140, 60), (50, 12), 4)
    pygame.draw.line(s, (70, 42, 24), (26, 88), (22, 108), 3)
    pygame.draw.line(s, (70, 42, 24), (44, 88), (48, 108), 3)
    return s


def ecoliers():
    s = _surf(90, 90)
    for i, x in enumerate((18, 44, 70)):
        pygame.draw.circle(s, (62, 38, 22), (x, 28), 8)
        pygame.draw.rect(s, (40, 70, 140) if i != 1 else (200, 80, 120), (x - 10, 36, 20, 28))
        pygame.draw.line(s, (62, 38, 22), (x - 6, 64), (x - 8, 84), 2)
        pygame.draw.line(s, (62, 38, 22), (x + 6, 64), (x + 8, 84), 2)
    return s


def chevre():
    s = _surf(90, 60)
    pygame.draw.rect(s, (220, 220, 210), (12, 22, 48, 18), border_radius=4)
    pygame.draw.circle(s, (220, 220, 210), (62, 20), 10)
    pygame.draw.line(s, (220, 220, 210), (68, 14), (78, 4), 2)
    pygame.draw.line(s, (90, 80, 70), (20, 38), (16, 56), 3)
    pygame.draw.line(s, (90, 80, 70), (30, 38), (32, 56), 3)
    pygame.draw.line(s, (90, 80, 70), (48, 38), (46, 56), 3)
    pygame.draw.line(s, (90, 80, 70), (56, 38), (60, 56), 3)
    return s


def camion_arriere():
    s = _surf(110, 100)
    pygame.draw.rect(s, (70, 90, 40), (18, 8, 74, 72))
    pygame.draw.rect(s, (40, 50, 28), (22, 12, 66, 50))
    pygame.draw.rect(s, C.ROUGE, (26, 66, 16, 8))
    pygame.draw.rect(s, C.ROUGE, (68, 66, 16, 8))
    pygame.draw.ellipse(s, (18, 18, 20), (22, 76, 26, 18))
    pygame.draw.ellipse(s, (18, 18, 20), (62, 76, 26, 18))
    pygame.draw.rect(s, C.JAUNE, (48, 70, 14, 6))
    return s


def camion_avant():
    s = _surf(110, 100)
    pygame.draw.rect(s, (70, 90, 40), (22, 18, 66, 62))
    pygame.draw.rect(s, (40, 50, 28), (18, 8, 74, 28))
    pygame.draw.rect(s, (90, 170, 210), (30, 14, 50, 18))
    pygame.draw.rect(s, C.BLANC, (26, 48, 16, 8))
    pygame.draw.rect(s, C.BLANC, (68, 48, 16, 8))
    pygame.draw.ellipse(s, (18, 18, 20), (22, 76, 26, 18))
    pygame.draw.ellipse(s, (18, 18, 20), (62, 76, 26, 18))
    return s


def camion_fuso():
    return camion_arriere()


def panneau_cede():
    """Cédez le passage : triangle inversé (pointe en bas)."""
    s = _surf(100, 190)
    poteau(s, 50, 92, 188)
    pygame.draw.polygon(s, C.ROUGE, [(8, 10), (92, 10), (50, 88)])
    pygame.draw.polygon(s, C.BLANC, [(18, 16), (82, 16), (50, 74)])
    _centre_texte(s, _police(9), "CÉDEZ", (20, 20, 20), 32)
    return s


def panneau_priorite():
    s = _surf(100, 190)
    poteau(s, 50, 90, 188)
    pygame.draw.polygon(s, C.BLANC, [(50, 8), (90, 48), (50, 88), (10, 48)])
    pygame.draw.polygon(s, C.JAUNE, [(50, 18), (78, 48), (50, 78), (22, 48)])
    return s


def panneau_travaux():
    return panneau_danger("TRAVAUX")


def panneau_depassement():
    s = _surf(100, 190)
    poteau(s, 50, 90, 188)
    pygame.draw.circle(s, C.ROUGE, (50, 48), 40)
    pygame.draw.circle(s, C.BLANC, (50, 48), 30)
    pygame.draw.rect(s, (20, 20, 24), (28, 40, 12, 20), border_radius=2)
    pygame.draw.rect(s, C.ROUGE, (48, 36, 12, 24), border_radius=2)
    return s


def panneau_stationnement():
    s = _surf(100, 190)
    poteau(s, 50, 90, 188)
    pygame.draw.circle(s, C.BLEU_POLICE, (50, 48), 40)
    _centre_texte(s, _police(28), "P", C.BLANC, 48)
    pygame.draw.line(s, C.ROUGE, (22, 22), (78, 74), 6)
    return s


def panneau_klaxon():
    s = _surf(120, 200)
    poteau(s, 60, 110, 198)
    pygame.draw.rect(s, (20, 40, 90), (10, 8, 100, 96), border_radius=6)
    pygame.draw.rect(s, C.BLANC, (14, 12, 92, 88), border_radius=4)
    _centre_texte(s, _police(11), "KLAXON", (20, 20, 20), 36)
    _centre_texte(s, _police(11), "INTERDIT", C.ROUGE, 58)
    return s


def pieton_marche():
    s = _surf(50, 110)
    pygame.draw.circle(s, (62, 38, 22), (25, 18), 10)
    pygame.draw.rect(s, (40, 90, 70), (16, 28, 18, 36), border_radius=4)
    pygame.draw.line(s, (62, 38, 22), (20, 64), (12, 100), 4)
    pygame.draw.line(s, (62, 38, 22), (30, 64), (38, 100), 4)
    pygame.draw.line(s, (62, 38, 22), (16, 36), (6, 56), 3)
    pygame.draw.line(s, (62, 38, 22), (34, 36), (44, 50), 3)
    return s


def moto_arriere():
    s = _surf(56, 80)
    pygame.draw.ellipse(s, (20, 20, 22), (14, 54, 28, 18))
    pygame.draw.polygon(s, (28, 28, 32), [(12, 56), (44, 56), (38, 34), (18, 34)])
    pygame.draw.rect(s, C.VERT, (18, 38, 20, 10))
    pygame.draw.circle(s, (58, 36, 20), (28, 26), 7)
    pygame.draw.ellipse(s, (16, 16, 18), (18, 16, 20, 12))
    pygame.draw.rect(s, C.ROUGE, (22, 48, 12, 5))
    return s


def moto_avant():
    s = _surf(56, 80)
    pygame.draw.ellipse(s, (20, 20, 22), (14, 54, 28, 18))
    pygame.draw.polygon(s, (28, 28, 32), [(14, 56), (42, 56), (36, 30), (20, 30)])
    pygame.draw.circle(s, (58, 36, 20), (28, 24), 7)
    pygame.draw.ellipse(s, C.JAUNE, (22, 42, 12, 8))
    pygame.draw.ellipse(s, (16, 16, 18), (18, 14, 20, 12))
    return s


def moto_trafic():
    return moto_arriere()


def police_arriere():
    s = _surf(96, 90)
    pygame.draw.rect(s, (30, 50, 120), (16, 28, 64, 40), border_radius=4)
    pygame.draw.rect(s, (24, 40, 90), (24, 10, 48, 22), border_radius=3)
    pygame.draw.circle(s, C.ROUGE, (34, 14), 6)
    pygame.draw.circle(s, (50, 90, 255), (62, 14), 6)
    pygame.draw.rect(s, C.ROUGE, (20, 50, 12, 7))
    pygame.draw.rect(s, C.ROUGE, (64, 50, 12, 7))
    pygame.draw.ellipse(s, (18, 18, 20), (18, 68, 24, 16))
    pygame.draw.ellipse(s, (18, 18, 20), (54, 68, 24, 16))
    _centre_texte(s, _police(8), "POLICE", C.BLANC, 46)
    return s


def police_pick():
    return police_arriere()


def nid_poule():
    s = _surf(90, 40)
    pygame.draw.ellipse(s, (28, 18, 10), (4, 8, 82, 26))
    pygame.draw.ellipse(s, (70, 50, 28), (18, 14, 50, 14))
    pygame.draw.ellipse(s, (40, 40, 38), (30, 16, 20, 8))
    return s


class Atlas:
    def __init__(self):
        self.stop = panneau_stop()
        self.ecole = panneau_ecole()
        self.interdit = panneau_interdit()
        self.casque = panneau_casque()
        self.feu = feu_tricolore(True)
        self.controle = controle_gendarmerie()
        self.taxi = taxi_arriere()
        self.taxi_avant = taxi_avant()
        self.taxi_cote = taxi_cote()
        self.camion_avant = camion_avant()
        self.moto_avant = moto_avant()
        self.call = call_box()
        self.palmier = palmier()
        self.mama = mama_bassin()
        self.ecoliers = ecoliers()
        self.chevre = chevre()
        self.camion = camion_fuso()
        self.trou = nid_poule()
        self.danger_bosse = panneau_danger("DOS D'ÂNE")
        self.pietons = panneau_danger("PIÉTONS")
        self.cede = panneau_cede()
        self.priorite = panneau_priorite()
        self.travaux = panneau_travaux()
        self.depassement = panneau_depassement()
        self.stationnement = panneau_stationnement()
        self.klaxon_interdit = panneau_klaxon()
        self.pieton = pieton_marche()
        self.moto_trafic = moto_trafic()
        self.police_pick = police_pick()
        self.panneaux_bord = {
            "stop": self.stop,
            "vitesse50": None,
            "ecole": self.ecole,
            "pietons": self.pietons,
            "cede": self.cede,
            "travaux": self.travaux,
            "interdit": self.interdit,
            "casque": self.casque,
            "priorite": self.priorite,
            "klaxon": self.klaxon_interdit,
            "stationnement": self.stationnement,
            "depassement": self.depassement,
        }
        self.vitesses = {n: panneau_vitesse(n) for n in (30, 40, 50, 60, 70, 80)}
        self.boutiques: dict[str, pygame.Surface] = {}
        self.villes: dict[str, pygame.Surface] = {}
        self.directions: dict[str, pygame.Surface] = {}

    def panneau_bord(self, cle: str) -> pygame.Surface:
        if cle == "vitesse50":
            return self.vitesse(50)
        return self.panneaux_bord.get(cle) or self.stop

    def vitesse(self, lim: int) -> pygame.Surface:
        cle = min(self.vitesses, key=lambda n: abs(n - lim))
        return self.vitesses[cle]

    def enseigne(self, nom: str) -> pygame.Surface:
        if nom not in self.boutiques:
            murs = [
                (186, 140, 78),
                (160, 90, 70),
                (90, 120, 90),
                (70, 90, 130),
                (170, 150, 90),
            ]
            self.boutiques[nom] = boutique(nom, murs[len(self.boutiques) % 5])
        return self.boutiques[nom]

    def ville(self, nom: str) -> pygame.Surface:
        if nom not in self.villes:
            self.villes[nom] = panneau_ville(nom)
        return self.villes[nom]

    def direction(self, label: str) -> pygame.Surface:
        if label not in self.directions:
            a, _, b = label.partition("|")
            self.directions[label] = panneau_direction(a, b)
        return self.directions[label]
