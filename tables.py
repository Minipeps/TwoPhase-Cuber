#########################################################
### Définition et générations des move/pruning tables ###
#########################################################

import numpy as np

from cubeCoord import Cube

faces = ['U', 'D', 'R', 'F', 'L', 'B']

PHASE1_MOVES = [(f, p) for f in faces for p in range(1, 4)]

PHASE2_MOVES = [(f, p) for f in ('U', 'D') for p in range(1, 4)] + [(f, 2)
                                                                    for f in ('R', 'F', 'L', 'B')]

COORDS = {'twist': (Cube.getTwist, Cube.setTwist, 2187, PHASE1_MOVES),
          'flip': (Cube.getFlip, Cube.setFlip, 2048, PHASE1_MOVES),
          'cPerm': (Cube.getCPermCoord, Cube.setCPermCoord, 40320, PHASE2_MOVES),
          'phase2ePerm': (Cube.getPhase2EdgePerm, Cube.setPhase2EdgePerm, 40320, PHASE2_MOVES),
          'UDSlice1': (Cube.getUDSlicePos, Cube.setUDSlicePos, 495, PHASE1_MOVES),
          'UDSlice2': (Cube.getUDSlicePerm, Cube.setUDSlicePerm, 24, PHASE2_MOVES)}

PRUNING_COUPLES = [('flip', 'UDSlice1', PHASE1_MOVES), ('twist', 'UDSlice1', PHASE1_MOVES),
                   ('cPerm', 'UDSlice2', PHASE2_MOVES), ('phase2ePerm', 'UDSlice2', PHASE2_MOVES)]


###################
### Move Tables ###
###################


class MoveTable:
    """ Classe permettant la génération des moveTables. """

    def __init__(self, generate=False):
        self.moveTables = {}
        # Si on souhaite regénérer les tables
        if generate:
            self.generate()
        self.loadTables()
        return

    def __iter__(self):
        return iter(self.moveTables)

    def __getitem__(self, x):
        return self.moveTables[x]

    def generate(self, coords=COORDS.keys()):
        """ Génère les tables associées aux coordonnées données dans coords. """
        n = len(coords)
        for coordName in coords:
            print("Début de génération de la table {}...".format(coordName))
            m = self.computeTable(coordName)
            print("Table {} générée, début de l'enregistrement...".format(coordName))
            self.saveTable(m, coordName)
            print("Table {} enregistrée !".format(coordName))

        print("Fin de la génération des tables, {} table(s) générée(s)".format(n))

    def loadTables(self, coords=COORDS.keys()):
        """ Renvoie la liste des tables associées aux coordonnées données dans coords. """
        for coordName in coords:
            m = self.loadTable(coordName)
            self.moveTables[coordName] = m
        return

    def computeTable(self, coordName):
        """
        Crée la table des mouvements pour une coordonnée donnée.
        coordName = 'twist' | 'flip' | 'cPerm' | 'phase2ePerm' | 'UDSlice1' | 'UDSlice2'
        Pour une valeur de la coordonnée donnée, on peut obtenir la valeur
        résultante d'un mouvement avec moveTable[( valeur, move=(axe,power) )].
        """
        moveTable = dict()
        getCoord, setCoord, maxCoord, allowedMoves = COORDS[coordName]
        for valeur in range(maxCoord):
            c = Cube()
            setCoord(c, valeur)
            for (f, p) in allowedMoves:
                c.rotate([(f, p)])
                moveTable[(valeur, (f, p))] = getCoord(c)
                c.rotate([(f, 4-p)])
        return moveTable

    def saveTable(self, moveTable, coordName):
        """
        Enregistre la moveTable dans un fichier .txt pour ne pas avoir à la générer plusieurs fois.
        """
        with open("res/" + "moveTable-" + coordName + ".txt", 'w') as fichier:
            for cle, res in moveTable.items():
                valeur, (face, power) = cle
                fichier.write(
                    str(valeur) + " " + str(face) + " " + str(power) + " " + str(res) + "\n")
        return

    def loadTable(self, coordName):
        """ Renvoie la moveTable associée à la coordonnée demandée. """
        try:
            with open("res/" + "moveTable-" + coordName + ".txt", 'r') as fichier:
                lines = fichier.readlines()

            moveTable = {}
            for l in lines:
                data = l.split()
                moveTable[(int(data[0]), (data[1], int(data[2])))] = int(data[3])
        except FileNotFoundError:
            print("Le fichier moveTable-{} est introuvable.".format(coordName))
        else:
            return moveTable


######################
### Pruning Tables ###
######################


class PruningTable:
    """ Classe permettant la génération des pruning tables. """

    def __init__(self, moveTables, generate=False):
        self.moveTables = moveTables
        self.pruningTables = {}
        # Si on souhaite regénérer les tables
        if generate:
            self.generate()
        self.loadTables()
        return

    def __iter__(self):
        return iter(self.pruningTables)

    def __getitem__(self, x):
        return self.pruningTables[x]

    def generate(self, coords=PRUNING_COUPLES):
        """ Génère les pruning tables associées aux coordonnées données dans coords. """
        n = len(coords)
        for coord1, coord2, moves in coords:
            print("Début de génération de la table {}_{}...".format(coord1, coord2))
            p = self.computeTable(coord1, coord2, moves)
            print("Table {}_{} générée, début de l'enregistrement...".format(coord1, coord2))
            self.saveTable(p, coord1, coord2)
            print("Table {}_{} enregistrée !".format(coord1, coord2))

        print("Fin de la génération des tables, {} table(s) générée(s)".format(n))

    def loadTables(self, coords=PRUNING_COUPLES):
        """ Renvoie la liste des pruning tables associées aux coordonnées données dans coords. """
        for coord1, coord2, moves in coords:
            p = self.loadTable(coord1, coord2)
            self.pruningTables[(coord1, coord2)] = p
        return

    def computeTable(self, coord1, coord2, allowedMoves):
        """
        Pour chaque tuple (coordName1, coordName2), associe le nombre minimal
        de mouvements nécessaires pour annuler simultanement les deux coordonnées
        (distance = 0 dans ce cas).
        La pruningTable est une matrice telle que, pour chaque état (coord1,coord2),
        pruningtable[coord1,coord2] est la distance à l'état (0,0).
        Voici la version itérative CLAIRE (à priori).
        """
        maxCoord1, maxCoord2 = COORDS[coord1][2], COORDS[coord2][2]
        moveTable1, moveTable2 = self.moveTables[coord1], self.moveTables[coord2]
        pruningTable = np.array([[-1] * maxCoord2] * maxCoord1)
        pruningTable[0, 0] = 0
        # d est la distance par rapport à l'état (0,0).
        # n est le nombre d'états pour lesquelles la pruningTable renvoie la bonne distance.
        # Il y a en tout maxCoord1*maxCoord2 états
        d, n = 0, 1
        while n < maxCoord1 * maxCoord2:
            print('Profondeur ' + str(d) + '...' + '\n' + str(n) + ' états traités jusque là.')
            # Dans la boucle suivante, on va traiter tous les états à la distance d+1
            # de l'état (0,0), c'est-à-dire ceux accessibles à partir d'un état à distance d.
            for coord1 in range(maxCoord1):
                for coord2 in range(maxCoord2):
                    # On ne regarde que les états à distance d.
                    if pruningTable[coord1, coord2] == d:
                        # On parcourt tous les états accessibles à partir de l'état actuel.
                        for mvt in allowedMoves:
                            newCoord1 = moveTable1[(coord1, mvt)]
                            newCoord2 = moveTable2[(coord2, mvt)]
                            # On vérifie que l'état n'a pas déjà été traité
                            if pruningTable[newCoord1, newCoord2] == -1:
                                pruningTable[newCoord1, newCoord2] = d + 1
                                n += 1
            d += 1
        print(str(n) + ' états traités !')
        return pruningTable

    def saveTable(self, pruningTable, coord1, coord2):
        """
        Enregistre la moveTable dans un fichier .txt pour ne pas avoir à la générer plusieurs fois.
        """
        with open("res/" + "pruningTable-" + coord1 + "_" + coord2 + ".txt", 'w') as fichier:
            maxCoord1, maxCoord2 = len(pruningTable), len(pruningTable[0])
            fichier.write(str(maxCoord1) + " " + str(maxCoord2) + "\n")
            for i in range(maxCoord1):
                for j in range(maxCoord2):
                    fichier.write(str(i) + " " + str(j) + " " + str(pruningTable[i, j]) + "\n")
        return

    def loadTable(self, coord1, coord2):
        try:
            with open("res/" + "pruningTable-" + coord1 + "_" + coord2 + ".txt", 'r') as fichier:
                lines = fichier.readlines()
            size = lines.pop(0)
            n, p = int(size.split()[0]), int(size.split()[1])
            pruningTable = np.array([[-1] * p] * n)
            for l in lines:
                data = l.split()
                pruningTable[int(data[0]), int(data[1])] = int(data[2])
        except FileNotFoundError:
            print("Le fichier pruningTable-{}_{} est introuvable.".format(coord1, coord2))
        else:
            return pruningTable
