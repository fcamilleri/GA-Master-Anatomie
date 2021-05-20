"""
Teste l'aptitutde d'une créature à courir sur une distance importante en un temps donné.
"""

# On importe le moteur physique
from .vecteur import Vecteur
from math import sqrt
from . import physique

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

def run(creature, largeur, hauteur, enable_graphics=False, simulation_time=1000):
    # se base sur la vitesse à laquelle se déplace le centre de gravité de la créature pour mesurer sa performance
    creature['adapted'] = 'run'

    # Centrer la créature et la faire toucher le sol
    if len(creature['lignee'].split('.')) == 1:
        creature.centreSol(hauteur)

    # Sélectionner son centre de gravité
    start_x, start_y = creature.centreGravite()

    if enable_graphics and HAS_PYGAME:
        tictac = 0
        screen = pygame.display.get_surface()

    # Débuter la simulation
    for i in range(simulation_time):
        if enable_graphics and HAS_PYGAME:
            creature.dessiner(screen, tictac, suivi_x=True, extrainfo="evolue pour la course")
            pygame.display.flip()   # Affichage
            tictac += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                (event.type == pygame.KEYDOWN and event.key == 27):
                    raise KeyboardInterrupt

        creature.maj()
        creature.collisionMur(hauteur, physique.BAS)

    # Resélectionner son centre de masse
    end_x, end_y = creature.centreGravite()

    # Retourne la distance parcourue
    return abs(end_x - start_x)                                                           