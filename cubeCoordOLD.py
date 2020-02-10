# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 18:01:56 2015

@author: Maxime
"""
from time import time
from random import choice
from scipy.special import binom

from data import *
import renderer as r


class Cube:
    """
    Le cube est défini par de multiples coordonnées :
        - l'orientation des coins : OC
        - l'orientation des arêtes : OA
        - la permutation des coins : PC
        - la permutation des arêtes : PA
        - la permutation des arêtes des faces U et D : UDSlice
    """

    def __init__(self, oc=0, oa=0, pc=0, pa=0):
        """
        Constructeur du Cube, on donne juste les 4 entiers et on calcule
        directement les orientations et les permutations des pièces.
        """

        # Permutation des coins
        self.setNewPC(pc)
        # Permutation des coins
        self.setNewPA(pa)
        # Orientation des coins
        self.setNewOC(oc)
        # Orientation des arêtes
        self.setNewOA(oa)
        # UDSliceCoord
        self.updateSortedUDSlice()
        # phase2EdgePerm
        self.updatePhase2EdgePerm()
        return

    def __repr__(self):
        return "Cube(oc = " + str(self.oc) + ", oa = " + str(self.oa) + \
               ", pc = " + str(self.pc) + ", pa = " + str(self.pa) + ", SortedUDSlice = " + \
               str(self.SortedUDSlice) + ")"

    def __str__(self):
        return self.__repr__()

    ### Getters ###

    def getOC(self):
        return self.oc

    def getOA(self):
        return self.oa

    def getPC(self):
        return self.pc

    def getPA(self):
        return self.pa

    def getSortedUDSlice(self):
        return self.SortedUDSlice

    def getUDSlice1(self):
        return self.SortedUDSlice // 24

    def getUDSlice2(self):
        return self.SortedUDSlice % 24

    def getPhase2EdgePerm(self):
        return self.phase2EdgePerm

    ### Setters ###

    def setNewPC(self, pc):
        """
        On récupère les positions des coins en convertissant la valeur
        dans la base variable des factorielles (ligne 33 data.py).
        Chaque coefficient indique le nombre de coins "supérieurs" situés
        à des positions "inférieures".Le premier coin est alors déduit des
        autres (permutation = bijection)
        @return : permutation des coins par rapport à l'ordre de référence
            (cf. ligne 24 data.py)
        """
        self.pc = pc
        pos = []    # Nombre de coins supérieurs situés à des pos inférieures
        for i in range(7, -1, -1):
            pos.insert(0, pc // fact[i])
            pc %= fact[i]
        # Ici, pos est terminée, on construit res la permutation des coins
        self.cornerPermutation = []
        lc = [i for i in range(8)]
        for i in range(7, -1, -1):
            self.cornerPermutation.insert(0, lc.pop(len(lc) - pos[i] - 1))
        return

    def setNewPA(self, pa):
        """
        On récupère les positions des arêtes en convertissant la valeur
        dans la base variable des factorielles (ligne 33 data.py).
        Chaque coefficient indique le nombre d'arêtes "supérieures" situés
        à des positions "inférieures". La première arête est alors déduite
        des autres.
        @return : permutation des arêtes par rapport à l'ordre de référence
            (ligne 28 data.py)
        """
        self.pa = pa
        pos = []  # nombre d'arêtes supérieures situées à des pos inférieures
        for i in range(11, -1, -1):
            pos.insert(0, pa // fact[i])
            pa %= fact[i]
        # Ici, pos est terminée, on construit res la permutation des arêtes
        self.edgePermutation = []
        la = [i for i in range(12)]
        for i in range(11, -1, -1):
            self.edgePermutation.insert(0, la.pop(len(la) - pos[i] - 1))
        return

    def setNewOC(self, oc):
        """
        On récupère les orientations des 7 premiers coins en
        utilisant un algorithme de changement de base puis on
        détermine l'orientation du dernier par addition modulo 3.
        """
        self.oc = oc
        self.cornersOrientations = [0] * 8
        for i in range(6, -1, -1):
            self.cornersOrientations[i] = oc % 3
            oc //= 3
        # On détermine l'orientations du 8eme coin
        self.cornersOrientations[7] = -sum(l for l in self.cornersOrientations) % 3
        return

    def setNewOA(self, oa):
        """
        On récupère les orientations des 11 premières arêtes en
        utilisant un algorithme de changement de base puis on
        détermine l'orientation de la dernière par addition modulo 2.
        """
        self.oa = oa
        self.edgesOrientations = [0] * 12
        for i in range(10, -1, -1):
            self.edgesOrientations[i] = oa % 2
            oa //= 2
        # On détermine l'orientations de la 12eme arête
        self.edgesOrientations[11] = -sum(l for l in self.edgesOrientations) % 2
        return

    def setSortedUDSlice(self, UDSlice):
        """ Construit un cube dont la coordonnées SortedUDSlice correspond à UDSlice. """
        self.SortedUDSlice = UDSlice
        UDSliceCoord = UDSlice // 24
        UDSlicePermCoord = UDSlice % 24
        UDSliceEdges = [8, 9, 10, 11]
        others = list(range(8))
        ePerm = [7] * 12

        for j in range(1, 4):
            k = UDSlicePermCoord % (j + 1)
            UDSlicePermCoord //= (j + 1)
            # rotateRight(UDSliceEdges, 0, j)
            for i in range(k):
                temp = UDSliceEdges[j]
                for l in range(j, 0, -1):
                    UDSliceEdges[l] = UDSliceEdges[l - 1]
                UDSliceEdges[0] = temp

        x = 3
        for j in range(12):
            a = binom(11 - j, x + 1)
            if (UDSliceCoord - a) >= 0:
                ePerm[j] = UDSliceEdges[3 - x]
                UDSliceCoord -= a
                x -= 1
        x = 0
        for j in range(12):
            if ePerm[j] == 7:
                ePerm[j] = others[x]
                x += 1
        self.edgePermutation = ePerm
        return

    def setUDSlice1(self, UDSlice1):
        return self.setSortedUDSlice(UDSlice1 * 24)

    def setUDSlice2(self, UDSlice2):
        return self.setSortedUDSlice(UDSlice2)

    def setPhase2EdgePerm(self, p2ePerm):
        """
        Crée la permutation des 8 arêtes de UR à DB, à partir de la nouvelle
        coordonnée p2ePerm.
        """
        self.phase2EdgePerm = p2ePerm
        pos = []  # nombre d'arêtes supérieures situées à des pos inférieures
        for i in range(7, -1, -1):
            pos.insert(0, p2ePerm // fact[i])
            p2ePerm %= fact[i]
        # Ici, pos est terminée, on construit res la permutation des arêtes
        self.edgePermutation = [8, 9, 10, 11]
        la = [i for i in range(8)]
        for i in range(7, -1, -1):
            self.edgePermutation.insert(0, la.pop(len(la) - pos[i] - 1))
        return

    ### Fonctions de rotations ###

    def updateOC(self):
        """ On repasse en base 10 pour revenir à un unique entier oc. """
        self.oc = 0
        for i in range(7):
            self.oc *= 3
            self.oc += self.cornersOrientations[i]
        return

    def updateOA(self):
        """ On repasse en base 10 pour revenir à un unique entier oa."""
        self.oa = 0
        for i in range(11):
            self.oa *= 2
            self.oa += self.edgesOrientations[i]
        return

    def updatePC(self):
        """
        On détermine la valeur de pc en calculant, pour chaque coin, le nombre
        de coins "inférieurs" (pour l'ordre l.24 data.py) placées "à gauche" de
        celui-ci et on recalcule pc comme somme de factorielles.
        """
        p = self.cornerPermutation
        res = []
        for i in range(1, 8):
            res.append(sum(1 for j in range(0, i) if p[j] > p[i]))
        # Puis on recalcule la valeur de pc
        self.pc = sum(res[i - 1] * fact[i] for i in range(1, 8))
        return

    def updatePA(self):
        """
        On détermine la valeur de pa en calculant, pour chaque arête, le nombre
        d'arêtes "inférieures" (pour l'ordre l.26 data.py) placées "à gauche" de
        celui-ci et on recalcule pa comme somme de factorielles.
        """
        p = self.edgePermutation
        res = []
        for i in range(1, 12):
            res.append(sum(1 for j in range(0, i) if p[j] > p[i]))
        # Puis on recalcule la valeur de pa
        self.pa = sum(res[i - 1] * fact[i] for i in range(1, 12))
        return

    def updateSortedUDSlice(self):
        """
        Permutation des 4 aretes FR, FL, BL, BR dont les indices sont 8,9,10 ou 11.
        UDSlice est un entier entre 0 et 11879.
        """
        UDSlicePosition, UDSliceCoord = 0, 0
        UDSlicePerm = [-1, -1, -1, -1]
        for i in range(11, -1, -1):
            j = self.edgePermutation[i]
            if j >= 8:
                UDSlicePerm[3 - UDSlicePosition] = j
                UDSlicePosition += 1
                UDSliceCoord += binom(11 - i, UDSlicePosition)

        b = 0
        for j in range(3, 0, -1):
            # s = 0
            # for k in range(j - 1, -1, -1):
            #     if UDSlicePerm[k] > UDSlicePerm[j]:
            #         s += 1
            # b = (b + s) * j
            k = 0
            while UDSlicePerm[j] != j + 8:
                # rotateLeft(UDSlicePerm, 0, j)
                temp = UDSlicePerm[0]
                for i in range(0, j):
                    UDSlicePerm[i] = UDSlicePerm[i + 1]
                UDSlicePerm[j] = temp
                k += 1
            b = (j + 1) * b + k

        self.SortedUDSlice = int(UDSliceCoord * 24 + b)
        return

    def updatePhase2EdgePerm(self):
        """
        Renvoie la coordonnée codant la permutation des 8 arêtes UR à DB,
        dans la phase 2 de l'algorithme. Elle est comprise entre 0 et 40319 (8! - 1).
        """
        ePerm = self.edgePermutation[:]
        coord = 0
        for i in range(7, 0, -1):
            # s = 0
            # for j in range(i - 1, -1, -1):
            #     if self.edgePermutation[j] > self.edgePermutation[i]:
            #         s += 1
            # coord = (coord + s) * i
            k = 0
            while ePerm[i] != i:
                # rotateLeft(ePerm, 0, i)
                temp = ePerm[0]
                for j in range(0, i):
                    ePerm[j] = ePerm[j + 1]
                ePerm[i] = temp
                k += 1
            coord = (i + 1) * coord + k
        self.phase2EdgePerm = coord
        return

    def moveCorners(self, mvt):
        """ Calcule la nouvelle position des coins après le mouvement mvt """
        p = self.cornerPermutation
        mvtp = permutations_coins[mvt]
        mvto = orientations_coins[mvt]
        self.cornerPermutation = [p[mvtp[i]] for i in range(8)]
        self.cornersOrientations = [
            (self.cornersOrientations[mvtp[i]] + mvto[i]) % 3 for i in range(8)]
        return

    def moveEdges(self, mvt):
        """ Calcule la nouvelle position des arêtes après le mouvement mvt """
        p = self.edgePermutation
        mvtp = permutations_aretes[mvt]
        mvto = orientations_aretes[mvt]
        # On compose la permutation actuelle avec celle du mouvement
        self.edgePermutation = [p[mvtp[i]] for i in range(12)]
        self.edgesOrientations = [
            (self.edgesOrientations[mvtp[i]] + mvto[i]) % 2 for i in range(12)]
        return

    def rotate(self, mvt):
        """ Effectue la liste de mouvements mvt """
        for (face, power) in mvt:
            for i in range(power):
                self.moveCorners(face)
                self.moveEdges(face)

        # On met à jour les 6 entiers oc, oa, pc, pa, UDSlice et phase2ePerm
        self.updateOC()
        self.updateOA()
        self.updatePC()
        self.updatePA()
        self.updateSortedUDSlice()
        self.updatePhase2EdgePerm()
        return

    def animation(self, fenetre, liste_mouvements):
        """ Anime les rotations du cube définies dans liste_mouvements """
        for (face, power) in liste_mouvements:
            r.animRotation(fenetre, self, face, power)
            self.rotate([(face, power)])
        return

    ### Fonctions de manipulation du cube ###

    def melanger(self, n=25):
        """ Mélange le cube en effectuant n=25 mouvements choisis aléatoirement """
        mvts = [(choice(['U', 'D', 'R', 'F', 'L', 'B']), 1) for i in range(n)]
        self.rotate(mvts)
        return mvts

    def edgeParity(self):
        s = 0
        for i in range(11, 0, -1):
            for j in range(i - 1, -1, -1):
                if self.edgePermutation[j] > self.edgePermutation[i]:
                    s += 1
        return s % 2

    def cornerParity(self):
        s = 0
        for i in range(7, 0, -1):
            for j in range(i - 1, -1, -1):
                if self.cornerPermutation[j] > self.cornerPermutation[i]:
                    s += 1
        return s % 2

    def verifier(self):
        """ Vérifie que le cube est resoluble """
        # Teste si toutes les arêtes existent exactement une fois.
        for i in range(12):
            if i not in self.edgePermutation:
                return False
        # Teste si tous les coins existent exactement un fois.
        for i in range(8):
            if i not in self.cornerPermutation:
                return False
        # Teste le défaut de flip.
        s = 0
        for i in range(12):
            s += self.edgesOrientations[i]
        if s % 2 != 0:
            # Une arête doit être retournée.
            return False
        # Teste le défaut de twist.
        s = 0
        for i in range(8):
            s += self.cornersOrientations[i]
        if s % 3 != 0:
            # Un coin doit être pivoté.
            return False
        if self.edgeParity() ^ self.cornerParity() != 0:
            # Défaut de parité, il faut échanger 2 arêtes ou 2 coins.
            return False
        return True


def timef(f, c=Cube()):
    """
    Fonction permettant de mesurer le temps d'éxécution d'une méthode du Cube
        f = Cube.methode
    """
    a = time()
    d = f(c)
    b = time()
    print(d)
    return(b - a)

c = Cube()
c.melanger()
