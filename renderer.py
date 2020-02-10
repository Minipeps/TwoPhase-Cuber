# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 19:27:47 2015

@author: Maxime
"""

from data import *

from OpenGL.GL import *

##########################
### Fonctions de rendu ###
##########################

### Fonctions d'affichage basique ###


def repere(echelle=1):
    """ Affiche le repère orthonormé direct """

    glPushMatrix()
    glDisable(GL_TEXTURE_2D)
    glScale(echelle, echelle, echelle)
    glBegin(GL_LINES)
    # Axe X
    glColor(BLEU)
    glVertex3i(0, 0, 0)
    glVertex3i(1, 0, 0)
    # Axe Y
    glColor(ROUGE)
    glVertex3i(0, 0, 0)
    glVertex3i(0, 1, 0)
    # Axe Z
    glColor(VERT)
    glVertex3i(0, 0, 0)
    glVertex3i(0, 0, 1)
    glEnd()
    glEnable(GL_TEXTURE_2D)
    glPopMatrix()
    return


def r_surface(points, couleur):
    """
    Affiche une surface de la couleur spécifiée
    (avec la texture préchargée dans la fenêtre)
    """
    glEnable(GL_TEXTURE_2D)
    if couleur is not None:
        glColor3fv(couleur)
        glBegin(GL_QUADS)
        for i in range(4):
            glTexCoord2iv(texMap[i])
            glVertex3fv(points[i])
        glEnd()
    glDisable(GL_TEXTURE_2D)
    return


def r_cube(couleurs, echelle=1):
    """
    Affiche un cube dont les faces ont des couleurs différentes.
    Ordre des couleurs : U, D, R, F, L, B
    """
    if echelle == 1:
        liste_sommets = s
    else:
        liste_sommets = sommets(float(echelle))
    for i in range(6):
        points = [liste_sommets[j] for j in indices[i]]
        r_surface(points, couleurs[i])
    return

### Fonction d'affichage des pièces ###


def getOrientationParam(piece, position, orientation):
    if len(piece) == 2:
        rotX, rotY, rotZ = table_axeOrientation_aretes[position]
        theta = 180 * orientation
    elif len(piece) == 3:
        rotX, rotY, rotZ = table_axeOrientation_coins[position]
        theta = -120 * orientation
    else:
        rotX, rotY, rotZ, theta = 0, 0, 0, 0
    return rotX, rotY, rotZ, theta


def render_piece(piece, position, orientation):
    """
    Affiche les facettes de la pièce et la positionne dans l'espace relativement
    au centre du cube.
    @param piece : Donne la chaîne de charactère correspondant à la position
                   de la pièce dans un cube terminé
    @param position : entier entre 0 et 5 pour un centre, 0 et 7 pour un coin
                      et 0 et 11 pour une arête
    @param orientation : entier dans {0,1,2} pour un coin, {0,1} pour une arête
    """
    # Couleurs setup
    c = [liste_couleurs[liste_centres.index(e)] for e in piece]
    couleurs = [None] * 6
    # On récupère la position/orientation de la pièce par rapport au repère
    rotX, rotY, rotZ, theta = getOrientationParam(piece, position, orientation)
    # Centre
    if len(piece) == 1:
        dX, dY, dZ = table_positions_centres[position]

        for i in table_couleurs_centres[position]:
            couleurs[i] = c.pop(0)
    # Arête
    elif len(piece) == 2:
        dX, dY, dZ = table_positions_aretes[position]

        for i in table_couleurs_aretes[position]:
            couleurs[i] = c.pop(0)
    # Coin
    elif len(piece) == 3:
        dX, dY, dZ = table_positions_coins[position]

        for i in table_couleurs_coins[position]:
            couleurs[i] = c.pop(0)
    # Autre ???
    else:
        raise ValueError("Pièce inconnue !")

    # Let's OpenGL it !
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    # On positionne d'abord le repère
    glRotatef(theta, rotX, rotY, rotZ)
    glTranslatef(dX, dY, dZ)
    # Puis on affiche la pièce
    r_cube(couleurs)
    glPopMatrix()
    return

### Fonctions d'affichage du cube ###


def getMovingPieces(cube, face):
    """
    Renvoie les liste des pièces affectées et des pièces non affectées
    par la rotation 'face'.
    """
    movingPieces, nonMovingPieces = [], []
    cornerP = cube.cornerPermutation
    cornerO = cube.cornersOrientations
    edgeP = cube.edgePermutation
    edgeO = cube.edgesOrientations
    # On compare les permutations de rotation de face avec les identités
    # pour récupérer les coins et arêtes affectées
    # Centres
    for i in range(6):
        if face == liste_centres[i]:
            movingPieces.append((liste_centres[i], i, 0))
        else:
            nonMovingPieces.append((liste_centres[i], i, 0))
    # Coins
    for i in range(8):
        if permutations_coins[face][i] != i:
            # On récupère les coins qui sont affectés
            movingPieces.append((liste_coins[cornerP[i]], i, cornerO[i]))
        else:
            # On récupère les coins qui ne sont pas affectés
            nonMovingPieces.append((liste_coins[cornerP[i]], i, cornerO[i]))
    # Arêtes
    for i in range(12):
        if permutations_aretes[face][i] != i:
            # On récupère les arêtes qui sont affectées
            movingPieces.append((liste_aretes[edgeP[i]], i, edgeO[i]))
        else:
            # On récupère les arêtes qui ne sont pas affectées
            nonMovingPieces.append((liste_aretes[edgeP[i]], i, edgeO[i]))
    return movingPieces, nonMovingPieces


def getRotationParam(face, power):
    """ Renvoie le vecteur directeur de la rotation """
    axe = tuple(map(lambda x: -x, axe_rotation[face])) if power == 3 else axe_rotation[face]
    thetaMax = 181 if power == 2 else 91
    return axe, thetaMax


def render(cube):
    """ Rendu du cube en 3D """
    cornerP = cube.cornerPermutation
    cornerO = cube.cornersOrientations
    edgeP = cube.edgePermutation
    edgeO = cube.edgesOrientations
    # Centres
    for i in range(6):
        render_piece(liste_centres[i], i, 0)
    # Arêtes
    for i in range(12):
        render_piece(liste_aretes[edgeP[i]], i, edgeO[i])
    # Coins
    for i in range(8):
        render_piece(liste_coins[cornerP[i]], i, cornerO[i])
    return

### Fonctions d'animation des mouvements ###


def animRotation(fenetre, cube, face, power):
    """ Affiche le cube pendant le mouvement (face, power) """
    movingPieces, nonMovingPieces = getMovingPieces(cube, face)
    axe, thetaMax = getRotationParam(face, power)
    # On récupère les coords de la surface à tracer pour cacher l'intérieur du cube
    hidingPoints = hide_coords[face]
    # Theta est l'angle de rotation variant entre 1 et 90 degrés
    for theta in range(1, thetaMax, 3):   # vitesse (theta)
        fenetre.prepare()

        glMatrixMode(GL_MODELVIEW)
        # On affiche les pieces affectées en les pivotant
        glPushMatrix()
        glRotatef(theta, axe[0], axe[1], axe[2])
        for i in range(9):
            piece, pos, ori = movingPieces[i]
            render_piece(piece, pos, ori)
        r_surface(hidingPoints, NOIR)
        glPopMatrix()
        # Puis on affiche les pièces immobiles
        for i in range(17):
            piece, pos, ori = nonMovingPieces[i]
            render_piece(piece, pos, ori)
        r_surface(hidingPoints, NOIR)

        fenetre.update()
    return
