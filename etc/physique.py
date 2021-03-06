"""
Ce module contient les parties essentielles des créatures, à savoir leurs articulations et leurs segments. Tous les comportements physiques et interactions sont
définis ici.
"""
import math
from math import sqrt, pi, sin, log

# Accélération de la pesanteur appliquée à tous les noeuds
PESANTEUR = (0,0.3)
# Vitesse de changement de phase: modifie la fréquence des mouvements. Un cycle correspond actuellement à 80 pi soit environ 251 itérations de la simulation.
INCREMENT_ANGLE = 0.025
# Masses des noeuds/articulations
POIDS_NOEUD = 1.24
# Rayon d'une articulation
RAYON = 8
# Longueur maximale d'un segment
NORME_MAX = 400.0
# Code pour orientation:
BAS = 2


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
        # provoque une collision avec un mur si possible, code redondant mais qui fait le job
        global HAUT, BAS, GAUCHE, DROITE
        force_collision = 0
        if cote == BAS and self.pos.y > limite - rayon:
            self.pos.y = limite - rayon
            self.vel.x *= atr_surface
            self.vel.y = self.vel.y * - atr_normal if abs(self.vel.y * - atr_normal) > min_vel else 0.0
            force_collision = abs(self.vel.y)
        elif cote not in [BAS]:
            raise ValueError("côté invalide")
        return force_collision        
    def maj(self, atr=0.01, grav=PESANTEUR, elast=0.6):
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

def _est_numerique(obj):
    #trouver si la variable est numérique
    if isinstance(obj, (int, float)):
        return True
    else:
        return False
        
        
        
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
        self.normal = min(sqrt(sum((a.pos-b.pos)**2)) if normal is None else normal, NORME_MAX)
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
            self.a.acc += diff/dis * (N-dis) * (1.0-elast) / 2
            self.b.acc -= diff/dis * (N-dis) * (1.0-elast) / 2
    def __repr__(self):
        return "<Segment normal=%.2f, amplitude=%.2f>" % (self.normal, self.amplitude)
if __name__ == '__main__':
    import unittest
"""
Ci-dessous se trouve la classe Vecteur, pour les opérations vectorielles concernant la position, vélocité et accélération.
Une partie de ces fonctions est inspirée d'internet.
"""


class Vecteur(object):
    def __init__(self, a=0, b=0 ):
        # permet de créer un nouveau vecteur
        if _est_numerique(a):
            # on part du principe que ce sont deux variables numériques
            self.x = a
            self.y = b
        else:
            # sinon ce sont sans doute des "tuples"
            self.x = b[0] - a[0]
            self.y = b[1] - a[1]
    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError
    def __add__(self, autre):
        return Vecteur(self.x + autre.x, self.y + autre.y)
    def __sub__(self, autre):
        return Vecteur(self.x - autre.x, self.y - autre.y) 
    def angle(self, vecteur=None):
        if vecteur == None:
            vecteur = Vecteur(1,0)
        return math.acos((self.dot(vecteur))/(self.length() * vecteur.length()))
    def angle_en_degres(self, vecteur=None):
        return (self.angle(vecteur) * 180) /math.pi
    def __mul__(self, autre):
        try:
            autre = autre - 0
        except:
            raise TypeError("Only scalar multiplication is supported.")
        return Vecteur( autre * self.x, autre * self.y )
    def __rmul__(self, autre):
        return self.__mul__(autre)
    def __div__(self, autre):
        return Vecteur( self.x // autre, self.y // autre )
    def cross(self, vecteur):
        return self.x * vecteur.y - self.y * vecteur.x
    def length(self):
        return math.sqrt( self.dot(self) )
    def perpendiculaire(self):
        return Vecteur(-self.y, self.x)
    def __neg__(self):
        return Vecteur(-self.x, -self.y)
    def unit(self):
        return self / self.length()
    def __abs__(self):
        return self.length()
    def __repr__(self):
        return '(%s, %s)' % (self.x, self.y)
    def __str__(self):
        return '(%s, %s)' % (self.x, self.y)
    def __pow__(self, y, z=None):
        return Vecteur(self.x.__pow__(y,z), self.y.__pow__(y,z))
    def __truediv__(self, autre):
        return Vecteur( self.x / autre, self.y / autre )
    def dot(self, vecteur):
        return self.x * vecteur.x + self.y * vecteur.y
    def projection(self, vecteur):
        return self.dot(vecteur.unit()) * vecteur.unit()
        