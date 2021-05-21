#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fait évoluer les créatures de manière sérialisée: une créature après l'autre.
"""

from creatures.creature import sauvegarder_xml, charger_xml
from creatures.evoluer_creature import Evoluercreature
from creatures.noms import nomFrancais, pseudoNomLatin
import sys, optparse
from creatures import adaptation
from random import sample
from functools import cmp_to_key
import time

# taille de la fenêtre en pixels 
LARGEUR, HAUTEUR = 1080, 1080

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
    
def cmp(a, b):
    return (a > b) - (a < b)

def evolution_serialisee(espece, adaptation=adaptation.run, save_frequency=10000,
        limite=-1,verbose=False, gfx=False, log=None, discard_fraction=0.6, random_include=0,
        best=False, start_itration = 1, id='', timer=0,path="", index=0):

    if log:
        sys.stdout = open("./data/log/" + id + ".log", "w")

    """
    Execute l'algorithme génétique et sauvegarde les résultats toutes les n générations
    """

    itr = start_itration # Première itération

    removed = int(len(espece)/2 * discard_fraction)
    aleatoires = int(len(espece)/2 * random_include)
    
    espece = [Evoluercreature(creature) for creature in espece]

    try:

        while espece and itr != limite:

            somme_adaptation = 0
            if verbose:
                print("Iteration %d:" % (itr))
                z = 1
                lignee_len_sum = 0

            # Tester le niveau d'adaptation de la créature
            for specimen in espece:
                specimen['adaptation'] = adaptation(specimen, LARGEUR, HAUTEUR, gfx)

                somme_adaptation += specimen['adaptation']
                if verbose:
                    output = "\t%d/%d: \"%s\"(%d) %.3f" % (z, len(espece), specimen['name'],specimen.generations(), specimen['adaptation'])
                    print(output) 
                    z += 1
                    lignee_len_sum += specimen.generations()
            
            avg = somme_adaptation/float(len(espece))
            if verbose:
                print("Moyenne d'adaptation: %.4f" % (avg))

            # On classe les individus en fonction de leur niveau d'adaptation
            
            espece = sorted(espece,key=cmp_to_key(lambda A,B: cmp(A['adaptation'], B['adaptation'])), reverse=True)
            
            # On supprime les moins bons
            for specimen in sample(espece[len(espece)//2:], removed + aleatoires):
                espece.remove(specimen)

            # On clone et on mute ceux qui restent
            for specimen in sample(espece, removed):
                enfant = Evoluercreature(specimen).mutation()
                enfant.nouvelleLignee(specimen)

                names = enfant['name'].split()

                # on donne un nom aux enfants
                if len(names) == 1:
                    enfant['name'] = names[0] + " " + nomFrancais(0)
                elif len(names) >= 2:
                    enfant['name'] =  names[0] + " " +  nomFrancais(0) + " (" + pseudoNomLatin(2) +")"

                # on incorpore les enfants dans la population
                espece.append(enfant)

            # On rajoute les individus créés aléatoirement de novo
            espece += [Evoluercreature(random=True) for x in range(aleatoires)]
            
            if itr % save_frequency == 0:
                # On sauvegarde la population
                filename = "./data/%si%dB.xml" % (id, itr)
                sauvegarder_xml(espece, filename)

                if verbose:
                    print("# itration %d saved into %s" % (itr, filename))

            # On sauvegarde le meilleur individu si spécifié
            if best:
                filename = "./data/"+path+"%s-best.xml" % (id)
                sauvegarder_xml(espece[:1], filename)

            itr += 1
            
            # En cas de timeout (pour l'usine à créatures)
            if timer != 0:
                if time.thread_time() > timer:
                    if verbose:
                        print("\n# Timeout at %d seconds" % (time.thread_time()))
                    break

    except KeyboardInterrupt:
        pass

    espece.sort(key=cmp_to_key(lambda A,B: cmp(A['adaptation'], B['adaptation'])), reverse=True)

    filename = "./data/"+path+"%s.xml" % (id)
    sauvegarder_xml(espece, filename)
    if verbose:
        print()
        print("# iteration %d sauvée sous %s" % (itr, filename))
        print("# FIN...")
    return (espece[0]['adaptation'], index)


if __name__ == "__main__":

    # Lecture des paramètres de la ligne de commande
    analyseur = optparse.OptionParser(description="Starts a creatures evolution experiment.")

    if HAS_PYGAME:
        analyseur.add_option("-g", "--gfx", dest="gfx", default=False,
                help="Activer les graphismes", action="store_true")
        analyseur.add_option("-F", "--fullscreen", dest="fullscreen", default=False,
                action="store_true", help="Plein écran")
    analyseur.add_option("-L", "--log", dest="log", default=None,
            help="Logger toutes les données pour du debugging", action="store_true")
    analyseur.add_option("-v", "--verbose", dest="verbose", default=False,
            help="Sortie bavarde", action="store_true")
    analyseur.add_option("-b", "--best", dest="best", default=False,
            help="Sauver le meilleur individu", action="store_true")
    analyseur.add_option("-s", "--save-freq", dest="save_frequency", default=200,
            help="Fréquence de sauvegarde", metavar="NUMBER")
    analyseur.add_option("-l", "--limite", dest="limite", default=-1,
            help="Limite d'itérations", metavar="ITERATIONS")
    analyseur.add_option("-t", "--timer", dest="timer", default=0,
            help="Limite de temps, utile pour l'arbitrage de l'usine à créatures", metavar="TIME")
    analyseur.add_option("-a", "--start-at", dest="start_at", default=1,
            help="itération de départ", metavar="ITERATION")
    analyseur.add_option("-i", "--id", dest="id", default=None,
            help="Donner un identifiant à l'espèce", metavar="IDENTIFIER")
    (options, args) = analyseur.parse_args()


    if not HAS_PYGAME:
        options.gfx = False

    # Charger la fonction d'adaptation
    adaptation = adaptation.__dict__["run"]

    options.save_frequency = int(options.save_frequency)
    options.limite = int(options.limite)
    options.start_at = int(options.start_at)

    options.id = options.id if options.id is not None else pseudoNomLatin(4).lower()
    if options.verbose: print("# %s experiment." % options.id)

    if len(args) == 0:
        readfile = sys.stdin
    else:
        readfile = args[0]

    # lire l'espèce initiale
    init_espece = charger_xml(readfile)

    # Si les graphismes sont activés, activer Pygame
    if options.gfx:
        pygame.init()
        pygame.display.set_mode((LARGEUR,HAUTEUR),
        pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE if options.fullscreen else pygame.DOUBLEBUF)
        pygame.display.set_caption("Evolving creature for %s" % (options.adaptation))
        pygame.mouse.set_visible(not options.fullscreen)

    # Débuter la simulation
    evolution_serialisee(init_espece, adaptation, save_frequency=options.save_frequency,
            limite=options.limite,
            verbose=options.verbose, gfx=options.gfx,
            best=options.best, start_itration=options.start_at, id=options.id, timer=int(options.timer), log = options.log)

    if options.gfx:
        pygame.quit()
