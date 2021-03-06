#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Permet de coordonner plusieurs instances d'évolution en parallèle pour utiliser un maximum de coeurs du processeur pendant la nuit et obtenir
un maximum de créatures intéressantes.
Il existe un temps d'expiration de chaque instance. Les résultats de toutes les instances sont comparés toutes les t heures, 
et les k espèces les moins performantes sont supprimées et remplacées par des especes aléatoires.
Cela permet de mettre "en concurrence" différentes espèces et de se débarrasser des convergences prématurées.
"""
from etc import adaptation
from etc.creature import sauvegarder_xml, charger_xml
from etc.noms import nomFrancais, pseudoNomLatin
import optparse, os, time, evolution, pop_aleatoire
import multiprocessing as mp
n = 12 #        nombre d'instances en parallèle
k = 3 #         pression de sélection < n
t = 2 * 3600 #  duree d'évolution d'une instance en heures
pop = 100 #      taille de population
rad = 125 #     diamètre maximal des créatures
# lancement d'une instance d'évolution
def evolveWorker(data):
    init_espece = charger_xml(data[0])
    return evolution.evolution_serialisee(init_espece, data[2],
            verbose=data[3], graphismes=False,
            meilleur=data[4],id=data[1], timer=int(data[5]), path=data[6]+"/", index=data[7])
# Génération d'un identifiant unique pour une nouvelle espèce (aléatoire)
def getSeed(name,generation,idx):
    return "./data/"+str(name)+"/"+str(generation)+"-"+str(idx)+".xml"
# Obtention de l'espèce aléatoire et sauvegarde dans un fichier XML
def randomBot(seed):
    os.system("python ./pop_aleatoire.py -p "+str(pop)+" -r "+str(rad)+" \""+seed+"\"")
if __name__ == "__main__":
    # Lecture de la ligne de commande
    analyseur = optparse.OptionParser(description="Permet de créer un grand nombre de créatures pour le mémoire")
    analyseur.add_option("-v", "--verbose", dest="verbose", default=False,
            help="Sortie bavarde", action="store_true")
    analyseur.add_option("-b", "--meilleur", dest="meilleur", default=False,
            help="sauver le meilleur de chaque génération", action="store_true")
    analyseur.add_option("-t", "--timer", dest="timer", default=t,
            help="instaure une limite de temps", metavar="TIME")
    (options, args) = analyseur.parse_args()
    adaptation = adaptation.__dict__["course"]
    ExpName = pseudoNomLatin(4)
    print("Experiment Name:" + ExpName)
    os.mkdir('./data/'+ExpName)
    gen = 0
    while True:
        inputs = list()
        for index in range(n):
            index = str(index)
            seed = getSeed(ExpName,gen,index)
            if gen == 0:
                randomBot(seed)
            # cleanup
            #if gen >= 2:
            #    os.remove(getSeed(ExpName,gen-2,index))
            initPop = charger_xml(seed)
            x = (seed,str(gen+1) + "-" + index,adaptation,options.verbose,options.meilleur,options.timer,ExpName,index)
            inputs.append(x) 
        with mp.Pool(n) as pool:
            results = pool.map(evolveWorker, inputs)
        results.sort()
        print(results)
        for j in range(k):
            kill = results[j][1]
            seed = getSeed(ExpName,gen+1,kill)
            randomBot(seed) 
        gen += 1 
        print('done gen ' + str(gen))