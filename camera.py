# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 17:28:01 2015

@author: Maxime
"""

from OpenGL.GL import *
from OpenGL.GLU import *


class Camera:
    """
    Cette classe permettra de contrôler le point de vue du cube à tout
    moment de l'affichage 3D
    """

    def __init__(self):
        """ Fonction appelée lors de la création de la caméra """
        self.x, self.y, self.z = 0, 0, 0
        self.rotX, self.rotY, self.rotZ = 0, 0, 0
        return

    def getPosition(self):
        return(self.x, self.y, self.z)

    def getRotation(self):
        return(self.rotX, self.rotY, self.rotZ)

    def increasePosition(self, dx, dy, dz):
        """
        Déplace la caméra par translation, en réalité on translate l'espace
        dans le sens opposé pour donner l'impression de mouvement
        """
        self.x -= dx
        self.y -= dy
        self.z -= dz
        return

    def increaseRotation(self, dPitch, dYaw, dRoll):
        """ Pivote la caméra par rotation suivant les angles d'Euler (en degrés) """
        self.rotX -= dPitch
        self.rotY -= dYaw
        self.rotZ -= dRoll
        return

    def move(self):
        glTranslatef(self.x, self.y, self.z)
        return

    def rotate(self):
        glRotatef(self.rotX, 1, 0, 0)
        glRotatef(self.rotY, 0, 1, 0)
        glRotatef(self.rotZ, 0, 0, 1)
        return

    def update(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.move()
        self.rotate()
        return
