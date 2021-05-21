"""
Ce module a pour fonction de nommer aléatoirement les sessions d'évolution avec des noms françasi ou pseudo-latins à peu près prononçables.
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import choice
from random import randrange
import io
    
def nomFrancais(opt):        
    if opt == 0:
       prenoms = open("./creatures/dictionnaire_prenoms.txt", 'r', encoding='utf-8').readlines()
       pN = len(prenoms)
       return prenoms[randrange(pN)].strip("\n")
    else:
       noms = open("./creatures/dictionnaire_noms.txt", 'r', encoding='utf-8').readlines()
       nN = len(noms)
       return noms[randrange(nN)].strip("\n").upper()

def pseudoNomLatin(sil=5):
    """
    Crée un nom pseudo-latin avec n syllabes
    """
    #: voyelles
    VOG = 'a e i o u ae ia au eu io iu ie'.split()
    #: consonnes
    CONS = 'b c d e f g h j l m p q r s t v pr gr st fr dr ph br'.split()
    MIDCONS = 'mm pp cc tt mn rs ll'.split()
    #: Terminaisons optionnelles
    TERM = 'um us a'.split()
    word = ''
    vog = choice([True, False])
    for x in range(sil-1):
        word += choice(VOG) if vog else choice(CONS+MIDCONS if x>0 else CONS)
        vog = not vog

    if not vog:
        word += choice(CONS + MIDCONS)

    word += choice(TERM) if choice([True, False]) else choice(VOG)

    return word[0].upper() + word[1:]
