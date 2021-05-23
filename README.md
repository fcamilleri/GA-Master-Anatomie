# Projet pour Master Anatomie-Morphogénèse-Imagerie

Algorithme génétique permettant de faire évoluer l'anatomie de créatures bidimensionnelles pour la locomotion terrestre.

![](./images/main.gif)

https://youtu.be/hnpN3FTBWZs



## Dépendences
- Python3.9.5 (https://www.python.org/downloads/)
- Pygame (https://www.pygame.org/wiki/GettingStarted)

## Exemple d'usage

```
#Générer une population aléatoire standard de 100 individus et la stocker dans randompop.xml
$ python ./pop_aleatoire.py  randompop.xml -p 100

#Faire évoluer cette population (Ctrl+C pour interrompre)
$ python ./evolution.py randompop.xml -v -id outputpop

#Afficher chaque créature de la population créée pendant 1000 cycles
$ python ./vue.py ./data/outputpop.xml -t 1000

#Afficher les paramètres disponibles
$ python ./evolution.py --help
```

Tutoriel vidéo: https://youtu.be/Kt2dmJf2BBQ
