"""
Ce module contient les parties essentielles des créatures, à savoir leurs articulations et leurs segments. Tous les comportements physiques et interactions sont
définis ici.
"""
from math import sqrt, pi, sin, log
from .vecteur import Vecteur
# Accélération de la pesanteur appliquée à tous les noeuds
PESANTEUR = (0,0.3)
# Vitesse de changement de phase: modifie la fréquence des mouvements
INCREMENT_ANGLE = 0.025
# Paramètre qui détermine la force de chaque segment
ELASTICITE = 0.6
# La prise en compte de la viscosité est déactivée actuellement
VISCOSITE = 0.05
# Masses des noeuds/articulations
POIDS_NOEUD = 1.26
# Rayon d'une articulation
RAYON = 8
MAX_NORMAL = 400.0
# Conditionne la vélocité perdue à chaque étape de la simulation (désactivé)
RESISTANCE_AIR = 0.01 # désactivé
# Code pour orientation:
HAUT      = 1
BAS    = 2
GAUCHE    = 3
DROITE   = 4
class Articulation(object):
    """
    Une articulation est une masse ponctuelle qui est soumise à la pesanteur et à la résistance de l'air. Elle est définie par une position, une vélocité et peut 
    être contrainte par des segments.
    """
    def __init__(self, pos=(0,0), vel=(0,0), acc=(0,0)):
        #Crée une articulation avec une position de départ, une vélocité et une accélération
        self.pos = Vecteur(pos[0], pos[1])
        self.vel = Vecteur(vel[0], vel[1])
        self.acc = Vecteur(acc[0], acc[1])

    def collisionMur(self, limite, cote, atr_normal=0.6, atr_surface=0.5, min_vel=0.99, rayon=RAYON):
        # provoque une collision avec un mur si possible
        global HAUT, BAS, GAUCHE, DROITE
        force_collision = 0
        if cote == GAUCHE and self.pos.x < limite + rayon:
            self.pos.x = limite + rayon
            self.vel.x = self.vel.x * - atr_normal if abs(self.vel.x * - atr_normal) > min_vel else 0.0
            self.vel.y *= atr_surface
            force_collision = abs(self.vel.x)
        elif cote == DROITE and self.pos.x > limite - rayon:
            self.pos.x = limite - rayon
            self.vel.x = self.vel.x * - atr_normal if abs(self.vel.x * - atr_normal) > min_vel else 0.0
            self.vel.y *= atr_surface
            force_collision = abs(self.vel.x)
        if cote == HAUT and self.pos.y < limite + rayon:
            self.pos.y = limite + rayon
            self.vel.x *= atr_surface
            self.vel.y = self.vel.y * - atr_normal if abs(self.vel.y * - atr_normal) > min_vel else 0.0
            force_collision = abs(self.vel.y)
        elif cote == BAS and self.pos.y > limite - rayon:
            self.pos.y = limite - rayon
            self.vel.x *= atr_surface
            self.vel.y = self.vel.y * - atr_normal if abs(self.vel.y * - atr_normal) > min_vel else 0.0
            force_collision = abs(self.vel.y)
        elif cote not in [HAUT, GAUCHE, DROITE, BAS]:
            raise ValueError("cote doit être HAUT, GAUCHE, DROITE ou BAS.")
        return force_collision        
    def maj(self, atr=RESISTANCE_AIR, grav=PESANTEUR, elast=ELASTICITE):
        # Met à jour l'articulation: modifie sa position sur la base de sa vélocité et sa vélocité sur la base de son accélération.
        self.pos = self.pos + self.vel
        self.vel = self.vel + (self.acc * elast)
        self.pos = self.pos + self.acc * (1.0 - elast)
        self.acc = Vecteur(0,0)
        self.vel = self.vel + Vecteur(grav[0], grav[1])
        self.vel = self.vel * (1.0 - atr)     
    def collision(self, autre, rayon=RAYON):
        # Calcule la collision entre deux articulations
        if (self is autre):
            return
        distance = (self.pos - autre.pos).length()
        if distance != 0 and distance <= rayon*2:
            contact = (self.pos - autre.pos)
            tr_a = self.vel.prjc(contact)
            tr_b = autre.vel.prjc(contact)
            r = (contact.unit() * rayon * 2) - contact
            self.pos += r / 2.0
            autre.pos -= r / 2.0
            self.vel += tr_b - tr_a
            autre.vel += tr_a - tr_b
    def __repr__(self):
        return "<Articulation pos=%dx%d, vel=%.2fx%.2f>" % (self.pos.x, self.pos.y, self.vel.x, self.vel.y)
class Segment(object):
    """
    Un segment est une poutre hybride qui connecte des articulations, et ne peut exister que s'il lie deux articulations. 
    Un segment est de taille normale il exerce une force sur les différentes articulations pour rétablir son état. (modèle passif: os)
    Il peut également modifier sa taille de manière cyclique selon une fonction sinusoïdale (modèle actif: muscle).
    """
    def __init__(self, a, b, amplitude=0, decalage=pi, normal=None):
        # Initialisation d'un segment qui connecte les articulations A et B, avec une amplitude, un décalage et une longueur normale
        self.b = b
        self.a = a
        self.normal = min(sqrt(sum((a.pos-b.pos)**2)) if normal is None else normal, MAX_NORMAL)
        self.decalage = decalage
        self.amplitude = amplitude   
    def maj(self, elast=0.5, ang=None, visc=0):
        # Met à jour un segment en appliquant les forces environnantes.
        ampl = 0 if ang is None else self.amplitude
        if ang is None:
            ang = 0
        diff = (self.a.pos + self.a.vel) - (self.b.pos + self.b.vel)
        # on calcule la distance
        dis = sqrt(sum(diff**2))
        N = self.normal + (sin(ang+self.decalage) * ampl * self.normal)
        # on met à jour l'accélération
        if dis != 0:
            self.a.acc += diff/dis * (N-dis) * (1.0-elast) * 0.5
            self.b.acc -= diff/dis * (N-dis) * (1.0-elast) * 0.5
    def __repr__(self):
        return "<Segment normal=%.2f, amplitude=%.2f>" % (self.normal, self.amplitude)
if __name__ == '__main__':
    import unittest
