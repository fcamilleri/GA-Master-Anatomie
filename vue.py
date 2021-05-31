#! /usr/bin/python

'''
Le rôle de ce module est de permettre de visualiser comment se déplacent nos créatures
'''
LARGEUR, HAUTEUR = 1080,1080

from etc.physique import *
from etc.creature import charger_xml
from etc.evoluer_creature import creature_aleatoire
import sys, pygame, optparse, os, random, time

if __name__ == "__main__":
    # Lecture de la ligne de commande
    analyseur = optparse.OptionParser(description="Montrer tous les génomes d'une espèce")
    analyseur.add_option("-f", "--fullscreen", dest="fullscreen", default=False,
            action="store_true", help="Montrer en plein écran")
    analyseur.add_option("-t", "--time", dest="time", default=5000, metavar="TIME",
            help="Temps de simulation de chaque créature")
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
    pygame.display.set_caption('Visualisateur de créatures')
    pygame.mouse.set_visible(not options.fullscreen)
    screen = pygame.display.get_surface()
    try:
        se_deplace = True
        while se_deplace:
            for creature in espece:
                # Centrer la créature horizontalement et la faire toucher le sol
                extrainfo = " "
                creature.centreSol(HAUTEUR)
                # Contrôler les cycles
                clock = pygame.time.Clock()
                tictac = 0;
                while se_deplace and tictac < options.time:
                    for event in pygame.event.get():
                        # on quitte sur on appuie sur Échap
                        if event.type == pygame.QUIT or \
                                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                            se_deplace = False
                            break
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                            tictac = options.time
                            break
                        # mise en pause si on appuie sur espace
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                            time.sleep(2000)
                    creature.dessiner(screen, tictac=tictac, suivi_x=True, extrainfo=extrainfo)
                    creature.maj()
                    col = creature.collisionMur(HAUTEUR, BAS)
                    pygame.display.flip()   # Afficher la fenêtre
                    tictac += 1
                    clock.tick(1000)        # Limiter la cadence d'image
                if not se_deplace:
                    break
    except KeyboardInterrupt:
        pass
    # Fermer pygame
    pygame.quit()
