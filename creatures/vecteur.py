"""
Ce module implémente la classe Vecteur. Permet de simplifier les opérations vectorielles comme le produit scalaire, l'addition, la projection et le calcul d'angle.

Une grande partie de ces fonctions est tirée d'un tutoriel sur le site Python.org.
"""

import math

def _est_numerique(obj):
    #trouver si la variable est numérique
    if isinstance(obj, (int, float)):
        return True
    else:
        return False

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
