# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 18:01:56 2015

@author: Maxime
"""
from time import time
from random import choice, randint

from data import *
import renderer as r

def binomial(n, k):
    """
    A fast way to calculate binomial coefficients by Andrew Dalke.
    See http://stackoverflow.com/questions/3025162/statistics-combinations-in-python
    """
    if 0 <= k <= n:
        ntok = 1
        ktok = 1
        for t in range(1, min(k, n - k) + 1):
            ntok *= n
            ktok *= t
            n -= 1
        return ntok // ktok
    else:
        return 0

class Cube:
    """
    Le cube est défini par 4 listes :
        - la permutation des arêtes
        - la permutation des coins
        - l'orientation des arêtes
        - l'orientation des coins
    Puis on calcule un certain nombre de coordonnées utiles pour la résolution :
        - l'orientation des coins : Twist
        - l'orientation des arêtes : Flip
        - la permutation des coins : cPermCoord
        - la position et la permutation des arêtes des faces U et D : UDSlicePos et UDSlicePerm
        - la permutation des 8 autres arêtes : phase2EdgePerm
    """

    def __init__(self):
        """
        Constructeur d'un cube tout neuf.
        """
        self.edgePermutation = [i for i in range(12)]
        self.cornerPermutation = [i for i in range(8)]

        self.edgesOrientations = [0] * 12
        self.cornersOrientations = [0] * 8
        return

    def __repr__(self):
        return "Cube(edgePermutation=" + str(self.edgePermutation) + \
            ", cornerPermutation=" + str(self.cornerPermutation) + \
            ", Twist=" + str(self.getTwist()) + ", Flip=" + str(self.getFlip()) + ")"

    def __str__(self):
        return self.__repr__()

    ### Getters ###

    def getTwist(self):
        """ On repasse en base 10 pour revenir à un unique entier. """
        twist = 0
        for i in range(7):
            twist *= 3
            twist += self.cornersOrientations[i]
        return twist

    def getFlip(self):
        """ On repasse en base 10 pour revenir à un unique entier."""
        flip = 0
        for i in range(11):
            flip *= 2
            flip += self.edgesOrientations[i]
        return flip

    def getCPermCoord(self):
        """
        On détermine la valeur de pc en calculant, pour chaque coin, le nombre
        de coins "inférieurs" (pour l'ordre l.24 data.py) placées "à gauche" de
        celui-ci et on recalcule pc comme somme de factorielles.
        """
        p = self.cornerPermutation
        x = 0
        for i in range(7, 0, -1):
            k = 0
            for j in range(i - 1, -1, -1):
                if p[j] > p[i]:
                    k += 1
            x = (x + k) * i
        return x

    def getUDSlicePos(self):
        UDSlicePos, k = 0, 0
        for i in range(11, -1, -1):
            if self.edgePermutation[i] >= 8:
                k += 1
                UDSlicePos += binomial(11 - i, k)
        return int(UDSlicePos)

    def getUDSlicePerm(self):
        j = 0
        UDSlicePerm = [-1] * 4
        for i in range(12):
            if self.edgePermutation[i] >= 8:
                UDSlicePerm[j] = self.edgePermutation[i]
                j += 1
        x = 0
        for j in range(3, 0, -1):
            s = 0
            for k in range(j - 1, -1, -1):
                if UDSlicePerm[k] > UDSlicePerm[j]:
                    s += 1
            x = (x + s) * j
        return x

    def getPhase2EdgePerm(self):
        x = 0
        for i in range(7, 0, -1):
            s = 0
            for j in range(i - 1, -1, -1):
                if self.edgePermutation[j] > self.edgePermutation[i]:
                    s += 1
            x = (x + s) * i
        return x

    ### Setters ###

    def setCPermCoord(self, cPerm):
        """
        On récupère les positions des coins en convertissant la valeur
        dans la base variable des factorielles (ligne 33 data.py).
        Chaque coefficient indique le nombre de coins "supérieurs" situés
        à des positions "inférieures".Le premier coin est alors déduit des
        autres (permutation = bijection)
        @return : permutation des coins par rapport à l'ordre de référence
            (cf. ligne 24 data.py)
        """
        pos = []    # Nombre de coins supérieurs situés à des pos inférieures
        for i in range(7, -1, -1):
            pos.insert(0, cPerm // fact[i])
            cPerm %= fact[i]
        # Ici, pos est terminée, on construit res la permutation des coins
        self.cornerPermutation = []
        lc = [i for i in range(8)]
        for i in range(7, -1, -1):
            self.cornerPermutation.insert(0, lc.pop(len(lc) - pos[i] - 1))
        return

    def setTwist(self, twist):
        """
        On récupère les orientations des 7 premiers coins en
        utilisant un algorithme de changement de base puis on
        détermine l'orientation du dernier par addition modulo 3.
        """
        self.cornersOrientations = [0] * 8
        for i in range(6, -1, -1):
            self.cornersOrientations[i] = twist % 3
            twist //= 3
        # On détermine l'orientations du 8eme coin
        self.cornersOrientations[7] = -sum(l for l in self.cornersOrientations) % 3
        return

    def setFlip(self, flip):
        """
        On récupère les orientations des 11 premières arêtes en
        utilisant un algorithme de changement de base puis on
        détermine l'orientation de la dernière par addition modulo 2.
        """
        self.edgesOrientations = [0] * 12
        for i in range(10, -1, -1):
            self.edgesOrientations[i] = flip % 2
            flip //= 2
        # On détermine l'orientations de la 12eme arête
        self.edgesOrientations[11] = -sum(l for l in self.edgesOrientations) % 2
        return

    def setUDSlicePos(self, UDSlicePos):
        """ Construit un cube dont la coordonnées SortedUDSlice correspond à UDSlice. """
        UDSliceEdges = [8, 9, 10, 11]
        others = list(range(8))
        ePerm = [7] * 12

        x = 3
        for j in range(12):
            a = binomial(11 - j, x + 1)
            if (UDSlicePos - a) >= 0:
                ePerm[j] = UDSliceEdges[3 - x]
                UDSlicePos -= a
                x -= 1
        x = 0
        for j in range(12):
            if ePerm[j] == 7:
                ePerm[j] = others[x]
                x += 1
        self.edgePermutation = ePerm
        return

    def setUDSlicePerm(self, UDSlicePerm):
        pos = []
        for i in range(3, -1, -1):
            pos.insert(0, UDSlicePerm // fact[i])
            UDSlicePerm %= fact[i]

        self.edgePermutation = [0, 1, 2, 3, 4, 5, 6, 7]
        la = [i for i in range(8, 12)]
        for i in range(3, -1, -1):
            self.edgePermutation.insert(8, la.pop(len(la) - pos[i] - 1))
        return

    def setPhase2EdgePerm(self, p2ePerm):
        """
        Crée la permutation des 8 arêtes de UR à DB, à partir de la nouvelle
        coordonnée p2ePerm.
        """
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
        mvts = [(choice(['U', 'D', 'R', 'F', 'L', 'B']), randint(1, 3)) for i in range(n)]
        self.rotate(mvts)
        print(mvts)
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
