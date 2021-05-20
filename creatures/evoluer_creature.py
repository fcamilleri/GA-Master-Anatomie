#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module qui permet l'évolution d'une créature. Implémente des opérateurs génétiques comme la mutation et les croisements
"""

from .creature import Creature
from .physique import Articulation, Segment
from random import choice, uniform, randint
from .noms import nomFrancais, pseudoNomLatin
from math import sqrt, pi
from .vecteur import Vecteur
from copy import copy

# Permet de connaître la génération d'une lignée
_lignee_compte = 0

# Séparateur entre les identifiants et la lignée
SEPARATEUR = ':'

class Evoluercreature(Creature):
    # Initialisation
    def __init__(self, parent=None, name="Unnamed", angleDepart=0, random=False):

        global _lignee_compte

        if random:
            super(Evoluercreature, self).__init__(parent=creature_aleatoire())
        else:
            super(Evoluercreature, self).__init__(parent, name, angleDepart)

        if not parent:
            self['adaptation'] = 0
            self['lignee'] = hex(_lignee_compte)[2:] + SEPARATEUR

        self._lignee_compte = 0
        _lignee_compte += 1

    def generations(self):
        # Retourne le nombre de générations
        return len(self['lignee'].split(SEPARATEUR)) - 1

    def nouvelleLignee(self, parent):
        # Ajoute une nouvelle lignée
        self['lignee'] += hex(parent._lignee_compte)[2:] + SEPARATEUR
        parent._lignee_compte += 1

    def crossover(self, autre):
        # Croise deux créatures
        global _lignee_compte

        # Créer nouvelle créature
        croisement = Evoluercreature()

        #  Croiser les infos
        for key in self:
            croisement[key] = self[key]

        croisement['adaptation'] = 0
        croisement['name'] = ' '.join(set(self['name'].split() + autre['name'].split()))
        croisement['adapted'] = "random"

        # Sélectionner la lignée
        try:
            croisement['lignee'] += 'X' + \
                autre['lignee'].split(SEPARATEUR)[0] + '...' + autre['lignee'].split(SEPARATEUR)[-2] + \
                SEPARATEUR
        except KeyError:
            pass

        # Pour chaque segment on moyenne
        for segmentA, segmentB in zip(self.segments + ([None] * ((len(autre.segments)-len(self.segments))//2)),
                                    autre.segments + ([None] * ((len(self.segments)-len(autre.segments))//2))):

            if segmentA is None: segmentA = segmentB
            elif segmentB is None: segmentB = segmentA

            # Selectionner segment
            segment = choice([segmentA,segmentB])

            # Selectionner articulation A
            articulationA = croisement.getArticulation(segment.a.id)
            if articulationA is None:
                articulationA = choice([self,autre]).getArticulation(segment.a.id)
                if articulationA is None: articulationA = segment.a

                # Créer articulation A
                new_articulationA = Articulation(articulationA.pos, articulationA.vel, articulationA.acc)
                new_articulationA.id = articulationA.id
                articulationA = new_articulationA

                # Ajouter articulation A
                croisement.add(articulationA)

            # Sélectionner articulation B
            articulationB = croisement.getArticulation(segment.b.id)
            if articulationB is None:
                articulationB = choice([self,autre]).getArticulation(segment.b.id)
                if articulationB is None: articulationB = segment.b

                # Créer articulation B
                new_articulationB = Articulation(articulationB.pos, articulationB.vel, articulationB.acc)
                new_articulationB.id = articulationB.id
                articulationB = new_articulationB

                # Ajoutter articulation B
                croisement.add(articulationB)

            # Ajouter segment créé
            croisement.add(Segment(articulationA, articulationB, segment.amplitude,
                             segment.decalage, segment.normal))

        # Retirer les éléments flottants
        croisement.retirerFlottantes()

        # Retourner le nouvel individu
        return croisement

    def mutate(self, newarticulationdist=100, articulationvariation=10):
        # Mute une structure de la créature, ce qui peut correspondre à: rajouter ou retirer un segment ou une articulation, modifier un segment ou modifier la position d'un noeud.
       
        if len(self.articulations) == 0:
            return

        mut = choice(list(range(6)))

        if mut == 0: # Ajouter une articulation
            neigh = choice(self.articulations)
            newarticulation = Articulation(pos=(neigh.pos.x + uniform(-newarticulationdist, newarticulationdist),
                            neigh.pos.y + uniform(-newarticulationdist, newarticulationdist)))
            self.add(newarticulation)       # Nouvelle articulation
            self.add(Segment(neigh, newarticulation, decalage=uniform(0,pi*2))) # Nouveau segment
            
        elif mut == 1 and len(self.articulations) > 1: # Retirer une articulation
            # Créer une copie de la créature
            copie = Creature()
            copie.articulations = copy(self.articulations)
            copie.segments = copy(self.segments)
            # sélectionner une articulation à retirer
            toremove = choice(copie.articulations)
            # Essayer de retirer l'articulation
            copie.remove(toremove)
            if not copie.flottantes():
                # Réussite, on continue
                for articulation in self.articulations:
                    if articulation.id == toremove.id:
                        self.remove(articulation)
                        break

        elif mut == 2 and len(self.articulations) > 1: # Rajouter un segment
            a = choice(self.articulations)
            b = choice(self.articulations)
            # Choisir le segment
            while a is b:
                b = choice(self.articulations)
            self.add(Segment(a, b, decalage=uniform(0,pi*2)))   # Ajouter le segment
            
        elif mut == 3 and len(self.segments) > 0: # Retirer un segment
            # Selectionner segment
            toremove = choice(self.segments)
            # Retirer le segment
            self.remove(toremove)
            if self.flottantes():
                # verifier que le segment lie bien deux articulations qui existent.
                self.add(toremove)

        elif mut == 4 and len(self.segments) > 0: # Modifier les propriétés d'un segment
            segment = choice(self.segments)
            if choice([1, 2]) == 1:
                segment.decalage = max(segment.decalage + uniform(-pi, pi), 0)
            else:
                added = uniform(-0.5, 0.5)
                segment.amplitude = segment.amplitude + added if abs(segment.amplitude + added) <= 0.5 else segment.amplitude

        elif mut == 5: # Modifier la position d'un noeud
            articulation = choice(self.articulations)
            articulation.pos.x += uniform(-articulationvariation,articulationvariation)
            articulation.pos.y += uniform(-articulationvariation,articulationvariation)

            # Corriger les segments
            for segment in self.segments:
                if segment.a is articulation or segment.b is articulation:
                    segment.normal = sqrt(sum((segment.a.pos-segment.b.pos)**2))

        # Retourne la créature elle-même
        return self
                                                                         #
def creature_aleatoire(articulations_num=10, segments_num=30, rayon_articulation=100):
    # Crée une créature totalement nouvelle
    creature = Evoluercreature(name=nomFrancais(1))
    creature["adapted"] = "random"

    for x in range(randint(articulations_num//2, articulations_num)):
        # Ajout d'une articulation
        newarticulation = Articulation(pos=(uniform(-rayon_articulation, rayon_articulation),
                uniform(-rayon_articulation, rayon_articulation)))
        creature.add(newarticulation) 

    if len(creature.articulations) > 1:
        for x in range(randint(segments_num//2, segments_num)):
            # ajout d'un segment aléatoire
            a = choice(creature.articulations)
            b = choice(creature.articulations)
            while a is b:
                b = choice(creature.articulations)
            creature.add(Segment(a, b, decalage=uniform(0,pi*2), amplitude=uniform(-0.5, 0.5)))

    creature.retirerFlottantes()

    return creature