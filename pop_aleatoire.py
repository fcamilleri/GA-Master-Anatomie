#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ce module génère des populations entièrement aléatoires pour initialiser l'algorithme génétique
"""

from etc.creature import sauvegarder_xml
from etc.evoluer_creature import creature_aleatoire
import sys
import optparse
if __name__ == "__main__":
    # Lecture des paramères de la ligne de commande
    analyseur = optparse.OptionParser(description="Générer une espece XML aléatoire")
    analyseur.add_option("-p", "--population", dest="espece", default=1,
            help="Taille de la population", metavar="NUMBER")
    analyseur.add_option("-n", "--articulations", dest="articulations_num", default=10,
            help="Nombre de noeuds (articulations)", metavar="NUMBER")
    analyseur.add_option("-s", "--segments", dest="segments_num", default=30,
            help="Nombre de segments", metavar="NUMBER")
    analyseur.add_option("-r", "--rayon_articulation", dest="articulation_rayon", default=100,
            help="Taille maximale de la créature", metavar="NUMBER")
    (options, args) = analyseur.parse_args()
    # Lecture des valeurs intégrales
    options.espece = int(options.espece)
    options.segments_num = int(options.segments_num)
    options.articulations_num = int(options.articulations_num)
    options.articulation_rayon = int(options.articulation_rayon)
    # Créer une espece de créatures générées aléatoirement ett
    # écrire le résultat dans un fichier XML
    sauvegarder_xml(\
            [creature_aleatoire(options.articulations_num, options.segments_num, options.articulation_rayon) \
            for x in range(options.espece)], fichierSortie=args[0])