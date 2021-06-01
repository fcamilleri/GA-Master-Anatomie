# Projet pour Master d'Anatomie-Morphogénèse-Imagerie

Algorithme génétique permettant de faire évoluer l'anatomie de créatures bidimensionnelles pour la locomotion terrestre.

![](./images/main.gif)

Quelques exemples de créatures https://youtu.be/jIrU-AoiPvc (toutes nos vidéos sont non-référencées)



## Dépendences
- Python3.9.5 (https://www.python.org/downloads/)
- Pygame (https://www.pygame.org/wiki/GettingStarted)

## Exemple d'usage

Exemple d'usage en vidéo: https://youtu.be/Kt2dmJf2BBQ

```
#Générer une population aléatoire standard de 100 individus et la stocker dans randompop.xml
$ python ./pop_aleatoire.py  randompop.xml -p 100

#Faire évoluer cette population (Ctrl+C pour interrompre)
$ python ./evolution.py randompop.xml -v -id outputpop

#Afficher chaque créature de la population créée pendant 1000 cycles
$ python ./vue.py ./data/outputpop.xml -t 1000
```

