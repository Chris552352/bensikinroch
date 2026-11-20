"""Rendu 3D : laterite, chaussée, panneaux, boutiques, moto Roch."""

from __future__ import annotations

import math
import random

import pygame

from . import constantes as C
from .visuel import Atlas


def lerp(a, b, t):
    return a + (b - a) * max(0.0, min(1.0, t))


def fcfa(n: int) -> str:
    signe = "+" if n > 0 else ""
    return f"{signe}{n:,} FCFA".replace(",", " ")


def couleur_ciel(niveau: dict, t: float) -> tuple[int, int, int]:
    moment = niveau.get("moment", "jour")
    meteo = niveau.get("meteo", "soleil")
    if moment == "nuit":
        return C.CIEL_NUIT
    if meteo == "pluie":
        return C.CIEL_PLUIE
    if moment == "crepuscule":
        return (int(lerp(92, 232, 0.6)), int(lerp(90, 110, 0.4)), int(lerp(70, 90, 0.3)))
    return C.CIEL_DOUALA


def bande_drapeau(surf: pygame.Surface) -> None:
    h = 8
    w = C.LARGEUR // 3
    pygame.draw.rect(surf, C.VERT, (0, 0, w, h))
    pygame.draw.rect(surf, C.ROUGE, (w, 0, w, h))
    pygame.draw.rect(surf, C.JAUNE, (2 * w, 0, C.LARGEUR - 2 * w, h))
    pygame.draw.circle(surf, C.JAUNE, (w + w // 2, h // 2), 3)


def soleil_ou_lune(surf, niveau, t):
    moment = niveau.get("moment", "jour")
    if moment == "nuit":
        pygame.draw.circle(surf, (230, 230, 210), (1000, 70), 26)
        pygame.draw.circle(surf, C.CIEL_NUIT, (1012, 62), 20)
        return
    col = (255, 214, 70) if moment != "crepuscule" else (255, 140, 60)
    pygame.draw.circle(surf, col, (1000, 64), 32)


def courbe_route(distance, z, force):
    d = distance * 0.022 + (1.0 - min(1.0, max(0.0, z))) * 0.85
    return (math.sin(d) * 1.2 + math.sin(d * 2.35) * 0.6 + math.cos(d * 0.5) * 0.22) * force * 200


def geometrie(z_obs, joueur_x, courbure, distance):
    """z_obs 0 = sous la moto, 1 = horizon. Retourne y, centre, demi-largeur, échelle."""
    horizon = int(C.HAUTEUR * 0.36)
    zc = max(0.02, min(1.35, float(z_obs)))
    t_near = 1.0 - min(1.0, zc)
    y = horizon + int((C.HAUTEUR - horizon) * (t_near ** 1.28))
    s = 0.84 / (0.84 + (1 - t_near) * 2.2)
    half_w = 70 + 520 * s
    courb = courbe_route(distance, zc, courbure)
    cx = C.LARGEUR / 2 + courb * (1 - t_near) ** 2 - joueur_x * 0.55 * s
    scale = 0.18 + 1.25 * (t_near ** 1.32)
    return horizon, y, cx, half_w, scale


def echelle_z(z, mini=0.16, maxi=0.62):
    t_near = 1.0 - min(1.0, max(0.04, float(z)))
    return mini + (maxi - mini) * (t_near ** 1.2)


def blit_pied(surf, sprite, x, y, scale):
    scale = max(0.10, min(1.05, scale * 1.35))
    w = max(8, int(sprite.get_width() * scale))
    h = max(8, int(sprite.get_height() * scale))
    img = pygame.transform.smoothscale(sprite, (w, h))
    surf.blit(img, img.get_rect(midbottom=(int(x), int(y))))


def trapeze(z0, z1, joueur_x, courbure, distance, marge=0):
    _, y0, c0, w0, _ = geometrie(z0, joueur_x, courbure, distance)
    _, y1, c1, w1, _ = geometrie(z1, joueur_x, courbure, distance)
    return [
        (c0 - w0 + marge, y0),
        (c0 + w0 - marge, y0),
        (c1 + w1 - marge, y1),
        (c1 - w1 + marge, y1),
    ]


def route_pseudo3d(surf, joueur_x, distance, courbure, niveau, t):
    horizon = int(C.HAUTEUR * 0.36)
    ciel = couleur_ciel(niveau, t)
    surf.fill(ciel)
    for y in range(horizon + 8):
        lumiere = y / (horizon + 8)
        col = tuple(int(lerp(c * .72, min(255, c + 22), lumiere)) for c in ciel)
        pygame.draw.line(surf, col, (0, y), (C.LARGEUR, y))
    soleil_ou_lune(surf, niveau, t)

    meteo = niveau.get("meteo", "soleil")
    herbe1 = (28, 98, 46) if meteo != "pluie" else (16, 58, 36)
    herbe2 = (22, 78, 38) if meteo != "pluie" else (12, 46, 30)
    laterite = C.LATERITE if meteo != "pluie" else (110, 70, 42)
    laterite2 = (148, 70, 32) if meteo != "pluie" else (96, 60, 36)

    n = 26
    for i in range(n):
        z0 = 1 - i / n
        z1 = 1 - (i + 1) / n
        _, y0, c0, w0, s0 = geometrie(z0, joueur_x, courbure, distance)
        _, y1, c1, w1, s1 = geometrie(max(0.02, z1), joueur_x, courbure, distance)
        bande = (i + int(distance * 0.14)) % 2 == 0
        pygame.draw.polygon(surf, herbe1, [(0, y0), (C.LARGEUR, y0), (C.LARGEUR, y1), (0, y1)])
        bord = 55 + 90 * max(0.15, min(1.0, s0))
        pygame.draw.polygon(
            surf, laterite,
            [(c0 - w0, y0), (c0 - w0 - bord, y0), (c1 - w1 - bord, y1), (c1 - w1, y1)],
        )
        pygame.draw.polygon(
            surf, laterite2,
            [(c0 + w0, y0), (c0 + w0 + bord, y0), (c1 + w1 + bord, y1), (c1 + w1, y1)],
        )
        pygame.draw.polygon(
            surf, C.CANIVEAU,
            [(c0 - w0 - 8, y0), (c0 - w0, y0), (c1 - w1, y1), (c1 - w1 - 8, y1)],
        )
        pygame.draw.polygon(
            surf, C.ASPHALTE if bande else C.ASPHALTE_CLAIR,
            [(c0 - w0, y0), (c0 + w0, y0), (c1 + w1, y1), (c1 - w1, y1)],
        )
        if bande:
            lw0, lw1 = max(2, 7 * s0), max(2, 7 * s1)
            pygame.draw.polygon(
                surf, C.LIGNE,
                [(c0 - lw0, y0), (c0 + lw0, y0), (c1 + lw1, y1), (c1 - lw1, y1)],
            )
            # Bandes de rive
            pygame.draw.line(surf, C.JAUNE, (c0 - w0 + 4, y0), (c1 - w1 + 4, y1), max(1, int(3 * s0)))
            pygame.draw.line(surf, C.JAUNE, (c0 + w0 - 4, y0), (c1 + w1 - 4, y1), max(1, int(3 * s0)))

    if meteo == "pluie":
        rng = random.Random(int(t * 40))
        for _ in range(80):
            x = rng.randint(0, C.LARGEUR)
            y = rng.randint(0, C.HAUTEUR)
            pygame.draw.line(surf, (180, 200, 220), (x, y), (x - 2, y + 11), 1)

    bande_drapeau(surf)
    return horizon


def moto_roch(surf, x, y, inclinaison, phare, casque_passager, nuit):
    lean = inclinaison * 16
    corps = pygame.Surface((150, 170), pygame.SRCALPHA)
    pygame.draw.ellipse(corps, (18, 18, 20), (48, 128, 56, 34))
    pygame.draw.ellipse(corps, (110, 110, 118), (60, 136, 32, 18))
    pygame.draw.polygon(corps, (22, 22, 26), [(36, 122), (114, 122), (104, 82), (46, 82)])
    pygame.draw.polygon(corps, C.VERT, [(48, 96), (102, 96), (96, 70), (54, 70)])
    pygame.draw.rect(corps, C.ROUGE, (52, 78, 46, 7))
    pygame.draw.rect(corps, C.JAUNE, (64, 86, 22, 6))
    pygame.draw.rect(corps, C.JAUNE, (58, 118, 36, 12), border_radius=2)
    font = pygame.font.SysFont("arial", 9, bold=True)
    corps.blit(font.render("CM ROCH", True, (20, 20, 20)), (60, 119))
    pygame.draw.line(corps, (30, 30, 32), (28, 88), (122, 88), 4)
    pygame.draw.circle(corps, (50, 50, 54), (26, 88), 6)
    pygame.draw.circle(corps, (50, 50, 54), (124, 88), 6)
    pygame.draw.circle(corps, (58, 36, 20), (75, 48), 14)
    pygame.draw.rect(corps, (24, 24, 30), (58, 58, 34, 26), border_radius=6)
    pygame.draw.ellipse(corps, (16, 16, 18), (56, 32, 38, 24))
    pygame.draw.rect(corps, C.JAUNE, (68, 40, 14, 5))
    pygame.draw.circle(corps, (78, 48, 28), (75, 70), 11)
    pygame.draw.rect(corps, (50, 80, 140), (60, 76, 30, 20), border_radius=4)
    if casque_passager:
        pygame.draw.ellipse(corps, C.ROUGE, (58, 54, 34, 22))
        pygame.draw.rect(corps, C.JAUNE, (68, 62, 14, 4))
    else:
        pygame.draw.circle(corps, (30, 18, 12), (75, 58), 6)
    if phare:
        pygame.draw.ellipse(corps, (255, 240, 160), (64, 104, 22, 12))
        halo = pygame.Surface((220, 110), pygame.SRCALPHA)
        pygame.draw.ellipse(halo, (255, 230, 120, 60), (0, 0, 220, 110))
        surf.blit(halo, (x - 110, y + 36))
    elif nuit:
        pygame.draw.ellipse(corps, (80, 80, 70), (64, 104, 22, 12))
    corps = pygame.transform.smoothscale(corps, (195, 221))
    rot = pygame.transform.rotate(corps, -lean)
    surf.blit(rot, rot.get_rect(center=(int(x), int(y))))


def _marquage_stripes(surf, z, joueur_x, courbure, distance, cols):
    pts = trapeze(max(0.04, z - 0.03), z + 0.05, joueur_x, courbure, distance, 8)
    pygame.draw.polygon(surf, cols[0], pts)
    _, y, cx, w, sc = geometrie(z, joueur_x, courbure, distance)
    for k in range(-3, 4):
        x0 = cx + k * (w / 4)
        pygame.draw.line(surf, cols[1], (x0 - 10 * sc, y - 6), (x0 + 10 * sc, y + 8), max(2, int(6 * sc)))


def dessiner_obstacle(surf, atlas: Atlas, obs, joueur_x, courbure, distance):
    z = obs.z
    if z < 0.04 or z > 1.28:
        return
    _, y, cx, half_w, _sc = geometrie(z, joueur_x, courbure, distance)
    sc = echelle_z(z, 0.20, 0.55)
    kind = obs.modele.get("sprite", "bosse")
    epaule_d = cx + half_w + 30 + 18 * sc
    epaule_g = cx - half_w - 30 - 18 * sc
    voie_x = cx + obs.voie * (half_w * 0.40)

    if kind == "bosse":
        _marquage_stripes(surf, z, joueur_x, courbure, distance, (C.JAUNE, (20, 20, 22)))
        blit_pied(surf, atlas.danger_bosse, epaule_d, y, sc * 0.95)
    elif kind == "feu":
        pygame.draw.polygon(surf, C.BLANC, trapeze(z - 0.02, z + 0.02, joueur_x, courbure, distance, 12))
        blit_pied(surf, atlas.feu, epaule_d, y, sc * 1.05)
    elif kind == "stop":
        pygame.draw.polygon(surf, C.BLANC, trapeze(z - 0.015, z + 0.02, joueur_x, courbure, distance, 10))
        blit_pied(surf, atlas.stop, epaule_d, y, sc)
    elif kind == "ecole":
        pygame.draw.polygon(surf, (40, 90, 50), trapeze(z - 0.08, z + 0.08, joueur_x, courbure, distance, 4))
        blit_pied(surf, atlas.ecole, epaule_d, y, sc)
        blit_pied(surf, atlas.ecoliers, voie_x, y, sc * 0.85)
    elif kind == "marche":
        pygame.draw.polygon(surf, C.BLANC, trapeze(z - 0.04, z + 0.05, joueur_x, courbure, distance, 6))
        blit_pied(surf, atlas.pietons, epaule_d, y, sc)
        blit_pied(surf, atlas.mama, voie_x + 20 * sc, y, sc)
    elif kind == "police":
        blit_pied(surf, atlas.controle, cx + half_w * 0.15, y, sc * 1.1)
    elif kind == "casque":
        blit_pied(surf, atlas.casque, epaule_d, y, sc)
    elif kind == "trou":
        blit_pied(surf, atlas.trou, voie_x, y + 4, sc * 1.2)
    elif kind == "chevre":
        blit_pied(surf, atlas.chevre, voie_x, y, sc)
        blit_pied(surf, atlas.danger_bosse, epaule_g, y, sc * 0.7)
    elif kind == "vitesse":
        lim = int(obs.modele.get("vitesse_max", 50))
        blit_pied(surf, atlas.vitesse(lim), epaule_d, y, sc)
        lieux = obs.modele.get("lieu") or "VILLAGE"
        blit_pied(surf, atlas.ville(str(lieux)), epaule_g, y - 10, sc * 0.8)
    elif kind == "rond":
        pygame.draw.circle(surf, (30, 90, 40), (int(cx), int(y - 20 * sc)), max(8, int(36 * sc)))
        pygame.draw.circle(surf, C.JAUNE, (int(cx), int(y - 20 * sc)), max(8, int(36 * sc)), max(2, int(3 * sc)))
    elif kind == "phare":
        pygame.draw.circle(surf, (255, 230, 140), (int(epaule_d), int(y - 50 * sc)), max(4, int(10 * sc)))
    elif kind == "camion":
        blit_pied(surf, atlas.camion, cx + half_w * 0.25, y, sc * 1.15)
    elif kind == "interdit":
        blit_pied(surf, atlas.interdit, epaule_g, y, sc)
        pygame.draw.polygon(surf, C.ROUGE, trapeze(z - 0.02, z + 0.04, joueur_x, courbure, distance, 20))
    elif kind == "tel":
        pygame.draw.rect(surf, (20, 20, 28), (int(cx - 10 * sc), int(y - 40 * sc), int(20 * sc), int(32 * sc)), border_radius=3)
    else:
        blit_pied(surf, atlas.stop, epaule_d, y, sc)


def dessiner_decor(surf, atlas: Atlas, decor, joueur_x, courbure, distance):
    z = decor.z
    if z < 0.12 or z > 1.15:
        return
    _, y, cx, half_w, _sc = geometrie(z, joueur_x, courbure, distance)
    sc = echelle_z(z, 0.18, 0.58)
    cote = 1.0 if decor.cote >= 0 else -1.0
    x = cx + cote * (half_w + 58)
    kind = decor.kind
    if kind == "boutique":
        blit_pied(surf, atlas.enseigne(decor.label), x, y, echelle_z(z, 0.22, 0.70))
    elif kind == "palmier":
        blit_pied(surf, atlas.palmier, x, y, echelle_z(z, 0.20, 0.64))
    elif kind == "taxi":
        blit_pied(surf, atlas.taxi_cote, x, y, echelle_z(z, 0.20, 0.55))
    elif kind == "call":
        blit_pied(surf, atlas.call, x, y, sc)
    elif kind == "ville":
        blit_pied(surf, atlas.ville(decor.label), x, y, echelle_z(z, 0.18, 0.48))
    elif kind == "direction":
        blit_pied(surf, atlas.direction(decor.label), x, y, echelle_z(z, 0.22, 0.50))
    elif kind == "drapeau":
        pygame.draw.line(surf, (80, 80, 80), (x, y), (x, y - 48 * sc), max(2, int(3 * sc)))
        pygame.draw.rect(surf, C.VERT, (x, y - 48 * sc, 10 * sc, 20 * sc))
        pygame.draw.rect(surf, C.ROUGE, (x + 10 * sc, y - 48 * sc, 10 * sc, 20 * sc))
        pygame.draw.rect(surf, C.JAUNE, (x + 20 * sc, y - 48 * sc, 10 * sc, 20 * sc))
    elif kind == "panneau":
        blit_pied(surf, atlas.panneau_bord(decor.label), x, y, echelle_z(z, 0.20, 0.52))


def dessiner_mobile(surf, atlas: Atlas, mobile, joueur_x, courbure, distance, t=0.0):
    z = mobile.z
    if z < 0.16 or z > 1.12:
        return
    _, y, cx, half_w, _sc = geometrie(z, joueur_x, courbure, distance)
    sc = echelle_z(z, 0.22, 0.62)
    face_avant = mobile.face < 0
    if mobile.kind == "pieton":
        x = cx + (1.0 if mobile.voie >= 0 else -1.0) * (half_w - 14)
        spr = atlas.pieton
        sc *= 0.78
    else:
        x = cx + mobile.voie * (half_w * 0.48)
        if mobile.kind == "taxi":
            spr = atlas.taxi_avant if face_avant else atlas.taxi
        elif mobile.kind == "moto":
            spr = atlas.moto_avant if face_avant else atlas.moto_trafic
            sc *= 0.78
        elif mobile.kind == "fuso":
            spr = atlas.camion_avant if face_avant else atlas.camion
            sc *= 1.08
        elif mobile.kind == "police":
            spr = atlas.police_pick
            if int(t * 8) % 2 == 0:
                pygame.draw.circle(surf, C.ROUGE, (int(x - 10), int(y - 42 * sc)), max(3, int(5 * sc)))
            else:
                pygame.draw.circle(surf, (40, 90, 255), (int(x + 10), int(y - 42 * sc)), max(3, int(5 * sc)))
        else:
            spr = atlas.taxi
    blit_pied(surf, spr, x, y, sc)


def carte(surf, titre, x, y, w, h, accent=C.JAUNE, fonts=None):
    panneau(surf, (x, y, w, h), accent)
    font = fonts["titre"] if fonts else pygame.font.SysFont("dejavusans", 19, bold=True)
    surf.blit(font.render(titre, True, accent), (x + 20, y + 14))


def panneau(surf, rect, accent=(66, 105, 88), actif=False):
    r = pygame.Rect(rect)
    pygame.draw.rect(surf, (4, 10, 9), r.move(0, 6), border_radius=16)
    pygame.draw.rect(surf, (24, 53, 43) if actif else (13, 31, 27), r, border_radius=16)
    pygame.draw.rect(surf, accent, r, 2 if actif else 1, border_radius=16)
    pygame.draw.rect(surf, accent, (r.x + 1, r.y + 17, 4, r.h - 34), border_radius=2)


def texte_bloc(surf, font, msg, rect, col=C.CREME):
    r = pygame.Rect(rect)
    mots = str(msg).split()
    ligne = ""
    y = r.y
    for mot in mots + [None]:
        candidat = f"{ligne} {mot}".strip() if mot else ""
        if ligne and (mot is None or font.size(candidat)[0] > r.w):
            if y + font.get_height() > r.bottom:
                break
            surf.blit(font.render(ligne, True, col), (r.x, y))
            y += font.get_linesize() + 2
            ligne = mot or ""
        else:
            ligne = candidat
    return y


def texte_ombre(surf, font, msg, pos, col=C.BLANC, ombre=C.NOIR):
    x, y = pos
    surf.blit(font.render(msg, True, ombre), (x + 2, y + 2))
    surf.blit(font.render(msg, True, col), (x, y))
