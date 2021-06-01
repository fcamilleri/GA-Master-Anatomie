"""
Teste l'aptitutde d'une créature à courir sur une distance importante en un temps donné.
"""

# On importe le moteur physique
from . import physique
from math import sqrt
import pygame

def course(creature, largeur, hauteur, activer_graphismes=False):
    # se base sur la vitesse à laquelle se déplace le centre de gravité de la créature pour mesurer sa performance
    temps_de_simulation=1000
    creature['adaptee'] = 'course'
    # Centrer la créature et la faire toucher le sol
    if len(creature['lignee'].split('.')) == 1:
        creature.centreSol(hauteur)
    # Sélectionner son centre de gravité
    depart_x, depart_y = creature.centreGravite()
    if activer_graphismes:
        tictac = 0
        ecran = pygame.display.get_surface()
    # Débuter la simulation
    for i in range(temps_de_simulation):
        # Boucle itérative de la simulation
        if activer_graphismes:
            creature.dessiner(ecran, tictac)
            pygame.display.flip()   # Affichage
            tictac += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                (event.type == pygame.KEYDOWN and event.key == 27):
                    # On quitte proprement
                    raise KeyboardInterrupt
        creature.maj() # On met à jour la créature
        creature.collisionMur(hauteur, physique.BAS)
    # Resélectionner son centre de masse
    arrivee_x, arrivee_y = creature.centreGravite()
    # Retourne la distance parcourue
    return abs(arrivee_x - depart_x)                                                           