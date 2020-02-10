# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 22:33:19 2015

@author: Maxime
"""

from camera import Camera

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluBuild2DMipmaps
import os


class Fenetre:

    def __init__(self, width=0, height=0, fullscreen=False, maxfps=200):
        """ Ouverture de la fenêtre """
        self.maxfps = maxfps
        self.camera = Camera()
        self.evenements = {}
        self.setupEvenements()
        self.clock = pygame.time.Clock()

        self.horizRotation = 0
        self.vertRotation = 0

        pygame.display.init()
        if (width, height) == (0, 0):
            self.display = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        else:
            self.display = (width, height)
        if fullscreen:
            pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL | FULLSCREEN)
        else:
            pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Cube 3D")
        pygame.mouse.set_visible(True)

        glMatrixMode(GL_PROJECTION)
        glClearColor(1., 1., 1., 1.0)
        glLoadIdentity()
        gluPerspective(50, (self.display[0] / self.display[1]), 0.1, 50.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.camera.increasePosition(0, 0, 12)
        self.camera.increaseRotation(-30, -30, 0)
        self.camera.update()

        glEnable(GL_DEPTH_TEST)

        self.loadTexture("facette.bmp")
        return

    def loadTexture(self, nomFichier):
        """ Charge la texture de la facette """
        # On charge l'image dans pygame
        textureSurface = pygame.image.load(os.path.join('res', nomFichier))
        textureData = pygame.image.tostring(textureSurface, "RGBA", True)
        # Puis on l'associe à la texture dans OpenGL
        self.texID = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texID)
        gluBuild2DMipmaps(GL_TEXTURE_2D, 4, textureSurface.get_width(),
                          textureSurface.get_height(), GL_BGRA, GL_UNSIGNED_BYTE, textureData)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        return

    def prepare(self):
        """ Prépare la fenêtre pour afficher le cube """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.gestionEvenements()
        self.gestionCamera()
        return

    def update(self):
        """ Met à jour l'affichage """
        pygame.display.flip()
        self.clock.tick(self.maxfps)
        pygame.display.set_caption("Cube 3D (FPS = " + str(int(self.clock.get_fps())) + ")")
        return

    def quitter(self):
        """ Ferme proprement la fenêtre et quitte le programme """
        pygame.quit()
        return

    def setupEvenements(self):
        """ Crée la liste des évènements par défaut """
        self.ajoutEvenement(KEYDOWN, K_ESCAPE, self.quitter)
        self.ajoutEvenement(KEYDOWN, K_LEFT, self.setHorizRotation, 1)
        self.ajoutEvenement(KEYDOWN, K_RIGHT, self.setHorizRotation, -1)
        self.ajoutEvenement(KEYDOWN, K_UP, self.setVertRotation, 1)
        self.ajoutEvenement(KEYDOWN, K_DOWN, self.setVertRotation, -1)

        self.ajoutEvenement(KEYUP, K_LEFT, self.setHorizRotation, -1)
        self.ajoutEvenement(KEYUP, K_RIGHT, self.setHorizRotation, 1)
        self.ajoutEvenement(KEYUP, K_UP, self.setVertRotation, -1)
        self.ajoutEvenement(KEYUP, K_DOWN, self.setVertRotation, 1)
        return

    def ajoutEvenementsRotation(self, cube):
        """ Permet de manipuler le cube directement pendant l'affichage """
        self.ajoutEvenement(KEYDOWN, K_u, cube.animation, self, [('U', 1)])
        self.ajoutEvenement(KEYDOWN, K_d, cube.animation, self, [('D', 1)])
        self.ajoutEvenement(KEYDOWN, K_r, cube.animation, self, [('R', 1)])
        self.ajoutEvenement(KEYDOWN, K_l, cube.animation, self, [('L', 1)])
        self.ajoutEvenement(KEYDOWN, K_f, cube.animation, self, [('F', 1)])
        self.ajoutEvenement(KEYDOWN, K_b, cube.animation, self, [('B', 1)])
        return

    def gestionEvenements(self):
        """ Gère l'interaction avec l'utilisateur """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quitter()
            elif event.type in (KEYDOWN, KEYUP):
                try:
                    f, args = self.evenements[(event.type, event.key)]
                except KeyError:
                    lamdba=0
                else:
                    f(*args)
        return

    def ajoutEvenement(self, eventType, key, f, *args):
        """
        Permet d'assigner une fonction à une touche du clavier,
        si la fonction admet des arguments ils doivent être transmis après.
        """
        self.evenements[(eventType, key)] = (f, args)
        return

    def setHorizRotation(self, value):
        self.horizRotation += value
        return

    def setVertRotation(self, value):
        self.vertRotation += value
        return

    def gestionCamera(self):
        """ Déplace la caméra """
        self.camera.increaseRotation(self.vertRotation, self.horizRotation, 0)
        self.camera.update()
        return
