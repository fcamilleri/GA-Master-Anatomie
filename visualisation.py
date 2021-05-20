#! /usr/bin/python

from creatures.physique import *
from creatures.creature import charger_xml
from creatures.evoluer_creature import creature_aleatoire
import sys, pygame, optparse, os
import random

LARGEUR, HAUTEUR = 1080,1080

# Si ce module est executé comme Main, lancer le thread principal

if __name__ == "__main__":

    # Lecture de la ligne de commande
    analyseur = optparse.OptionParser(description="Show all genomes from a Creature XML espece")
    analyseur.add_option("-f", "--fullscreen", dest="fullscreen", default=False,
            action="store_true", help="Show in fullscreen")
    analyseur.add_option("-t", "--time", dest="time", default=5000, metavar="TIME",
            help="Time(in cicles) simulating each creature")

    (options, args) = analyseur.parse_args()

    if len(args) == 0:
        readfile = sys.stdin
    else:
        readfile = args[0]

    options.time = int(options.time)
    
    # Charger la populaiton depuis le fichier
    espece = charger_xml(readfile)
   
    pygame.init()
    
    pygame.display.set_mode((LARGEUR,HAUTEUR),
            pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE if options.fullscreen else pygame.DOUBLEBUF)
    pygame.display.set_caption('Creatures viewer')
    pygame.mouse.set_visible(not options.fullscreen)
    screen = pygame.display.get_surface()

    try:
        running = True
        while running:

            for creature in espece:
                # Centrer la créature horizontalement et la faire toucher le sol
                extrainfo = "évolué pour la course"
                creature.centreSol(HAUTEUR)

                # Contrôler la cadence d'image
                clock = pygame.time.Clock()

                tictac = 0;
                while running and tictac < options.time:

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or \
                                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                            running = False
                            break
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                            tictac = options.time
                            break
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                            sleep(2000)
                    creature.dessiner(screen, tictac=tictac, suivi_x=True, extrainfo=extrainfo)
                    creature.maj()
                    col = creature.collisionMur(HAUTEUR, BAS)

                    pygame.display.flip()   # Afficher la fenêtre

                    tictac += 1
                    clock.tick(1000)        # Limiter la cadence d'image


                if not running:
                    break

    except KeyboardInterrupt:
        pass

    # Fermer pygame
    pygame.quit()
