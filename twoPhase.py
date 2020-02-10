# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 19:01:18 2016

@author: Maxime
"""

from cubeCoord import Cube
from tables import MoveTable, PruningTable, PHASE1_MOVES, PHASE2_MOVES

from time import time
from copy import copy

faces = ['U', 'D', 'R', 'F', 'L', 'B']

moveTables = MoveTable(generate=False)
pruningTables = PruningTable(moveTables, generate=False)

# Tables de la phase 1
moveFlip, moveTwist, moveUDSlice1 = moveTables['flip'], moveTables['twist'], moveTables['UDSlice1']
flipPrun, twistPrun = pruningTables[('flip', 'UDSlice1')], pruningTables[('twist', 'UDSlice1')]
# Tables de la phase 2
moveCPerm, moveP2ePerm, moveUDSlice2 = moveTables[
    'cPerm'], moveTables['phase2ePerm'], moveTables['UDSlice2']
cPermPrun, p2ePermPrun = pruningTables[
    ('cPerm', 'UDSlice2')], pruningTables[('phase2ePerm', 'UDSlice2')]


def distance1(etat):
    """
    Renvoie le max des distances de l'état actuel du cube à l'identité d'après
    les pruning tables de la phase 1.
    """
    flip, twist, UDSlice1 = etat
    return max(flipPrun[flip, UDSlice1], twistPrun[twist, UDSlice1])


def distance2(etat):
    """
    Renvoie le max des distances de l'état actuel du cube à l'identité d'après
    les pruning tables de la phase 2.
    """
    cPerm, p2ePerm, UDSlice2 = etat
    return max(cPermPrun[cPerm, UDSlice2], p2ePermPrun[p2ePerm, UDSlice2])


PAS_BON = False
BON = True

bcpTrop = 20


class Solver:
    """ Algorithme Two-Phase """

    def __init__(self, cube):
        ### Initialisation ###

        self.resultat1 = PAS_BON

        self.cube = cube
        self.etat = (cube.getFlip(), cube.getTwist(), cube.getUDSlicePos())

        self.limite1 = distance1(self.etat)

        self.solution1 = [None] * bcpTrop
        ### Fin initialisation ###
        self.phase1()
        self.phase2()

    def phase1(self):
        """ Effectue la phase 1 de l'agorithme """
        while self.resultat1 is PAS_BON:
            self.newLimite1 = bcpTrop
            self.resultat1 = self.recherche1(self.etat, 0)
            self.limite1 = self.newLimite1
        return

    def recherche1(self, etat, depth):
        """ Fonction de recherche de la phase 1 """
        dist = distance1(etat)

        if dist == 0:
            return BON

        distTemp = dist + depth

        if distTemp <= self.limite1:
            for mvt in PHASE1_MOVES:
                newFlip = moveFlip[etat[0], mvt]
                newTwist = moveTwist[etat[1], mvt]
                newUDSlice1 = moveUDSlice1[etat[2], mvt]
                newEtat = (newFlip, newTwist, newUDSlice1)
                self.solution1[depth] = mvt

                self.resultat1 = self.recherche1(newEtat, depth + 1)
                if self.resultat1:
                    return self.resultat1
        else:
            if distTemp < self.newLimite1:
                self.newLimite1 = distTemp
        return PAS_BON

    def getPhase1Solution(self):
        """ Enlève les None en trop et renvoie la solution de la phase 1 """
        while None in self.solution1:
            self.solution1.remove(None)
        return self.solution1

    def phase2(self):
        self.resultat2 = PAS_BON

        self.cube.rotate(self.getPhase1Solution())
        self.etat2 = (self.cube.getCPermCoord(),
                      self.cube.getPhase2EdgePerm(),
                      self.cube.getUDSlicePerm())
        self.limite2 = distance2(self.etat2)

        self.solution2 = [None] * bcpTrop

        while self.resultat2 == PAS_BON:
            self.newLimite2 = bcpTrop
            self.resultat2 = self.recherche2(self.etat2, 0)
            self.limite2 = self.newLimite2
        return self.resultat2

    def recherche2(self, etat, depth):
        dist = distance2(etat)
        if dist == 0:
            return BON

        distTemp = depth + dist

        if distTemp <= self.limite2:
            for mvt in PHASE2_MOVES:
                newCPerm = moveCPerm[etat[0], mvt]
                newP2ePerm = moveP2ePerm[etat[1], mvt]
                newSlice2 = moveUDSlice2[etat[2], mvt]
                newEtat = (newCPerm, newP2ePerm, newSlice2)
                self.solution2[depth] = mvt

                self.resultat2 = self.recherche2(newEtat, depth + 1)
                if self.resultat2:
                    return self.resultat2
        else:
            if distTemp < self.newLimite2:
                self.newLimite2 = distTemp
        return PAS_BON

    def getPhase2Solution(self):
        while None in self.solution2:
            self.solution2.remove(None)
        return self.solution2

    def getSolution(self):
        return self.getPhase1Solution() + self.getPhase2Solution()

####################
### Statistiques ###
####################

def statsWrite(n=10):
    
    with open("res/" + "stats_n=" + str(n) + ".txt", 'w') as fichier:
        temps, nb_mvts = [], []
        for i in range(n):
            c = Cube()
            c.melanger()
            
            debut = time()
            s = Solver(c)
            fin = time()
            
            temps.append(fin-debut)
            nb_mvts.append(len(s.getSolution()))
            fichier.write(str(fin-debut) + ' ' + str(len(s.getSolution())) + '\n')
            print(i)
    return temps, nb_mvts
        
def statsRead(n=10):
    try:
        with open("res/" + "stats_n=" + str(n) + ".txt", 'r') as fichier:
            lines = fichier.readlines()
        
        
        temps, nb_mvts = [], []
        for l in lines:
            data = l.split()
            temps.append(float(data[0]))
            nb_mvts.append(int(data[1]))
    except FileNotFoundError:
        print("Le fichier stats_n={} est introuvable.".format(n))
    else:
        return temps, nb_mvts




