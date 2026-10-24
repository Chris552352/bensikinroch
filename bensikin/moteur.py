"""Journée de Roch : courses, éléments de route, primes et coupes."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from .constantes import CAISSE_DEPART, ELEMENTS


@dataclass
class Flash:
    texte: str
    montant: int
    age: float = 0.0
    duree: float = 2.4
    ok: bool = True


@dataclass
class Obstacle:
    modele: dict
    z: float
    voie: float
    resolu: bool = False
    rate: bool = False
    actif: bool = False


@dataclass
class Decor:
    kind: str
    z: float
    cote: float
    label: str = ""


@dataclass
class Mobile:
    kind: str
    z: float
    voie: float
    face: int = 1
    vx: float = 0.0
    touche: bool = False


@dataclass
class Journal:
    lignes: list = field(default_factory=list)
    primes: int = 0
    coupes: int = 0
    fautes: int = 0
    respects: int = 0
    courses: int = 0
    recette_courses: int = 0
    honneur: int = 0

    def ajouter(self, texte: str, montant: int, ok: bool) -> None:
        self.lignes.append({"texte": texte, "montant": montant, "ok": ok})
        if ok:
            self.primes += montant
            self.respects += 1
            self.honneur += 12
        else:
            self.coupes += -montant if montant < 0 else montant
            self.fautes += 1
            self.honneur -= 18


class Journee:
    def __init__(self, niveau: dict, profil: dict):
        self.niveau = niveau
        self.rng = random.Random()
        self.temps = 0.0
        self.duree = float(niveau["duree"])
        self.vitesse = 18.0
        self.vitesse_max = float(niveau["vitesse_max"])
        self.joueur_x = 0.0
        self.inclinaison = 0.0
        self.distance = 0.0
        self.caisse_jour = 0
        self.phare = niveau.get("moment") == "nuit" or niveau.get("meteo") == "pluie"
        self.casque_passager = True
        self.client_a_bord = True
        self.flashs: list[Flash] = []
        self.journal = Journal()
        self.obstacles: list[Obstacle] = []
        self.decors: list[Decor] = []
        self.mobiles: list[Mobile] = []
        self.termine = False
        self.game_over_vitesse = False
        self.telephone_piege = False
        self.ambiance_idx = 0
        self.prochain_client = 16.0
        self.feux_grilles = 0
        self.poursuite = False
        self.police_z = 1.1
        self.poursuite_t = 0.0
        self.hors_route_cd = 0.0
        self._peupler()
        self.annoncer(
            f"Départ {niveau['nom']}. Caisse globale : {int(profil.get('caisse_globale', CAISSE_DEPART))} FCFA.",
            0,
            True,
        )

    def _catalogue(self) -> list[dict]:
        ids = [
            "dos_dane",
            "pietons",
            "nid",
            "casque",
            "ecole",
            "stop",
            "limitation",
            "rond_point",
            "chevre",
            "controle",
            "feu_rouge",
            "telephone",
            "klaxon",
            "sens_unique",
        ]
        if self.niveau.get("moment") in ("nuit", "crepuscule") or self.niveau.get("meteo") == "pluie":
            ids.append("phare")
            self.phare = False
        diff = self.niveau["difficulte"]
        pool = []
        for e in ELEMENTS:
            if e["id"] not in ids:
                continue
            poids = 2
            if e["id"] in ("feu_rouge", "controle", "ecole", "stop") and diff >= 2:
                poids += 2
            if e["id"] in ("nid", "phare") and diff >= 4:
                poids += 2
            pool.extend([e] * poids)
        return pool

    def _peupler(self) -> None:
        pool = self._catalogue()
        n = 9 + self.niveau["difficulte"] * 3
        densite = float(self.niveau["densite"])
        z = 2.6
        for i in range(n):
            modele = dict(self.rng.choice(pool))
            if modele["id"] == "limitation":
                lim = max(35, int(self.vitesse_max * (0.38 + 0.08 * self.rng.random())))
                modele["vitesse_max"] = lim
                lieux = self.niveau.get("lieux") or ["Village"]
                modele["lieu"] = self.rng.choice(lieux)
                modele["consigne"] = f"{modele['lieu']} : {lim} km/h. Ralentis (BAS)."
            voie = self.rng.choice([-1, 0, 1]) if modele["id"] in ("nid", "sens_unique") else 0
            if modele["id"] == "nid":
                voie = self.rng.choice([-1, 1])
            z += (1.15 + self.rng.random() * 0.7) / densite
            self.obstacles.append(Obstacle(modele, z, float(voie)))
        self._peupler_decors()
        self._peupler_trafic()

    def _peupler_decors(self) -> None:
        boutiques = list(self.niveau.get("boutiques") or ["Boutique"])
        lieux = list(self.niveau.get("lieux") or ["Cameroun"])
        z = 0.35
        kinds = ["boutique", "palmier", "taxi", "call", "ville", "drapeau", "palmier", "boutique"]
        for i in range(18):
            kind = kinds[i % len(kinds)]
            cote = -1.0 if i % 2 == 0 else 1.0
            label = ""
            if kind == "boutique":
                label = boutiques[i % len(boutiques)]
            elif kind == "ville":
                label = lieux[i % len(lieux)]
            elif kind == "direction" or i % 11 == 0:
                kind = "direction"
                cote = 1.0
                label = f"{lieux[i % len(lieux)]}|{lieux[(i + 1) % len(lieux)]}"
            else:
                cote = 1.0 if i % 3 else -1.0
            z += 0.22 + self.rng.random() * 0.18
            self.decors.append(Decor(kind, z, cote, label))
        panneaux = [
            "stop", "vitesse50", "ecole", "pietons", "cede", "travaux",
            "interdit", "casque", "priorite", "klaxon", "stationnement", "depassement",
        ]
        z = 0.7
        for i, p in enumerate(panneaux):
            z += 0.55 + self.rng.random() * 0.15
            self.decors.append(Decor("panneau", z, 1.0, p))

    def _peupler_trafic(self) -> None:
        kinds = ["taxi", "moto", "fuso", "pieton", "taxi", "moto", "pieton"]
        z = 0.55
        for i in range(10):
            kind = kinds[i % len(kinds)]
            if kind == "pieton":
                face = 1
                voie = self.rng.choice([-0.92, 0.92])
            elif i % 3 == 0:
                face = -1
                voie = -0.42
            else:
                face = 1
                voie = 0.40
            z += 0.28 + self.rng.random() * 0.16
            self.mobiles.append(
                Mobile(kind, z, voie, face, self.rng.uniform(-0.25, 0.25) if kind == "pieton" else 0.0)
            )

    def annoncer(self, texte: str, montant: int, ok: bool) -> None:
        self.flashs.append(Flash(texte, montant, ok=ok))
        if len(self.flashs) > 4:
            self.flashs = self.flashs[-4:]

    def courant(self) -> Obstacle | None:
        proches = [o for o in self.obstacles if (not o.resolu) and 0.12 < o.z < 1.05]
        if not proches:
            return None
        return min(proches, key=lambda o: o.z)

    def _payer(self, obs: Obstacle, ok: bool, extra: str = "") -> None:
        if obs.resolu:
            return
        obs.resolu = True
        coef_p = float(self.niveau["prime"])
        coef_a = float(self.niveau["amende"])
        if ok:
            brut = int(obs.modele["prime"] * coef_p)
            msg = extra or obs.modele["ok"]
            self.caisse_jour += brut
            self.journal.ajouter(f"PRIME · {obs.modele['nom']}", brut, True)
            self.annoncer(f"+ {brut} FCFA — {msg}", brut, True)
        else:
            perte = -int(obs.modele["coupe"] * coef_a)
            msg = extra or obs.modele["ko"]
            self.caisse_jour += perte
            self.journal.ajouter(f"COUPE · {obs.modele['nom']}", perte, False)
            self.annoncer(f"{perte} FCFA — {msg}", perte, False)
            if obs.modele["id"] in ("ecole", "controle", "feu_rouge") and not ok:
                self.vitesse *= 0.45
            if obs.modele["id"] == "feu_rouge" and not ok:
                self.feux_grilles += 1
                amende = -2500 * self.feux_grilles
                self.caisse_jour += amende
                self.journal.ajouter("COUPE · feu grillé (récidive)", amende, False)
                if self.feux_grilles >= 2:
                    self._lancer_poursuite()
                else:
                    self.annoncer("Feu grillé. Encore un et la police te court après.", amende, False)

    def _lancer_poursuite(self) -> None:
        if not self.poursuite:
            self.poursuite = True
            self.police_z = 0.92
            self.poursuite_t = 0.0
            self.mobiles.append(Mobile("police", self.police_z, 0.25, 1, 0.0))
        extra = -4000 * (self.feux_grilles - 1)
        self.caisse_jour += extra
        self.journal.ajouter("COUPE · poursuite police", extra, False)
        self.annoncer(
            f"POURSUITE ! {self.feux_grilles} feux grillés. ESPACE pour te rendre, sinon fourrière.",
            extra,
            False,
        )

    def _juger(self, obs: Obstacle, touches: dict, frein: bool, stop: bool) -> None:
        action = obs.modele["action"]
        vmax = obs.modele.get("vitesse_max", 999)
        if action == "stop":
            if stop and self.vitesse <= vmax + 4:
                self._payer(obs, True)
            return
        if action == "ralentir":
            if self.vitesse <= vmax:
                self._payer(obs, True)
            return
        if action == "frein":
            if frein or self.vitesse <= vmax:
                self._payer(obs, True)
            return
        if action == "casque":
            if touches.get("casque"):
                self.casque_passager = True
                self._payer(obs, True)
            return
        if action == "phare":
            if self.phare or touches.get("phare"):
                self.phare = True
                self._payer(obs, True)
            return
        if action == "klaxon":
            if touches.get("klaxon"):
                self._payer(obs, True)
            return
        if action == "droite":
            if self.joueur_x > 90:
                self._payer(obs, True)
            return
        if action == "esquive":
            cote = obs.voie
            if cote > 0 and self.joueur_x < -70:
                self._payer(obs, True)
            elif cote < 0 and self.joueur_x > 70:
                self._payer(obs, True)
            return
        if action == "ignorer":
            if touches.get("telephone"):
                self._payer(obs, False, "Tu as décroché au guidon. Double peine.")
            return

    def _rater_si_besoin(self, obs: Obstacle, touches: dict) -> None:
        if obs.resolu or obs.z > 0.16:
            return
        action = obs.modele["action"]
        if action == "ignorer":
            if not touches.get("telephone"):
                self._payer(obs, True)
            return
        self._payer(obs, False)

    def _course_client(self) -> None:
        if self.temps < self.prochain_client:
            return
        self.prochain_client = self.temps + self.rng.uniform(14, 22)
        destinations = [
            ("Akwa", 1800),
            ("Bonanjo", 2200),
            ("Deïdo", 1500),
            ("Mvan", 2000),
            ("Etoudi", 2400),
            ("Makepe", 1700),
            ("Mokolo", 1900),
            ("Kribi plage", 3200),
            ("Marché Central", 1600),
            ("Aéroport Nsimalen", 3500),
        ]
        nom, base = self.rng.choice(destinations)
        malus = 400 * self.journal.fautes
        gain = max(400, int((base + self.rng.randint(-200, 400)) * self.niveau["prime"]) - malus)
        self.caisse_jour += gain
        self.journal.courses += 1
        self.journal.recette_courses += gain
        self.casque_passager = self.rng.random() > 0.35
        self.annoncer(
            f"Client descendu à {nom} · course {gain} FCFA"
            + ("" if self.casque_passager else " · le prochain n'a pas de casque !"),
            gain,
            True,
        )
        self.journal.ajouter(f"COURSE · {nom}", gain, True)

    def actualiser(self, dt: float, touches: dict) -> None:
        if self.termine:
            return
        self.temps += dt
        accel = 38 if touches.get("accel") else 0
        frein = touches.get("frein")
        stop = touches.get("stop")
        if stop:
            self.vitesse = max(0.0, self.vitesse - 95 * dt)
        elif frein:
            self.vitesse = max(0.0, self.vitesse - 55 * dt)
        else:
            self.vitesse = min(self.vitesse_max, self.vitesse + accel * dt)
            self.vitesse = max(8.0, self.vitesse - 6 * dt)

        # Virage : la route tire, tu dois contre-braquer.
        d = self.distance * 0.022
        force = float(self.niveau["courbure"])
        courb_now = (math.sin(d) * 1.2 + math.sin(d * 2.35) * 0.6) * force
        self.joueur_x += courb_now * (self.vitesse / 55.0) * 95 * dt
        if touches.get("gauche"):
            self.joueur_x = max(-240, self.joueur_x - 210 * dt)
            self.inclinaison = max(-1.0, self.inclinaison - 5 * dt)
        elif touches.get("droite"):
            self.joueur_x = min(240, self.joueur_x + 210 * dt)
            self.inclinaison = min(1.0, self.inclinaison + 5 * dt)
        else:
            self.inclinaison *= 0.88
        self.inclinaison = max(-1.0, min(1.0, self.inclinaison + courb_now * 0.35))
        self.hors_route_cd = max(0.0, self.hors_route_cd - dt)
        if abs(self.joueur_x) > 210 and self.hors_route_cd <= 0:
            perte = -1800
            self.caisse_jour += perte
            self.journal.ajouter("COUPE · sortie de virage / laterite", perte, False)
            self.annoncer("Virage grillé : tu mords la laterite. Jante + honneur.", perte, False)
            self.vitesse *= 0.55
            self.joueur_x = max(-180, min(180, self.joueur_x))
            self.hors_route_cd = 2.8

        if touches.get("phare"):
            self.phare = True
        if touches.get("casque"):
            self.casque_passager = True

        self.distance += self.vitesse * dt * 0.55
        avance = (self.vitesse / max(40.0, self.vitesse_max)) * dt * 0.72

        for obs in self.obstacles:
            obs.z -= avance
            if 0.18 < obs.z < 0.92:
                obs.actif = True
                self._juger(obs, touches, frein, stop)
            if obs.z <= 0.16 and not obs.resolu:
                self._rater_si_besoin(obs, touches)
        for decor in self.decors:
            decor.z -= avance
            if decor.z < -0.12:
                decor.z += 4.2 + self.rng.random() * 0.6

        self._trafic(dt, avance)
        self._poursuite_police(dt, stop)

        for f in self.flashs:
            f.age += dt
        self.flashs = [f for f in self.flashs if f.age < f.duree]

        self._course_client()
        if self.temps >= self.duree:
            self.termine = True

    def _trafic(self, dt: float, avance: float) -> None:
        for m in self.mobiles:
            if m.kind == "police" and self.poursuite:
                continue
            coef = 0.32 if m.face > 0 else 1.35
            if m.kind == "pieton":
                coef = 0.55
            m.z -= avance * coef
            if m.z < 0.06 or m.z > 2.4:
                m.z = 1.05 + self.rng.random() * 0.35
                if m.kind == "pieton":
                    m.voie = self.rng.choice([-0.92, 0.92])
                elif m.face < 0:
                    m.voie = -0.42
                else:
                    m.voie = 0.40
                m.touche = False
                continue
            if m.touche:
                continue
            if 0.14 < m.z < 0.32:
                px = self.joueur_x / 200.0
                if abs(m.voie - px) < 0.38:
                    m.touche = True
                    if m.kind == "pieton":
                        perte = -7000
                        msg = "Piéton sur la chaussée. Tu l'as frôlé. La caisse saigne."
                    else:
                        perte = -3500
                        msg = "Accrochage dans le trafic (taxi / moto / Fuso)."
                    self.caisse_jour += perte
                    self.journal.ajouter(f"COUPE · {m.kind}", perte, False)
                    self.annoncer(msg, perte, False)
                    self.vitesse *= 0.6

    def _poursuite_police(self, dt: float, stop: bool) -> None:
        if not self.poursuite:
            return
        self.poursuite_t += dt
        self.police_z = max(0.16, self.police_z - 0.085 * dt)
        for m in self.mobiles:
            if m.kind == "police":
                m.z = self.police_z
                m.voie = 0.2 + 0.08 * math.sin(self.temps * 6)
        drain = -int(120 * dt * (1 + self.feux_grilles))
        if drain != 0:
            self.caisse_jour += drain
        if stop and self.vitesse <= 10:
            amende = -5000 - 1500 * self.feux_grilles
            self.caisse_jour += amende
            self.journal.ajouter("COUPE · reddition police", amende, False)
            self.annoncer("Tu t'arrêtes. PV. Ils te laissent repartir — plus pauvre.", amende, False)
            self.poursuite = False
            self.vitesse = 0
            self.mobiles = [m for m in self.mobiles if m.kind != "police"]
            return
        if self.police_z <= 0.20 or self.poursuite_t > 16:
            amende = -14000 - 2000 * self.feux_grilles
            self.caisse_jour += amende
            self.journal.ajouter("COUPE · interception / fourrière", amende, False)
            self.annoncer("Intercepté. Moto au commissariat. La journée peut finir en négatif.", amende, False)
            self.poursuite = False
            self.vitesse = 0
            self.mobiles = [m for m in self.mobiles if m.kind != "police"]

    def bilan(self) -> dict:
        recette = int(self.caisse_jour)
        note = max(0, min(20, 11 + self.journal.respects * 1.2 - self.journal.fautes * 2.4))
        if recette >= 8000 and self.journal.fautes == 0:
            titre = "Bensikin d'honneur — légende du bitume"
        elif recette >= 3000 and self.journal.fautes <= 1:
            titre = "Motard propre — le quartier te salue"
        elif recette >= 0:
            titre = "Journée moyenne — tu manges, tu n'éblouis pas"
        elif recette > -8000:
            titre = "Caisse négative — tu dois au vulcanisateur"
        else:
            titre = "Saisie — la moto dort au commissariat"

        morale = [
            "Au Cameroun, le plus court chemin n'est pas le plus vivant.",
            "Le casque n'est pas un bijou. C'est un contrat avec ta famille.",
            "Un dos d'âne respecté, c'est un client qui revient demain.",
            "La pluie de Douala pardonne tout, sauf la vitesse.",
            "On peut finir la journée à -15 000. La route ne fait pas crédit d'honneur.",
        ]
        return {
            "niveau": self.niveau["nom"],
            "recette": recette,
            "primes": self.journal.primes,
            "coupes": self.journal.coupes,
            "courses": self.journal.courses,
            "recette_courses": self.journal.recette_courses,
            "fautes": self.journal.fautes,
            "respects": self.journal.respects,
            "honneur": self.journal.honneur,
            "note": round(note, 1),
            "titre": titre,
            "morale": self.rng.choice(morale),
            "lignes": self.journal.lignes[-12:],
            "temps": int(self.temps),
            "feux_grilles": self.feux_grilles,
        }
