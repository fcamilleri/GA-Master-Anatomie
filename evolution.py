
"""
Fait évoluer une population sur la base d'une population de départ, soit aléatoire soit issue d'une précédente évolution.
"""

# taille de la fenêtre en pixels 
LARGEUR, HAUTEUR = 1080, 1080
from etc.creature import sauvegarder_xml, charger_xml
from etc.evoluer_creature import Evoluercreature
from etc.noms import nomFrancais, pseudoNomLatin
import sys, optparse, time
from etc import adaptation
from random import sample
from functools import cmp_to_key

try:
    import pygame
except: 
    """
    Execute l'algorithme génétique et sauvegarde les résultats toutes les n générations
    """
def evolution_serialisee(espece, adaptation=adaptation.course, save_frequency=10000,
        limite=-1,verbose=False, graphismes=False, 
        meilleur=False, start_itration = 1, id='', timer=0,path="", index=0):
    itr = start_itration # Première itération
    pression_selection=0.6 # En réalité il s'agit de 1 - la pression de sélection
    retirees = int(len(espece)/2 * pression_selection)
    aleatoires = 0
    espece = [Evoluercreature(creature) for creature in espece]
    try:
        while espece and itr != limite:
            somme_adaptation = 0
            if verbose:
                print("Iteration %d:" % (itr))
                z = 1
                somme_lignee = 0
            # Tester le niveau d'adaptation de la créature
            for specimen in espece:
                specimen['adaptation'] = adaptation(specimen, LARGEUR, HAUTEUR, graphismes)
                somme_adaptation += specimen['adaptation']
                if verbose:
                    sortie_console = "\t%d/%d: \"%s\"(%d) %.3f" % (z, len(espece), specimen['name'],specimen.generations(), specimen['adaptation'])
                    print(sortie_console) 
                    z += 1
                    somme_lignee += specimen.generations()
            avg = somme_adaptation/float(len(espece))
            if verbose:
                print("Moyenne d'adaptation: %.4f" % (avg))
            # On classe les individus en fonction de leur niveau d'adaptation
            espece = sorted(espece,key=cmp_to_key(lambda A,B: cmp(A['adaptation'], B['adaptation'])), reverse=True)
            # On supprime les moins bons
            for specimen in sample(espece[len(espece)//2:], retirees + aleatoires):
                espece.remove(specimen)
            # On clone et on mute ceux qui restent
            for specimen in sample(espece, retirees):
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
                    print("# itération %d sauvegardée dans %s" % (itr, filename))
            # On sauvegarde le meilleur individu si spécifié
            if meilleur:
                filename = "./data/"+path+"%s-meilleur.xml" % (id)
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
# fonction toute simple pour comparer    
def cmp(a, b):
    return (a > b) - (a < b)

if __name__ == "__main__":
    # Lecture des paramètres de la ligne de commande
    analyseur = optparse.OptionParser(description="Débute un processus évolutif.")
    analyseur.add_option("-v", "--verbose", dest="verbose", default=False,
            help="Sortie bavarde", action="store_true")
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
    # Charger la fonction d'adaptation
    adaptation = adaptation.__dict__["course"]
    options.save_frequency = int(options.save_frequency)
    options.limite = int(options.limite)
    options.start_at = int(options.start_at)
    options.id = options.id if options.id is not None else pseudoNomLatin(4).lower()
    if len(args) == 0:
        lecture_fichier = sys.stdin
    else:
        lecture_fichier = args[0]   
    if options.verbose: print("# Expérience %s " % options.id)
    # lire l'espèce initiale
    init_espece = charger_xml(lecture_fichier)
    # Si les graphismes sont activés, activer Pygame
    if options.graphismes:
        pygame.init()
        pygame.display.set_mode((LARGEUR,HAUTEUR),
        pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE if options.fullscreen else pygame.DOUBLEBUF)
        pygame.display.set_caption("Evolution de la créature pour %s" % (options.adaptation))
        pygame.mouse.set_visible(not options.fullscreen)
    # Débuter la simulation
    evolution_serialisee(init_espece, adaptation, save_frequency=options.save_frequency,
            limite=options.limite, verbose=options.verbose,start_itration=options.start_at, id=options.id, timer=int(options.timer))
    if options.graphismes:
        pygame.quit()
