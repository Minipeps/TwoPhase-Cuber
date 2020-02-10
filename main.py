# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 19:50:28 2015

@author: Maxime
"""

from data import *
import renderer as r
from fenetre import Fenetre
from cubeCoord import Cube
from twoPhase import Solver
import traceback
from copy import copy


def test(cubeDisplay):
    """ test de l'affichage 3D """

    fenetre = Fenetre(1280, 720, fullscreen=False, maxfps=144)
    fenetre.ajoutEvenementsRotation(cubeDisplay)
    running = True
    end = False
    cubeSolver = copy(cubeDisplay)
    while running:
        try:
            fenetre.prepare()
            # Ce qu'on veut afficher :
            r.render(cubeDisplay)
            if not end:  # Fonctions à n'executer qu'une fois
                print("Mélange du cube...")
                cubeDisplay.animation(fenetre, cubeSolver.melanger())
                print()
                s = Solver(cubeSolver)
                print("Début phase 1 : {}".format(s.getPhase1Solution()))
                cubeDisplay.animation(fenetre, s.getPhase1Solution())
                print()
                print("Début phase 2 : {}".format(s.getPhase2Solution()))
                cubeDisplay.animation(fenetre, s.getPhase2Solution())
                print()
                print("{} mouvements.".format(len(s.getSolution())))
                end = True
            # Fin de ce qu'on veut afficher
            fenetre.update()
        except:
            #traceback.print_exc()
            running = False

    fenetre.quitter()
    return

test(Cube())
