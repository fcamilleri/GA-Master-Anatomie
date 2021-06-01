# -*- coding: utf-8 -*-
"""
Ce module implémente la créature, construite à partir de segments et d'articulations.
"""
import sys
from warnings import warn
from .physique import *
import xml.dom.minidom
from xml.parsers.expat import ExpatError
from math import sqrt, pi, fabs
def aVirgule(s):
    # teste si une variable est à virgule flottante
    if s.isdigit() or s == '.': return False
    spl = s.split('.')
    if len(spl) > 2: return False
    for p in spl:
        if p and not p.isdigit(): return False
    return True
class Creature(object):
    """
    Une créature est construite avec des noeuds qui correspondent à des masses ponctuelles, connectées par des segments qui lient ces
    noeuds et peuvent se contracter. Chaque segment dispose d'un cycle composé de contractions et distensions.
    """
    def __init__(self, parent=None, name="Inconnue au bataillon", angleDepart=0):
        """
        Créer une créature de novo ou qui descend d'un parent
        """
        self.articulations = []
        self.segments = []
        self._articulation_count_id = 0
        if not parent:
            self._information = {"name": name, "angle": angleDepart}
        else:
            # Agréger les articulations
            for articulation in parent.articulations:
                newarticulation = Articulation((articulation.pos.x, articulation.pos.y))
                newarticulation.id = articulation.id
                self.add(newarticulation)
            # Agréger les segments
            for segment in parent.segments:
                # Trouver la référence de chaque segment
                for articulation in self.articulations:
                    if articulation.id == segment.a.id:
                        A = articulation
                for articulation in self.articulations:
                    if articulation.id == segment.b.id:
                        B = articulation
                self.add(Segment(A, B, segment.amplitude, segment.decalage, segment.normal))
            # Copier les attributions
            self._articulation_count_id = parent._articulation_count_id
            self._information = dict(parent._information)
    def __setitem__(self, key, value):
        #fonction dictionnaire
        self._information[key] = value
        return value        
    def __getitem__(self, key):
        #fonction dictionnaire
        return self._information[key] if key in self._information else ''    
    def __iter__(self):
        #itération entre des _information
        return self._information.__iter__()
    def maj(self, atr=0.01, grav=PESANTEUR, elast=0.6, visc=0, moving=True):
        #mise à jour de l'état de la créature
        for articulation in self.articulations:
            articulation.maj(atr, grav, elast)
        for segment in self.segments:
            segment.maj(elast, self['angle'] if moving else None, visc)
        if moving:
            self['angle'] += INCREMENT_ANGLE
    def getArticulation(self, id):
        # obtenir l'articulation à partir de son identifiant
        for articulation in self.articulations:
            if articulation.id == id:
                return articulation
        else:
            return None
    def chargerXML(self, file=sys.stdin):
        # Lit un fichier XML et le transforme en créature 
        self.__init__(charger_xml(file, limite=1)[0])
        return self
    def sauvegarderXML(self, file=sys.stdout):
        # Sauve la créature donnée sous forme de XML
        sauvegarder_xml([self], file)
    def collision(self, autre, rayon=RAYON):
        for articulation in self.articulations:
            for articulation2 in autre.articulations:
                articulation.collision(articulation2, rayon)
    def collisionMur(self, limite, cote, atr_normal=0.6, atr_surface=0.5, min_vel=0.99, rayon=RAYON):
        force_collision = 0
        for articulation in self.articulations:
            force_collision += articulation.collisionMur(limite, cote, atr_normal, atr_surface, min_vel, rayon)
        return force_collision/len(self.articulations) if len(self.articulations) > 0 else 0
    def __len__(self):
        #nombre d'articulations
        return len(self.articulations)
    def add(self, objet):
        #ajouter une articulation ou un segment
        if objet.__class__ == Articulation:
            objet.parent = self
            if not hasattr(objet, "id"):
                self._articulation_count_id += 1
                objet.id = self._articulation_count_id
            self.articulations.append(objet)
        elif objet.__class__ == Segment:
            # Vérifier que le segment n'existe pas déjà
            for segment in self.segments:
                if (segment.a is objet.a or segment.b is objet.a) and (segment.a is objet.b or segment.b is objet.b):
                    break
            else:
                objet.parent = self
                self.segments.append(objet)
    def remove(self, objet):
        # retirer un segment
        if objet.__class__ == Articulation:
            # vérifier que le segment existe
            removelist = set()
            for segment in self.segments:
                if segment.a is objet or segment.b is objet:
                    removelist.add(segment)
            for segment in removelist:
                self.segments.remove(segment)
            self.articulations.remove(objet)
        elif objet.__class__ == Segment:
            self.segments.remove(objet)
    def centreGravite(self):
        #calculer le centre de gravité
        cx, cy = 0, 0
        total = 0
        for articulation in self.articulations:
            total += 1
            cx += articulation.pos.x
            cy += articulation.pos.y
        return cx / total,      cy / total
    def boiteContours(self, rayon=RAYON):
        #calculer les contours
        if len(self.articulations) == 0:
            return 0, 0, 0, 0
        min_x, max_x = self.articulations[0].pos.x, self.articulations[0].pos.x
        min_y, max_y = self.articulations[0].pos.y, self.articulations[0].pos.y
        for articulation in self.articulations:
            min_x = min(min_x, articulation.pos.x)
            min_y = min(min_y, articulation.pos.y)
            max_x = max(max_x, articulation.pos.x)
            max_y = max(max_y, articulation.pos.y)
        return min_x-rayon, min_y-rayon, max_x+rayon, max_y+rayon
    def flottantes(self):
        #renvoie à toutes les articulations non connectées
        if len(self.articulations) == 0:
            return []
        allsegments = self.segments[:]
        segmentsActuels = []
        toutesArticulations = self.articulations[1:]
        articulationActuelles = [self.articulations[0]]
        while len(articulationActuelles) > 0:
            atual = articulationActuelles.pop()
            for segment in allsegments:
                if segment.a is atual or segment.b is atual:
                    segmentsActuels.append(segment)
            for segment in segmentsActuels:
                allsegments.remove(segment)
                if segment.a in toutesArticulations:
                    toutesArticulations.remove(segment.a)
                    articulationActuelles.append(segment.a)
                elif segment.b in toutesArticulations:
                    toutesArticulations.remove(segment.b)
                    articulationActuelles.append(segment.b)
            segmentsActuels = []
        return toutesArticulations
    def retirerFlottantes(self):
        #retirer toutes les articulations non connectées
        articulations_deconnectees = self.flottantes()
        for articulation in articulations_deconnectees:
            self.articulations.remove(articulation)
        segments_deconnectes = []
        for segment in self.segments:
            if segment.a in articulations_deconnectees or segment.b in articulations_deconnectees:
                segments_deconnectes.append(segment)
        for segment in segments_deconnectes:
            self.segments.remove(segment)
    def __repr__(self):
        return "<Creature %s: %d articulations, %d segments>" % (self['name'], len(self.articulations), len(self.segments))

    def centreSol(self, hauteur):
        #centre la créature pour qu'elle touche le sol
        x1, y1, x2, y2 = self.boiteContours()
        cx = - ((x2+x1)//2)
        for articulation in self.articulations:
            articulation.pos.y -= (y2 - hauteur) + RAYON
            articulation.pos.x += cx
        return self
    def dessiner(self, ecran, tictac=None,
            backgroundcolor=(20,10,0), montrerTexte=True):
        suivi_x=True
        # dessine la créature en utilisant le moteur Pygame
        if not A_GRAPHISMES:
            raise exceptions.NotImplementedError("Module Pygame non trouvé. Veuillez l'installer.")
        # Obtenir la position centrale
        largeur, hauteur = ecran.get_size()
        x1, y1, x2, y2 = self.boiteContours()
        zm = min(min(largeur//((x2-x1)+50.0), hauteur//((y2-y1)+50.0)), 1.0)
        if suivi_x:
            bxp = (x2+x1)//2
            cx = bxp*zm - (largeur//2)
        byp = cy = 0
        if montrerTexte:
            font = pygame.font.Font(None, 20)    
        ecran.fill((0,0,0))
        taille_x, taille_y = largeur//10, hauteur//10
        for x in range(0,largeur+100,taille_x):
            for y in range(0,hauteur+100,taille_y):
                pygame.draw.rect(ecran, backgroundcolor,
                                 (int(x - bxp) % (taille_x+largeur) - taille_x, int(y - byp) % (taille_y+hauteur) - taille_y,
                                  taille_x-10,taille_y-10))               
        # Montrer l'arrière plan
        ecran.blit(bg, (int(x - bxp) % (largeur+taille_x) - taille_x - bgSize[0], 0))
        ecran.blit(bg, (int(x - bxp) % (largeur+taille_x) - taille_x, 0))
        # Dessiner les segments
        for segment in self.segments:
            length = (segment.a.pos - segment.b.pos).length()
            facteur = (length - segment.normal)/length if length > 0 else 0
            if facteur > 0:
                color = (255-min(int(facteur * 255), 255), 255, 255-min(int(facteur * 255), 255))
            elif facteur <= 0:
                color = (255, 255-min(int(-facteur * 255), 255), 255-min(int(-facteur * 255), 255))
            pygame.draw.line(ecran, color, (segment.a.pos.x*zm - cx, segment.a.pos.y*zm - cy),
                    (segment.b.pos.x*zm - cx, segment.b.pos.y*zm - cy), int(8*zm))
        # Dessiner les articulations
        velx, vely = 0, 0
        for articulation in self.articulations:
            velx += articulation.vel.x
            vely += articulation.vel.y
            #pygame.draw.circle(ecran, (0,0,0), (int(articulation.pos.x*zm - cx), int(articulation.pos.y*zm - cy)), int(RAYON*zm), 0)
            pygame.draw.circle(ecran, (160,40,80), (int(articulation.pos.x*zm - cx), int(articulation.pos.y*zm - cy)),
                               int(RAYON*zm), int(8*zm))
        velx //= len(self.articulations)
        vely //= len(self.articulations)
        if montrerTexte:
            # Rendu du nom de la créature
            texteNom = font.render("%s%s" % (self['name'], ""), False, (200,200,200))           
            ecran.blit(texteNom, (100,100))
try:
    import os, pygame
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
    A_GRAPHISMES = True
    # charger le fond d'écran une seule fois.
    bg = pygame.image.load('images/parking_externes_CBRS.jpg')
    bgSize = bg.get_rect().size
except ImportError:
    A_GRAPHISMES = False
def sauvegarder_xml(creatures, fichierSortie=sys.stdout): # écrit le génome d'une créature sous forme de XML
    fermerFichierSortie = (type(fichierSortie) is str)
    if fermerFichierSortie:
        fichierSortie = open(fichierSortie, 'w', encoding='utf-8')
    fichierSortie.write('<creatures>\n')
    for n, creature in enumerate(creatures):
        x1, y1, x2, y2 = creature.boiteContours()
        cx, cy = (x1+x2)//2, (y1+y1)//2
        fichierSortie.write('\t<creature ')
        for key, value in creature._information.items():
            fichierSortie.write('%s="%s" ' % (key, str(value)))
        fichierSortie.write('>\n')
        for articulation in creature.articulations:
            fichierSortie.write('\t\t<articulation pos="%d,%d" id="S%dN%d" />\n' % (articulation.pos.x-cx, articulation.pos.y-cy, n, articulation.id))
        for segment in creature.segments:
            fichierSortie.write('\t\t<segment from="S%dN%d" to="S%dN%d" ' % (n, segment.a.id, n, segment.b.id))
            if round(segment.amplitude, 2) != 0:
                fichierSortie.write('decalage="%.3f" amplitude="%.3f" ' % (segment.decalage, segment.amplitude))
            if fabs(segment.normal - sqrt(sum((segment.a.pos - segment.b.pos)**2))) > 1:
                fichierSortie.write('normal="%.3f" ' % (segment.normal))
            fichierSortie.write('/>\n')
        fichierSortie.write("\t</creature>\n")
    fichierSortie.write("</creatures>\n")
    if fermerFichierSortie:
        fichierSortie.close()
    else:
        fichierSortie.flush()
def charger_xml(arq=sys.stdin, limite=None):# lit un ficher XML et le transforme en créature
    try:
        doc = xml.dom.minidom.parse(arq)
    except ExpatError:
        warn("creature.chargerXML: XML parse error at file %s." %
                (arq.name if type(arq) == type(sys.stdin) else str(arq)))
        return []
    creatures = []
    for cnode in doc.childNodes:
        if cnode.nodeType is xml.dom.minidom.Node.ELEMENT_NODE:
            creaturesArticulation = cnode
            break
    else:
        warn("creature.charger_xml: There is no <creatures> XML element in file %s." %
                (arq.name if type(arq) == file else str(arq)))
        return []
    for creatureArticulation in creaturesArticulation.childNodes:
        if str(creatureArticulation.nodeName) == "creature":
            # Créer nouvelle créature
            newcreature = Creature()
            for key, value in list(creatureArticulation.attributes.items()):
                newcreature[key] = float(value) if aVirgule(value) else \
                (int(value) if value.isdigit() else value)
            for cnode in creatureArticulation.childNodes:
                if str(cnode.nodeName) == "articulation":
                    newarticulation = Articulation(pos=tuple((int(x) for x in str(cnode.attributes["pos"].value).split(","))))
                    newarticulation.id = int(str(cnode.attributes["id"].value).split('N')[-1])
                    newcreature._articulation_count_id = max(newcreature._articulation_count_id, newarticulation.id)
                    newcreature.add(newarticulation)
                elif str(cnode.nodeName) == "segment":
                    id_a = int(str(cnode.attributes["from"].value).split('N')[-1])
                    id_b = int(str(cnode.attributes["to"].value).split('N')[-1])
                    for articulation in newcreature.articulations:
                        if articulation.id == id_a:
                            a = articulation
                            break
                    else:
                        raise exceptions.IndexError("articulation id %d(from) non trouvée\n" % (id_a))
                    for articulation in newcreature.articulations:
                        if articulation.id == id_b:
                            b = articulation
                            break
                    else:
                        raise exceptions.IndexError("articulation id %d(to) non trouvée\n" % (id_b))
                    # Créer un segment
                    offs = float(str(cnode.attributes["decalage"].value)) if cnode.hasAttribute("decalage") else pi
                    ampl = float(str(cnode.attributes["amplitude"].value)) if cnode.hasAttribute("amplitude") else 0.0
                    norm = float(str(cnode.attributes["normal"].value)) if cnode.hasAttribute("normal") else None
                    newcreature.add(Segment(a, b, decalage=offs, amplitude=ampl, normal=norm))
            # Ajouter une nouvelle créature à la liste
            creatures.append(newcreature)
            # Vérfier si la limite a été atteinte
            if limite is not None and len(creatures) >= limite:
                break
    return creatures
