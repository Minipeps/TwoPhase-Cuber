# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 23:53:41 2016

@author: victor
"""

from cv2 import *
from numpy import min
from data import *

# Couleurs en GBR
BLEU = (255, 0, 0)
ROUGE = (0, 0, 255)
BLANC = (255, 255, 255)
JAUNE = (0, 255, 255)
VERT = (8, 79, 27)
ORANGE = (0, 127, 255)
NOIR = (0, 0, 0)
# j'ai changé l'ordre, efface ce commentaire si ça ne dérange pas
couleursCube = [BLEU, BLANC, VERT, JAUNE, ROUGE, ORANGE]
color_list = [(BLEU, BLANC), (BLANC, VERT), (VERT, JAUNE),
              (JAUNE, BLEU), (ROUGE, BLEU), (ORANGE, BLEU)]
color_list_name = [('Bleu', 'Blanc'), ('Blanc', 'Vert'), ('Vert', 'Jaune'),
                   ('Jaune', 'Bleu'), ('Rouge', 'Bleu'), ('Orange', 'Bleu')]


def myadd(xs, ys):
    """addition des tuples"""
    return tuple(int(x + y) for x, y in zip(xs, ys))


def capture():
    "lance la capture vidéo, suivre les instructions à l'écran"
    cap = VideoCapture(0)
    save = []
    State = False  # Tracker pour les captures d'images
    # nombre de pixels sur les lignes et les colonnes
    ligne, colonne = int(cap.get(3)), int(cap.get(4))
    compteur = 0  # Tracker pour les captures d'images
    centre = (ligne // 2, colonne // 2)  # centre de l'image
    dp = ligne // 25  # zone sure

    dist = ligne // 9
    # pour tracer les lignes, coins en haut à gauche
    base = (ligne * 3 / 9, (colonne - ligne * 3 // 9) // 2)

    def trace(text, color, proportion=(50, 50), scale=1, font=FONT_HERSHEY_COMPLEX, thickness=2):
        """
        Permet d'écrire du texte à l'écran.
        Les proportions sont (0,0) en haut à gauche, (100,100) en bas à droite.
        """
        textSize = getTextSize(text, font, scale, 0)
        textOrg = (int((ligne - textSize[0][0]) * proportion[0] / 100),
                   int((colonne - textSize[0][1]) * proportion[1] /
                       100 + textSize[0][1] * (100 - proportion[1] / 100) / 100))
        putText(img, text, textOrg, font, scale, color, thickness, 8)
        return None

    while(True):
        # lecture image par image
        ret, frame = cap.read()

        # Opération sur les images
        img = flip(frame, 1)

        # affichage des lignes
        if State:
            trace("Appuyez sur espace pour continuer", NOIR, scale=1, thickness=3)
        else:
            for i in range(4):
                line(img, myadd(base, (dist * i, 0)),
                     myadd(base, (dist * i, dist * 3)), NOIR, thickness=2)
                line(img, myadd(base, (0, dist * i)),
                     myadd(base, (dist * 3, dist * i)), NOIR, thickness=2)
            rectangle(img, myadd(base, (dist, dist)), myadd(
                base, (dist * 2, dist * 2)), color_list[compteur][0], thickness=2)
            trace("Appuyez sur 'p' pour capturer", color_list[
                  compteur][0], proportion=(50, 90), thickness=1)
            trace(color_list_name[compteur][1] + " en haut",
                  color_list[compteur][1], proportion=(50, 14), thickness=1)

            # Trace les couleurs scannées temporaires
            for i in range(-1, 2):
                for j in range(-1, 2):
                    coord = myadd(centre, (i * dist, j * dist))
                    couleur = cal_couleur(img, coord, dp)
                    couleurCube = couleurProche(couleur)
                    rectangle(
                        img, myadd(coord, (-dp, -dp)),
                        myadd(coord, (dp, dp)),
                        couleurCube, thickness=1
                    )

        touch = waitKey(1)
        if touch == 27 or compteur == 6:
            break
        elif touch == ord('p') and not State:
            State = not State
            compteur += 1
            save.append(frame)
        elif touch == ord(' ') and State:
            State = not State
        # affichage de l'image résultante
        imshow('continu', img)

    # The End.
    cap.release()
    destroyWindow('continu')
    return save, centre, dist, dp


def cal_couleur(img, coord, dp):
    """
    Renvoie la couleur moyenne de la surface délimitée par
    centre - dp et centre + dp.
    """
    lenpixel = (2 * dp)  # nombre de pixels d'une ligne/colonne dans la zone de sureté
    pixels = img[coord[1] - dp:coord[1] + dp, coord[0] - dp:coord[0] + dp]  # ordre inversé
    # On calcule la valeur moyenne de la couleur des pixels
    Bvalue, Gvalue, Rvalue = 0, 0, 0
    for i in range(lenpixel):
        for j in range(lenpixel):
            Bvalue += int(pixels[i, j, 0])  # int indispensable
            Gvalue += int(pixels[i, j, 1])
            Rvalue += int(pixels[i, j, 2])
    couleurCentre = (Bvalue // (lenpixel**2), Gvalue // (lenpixel**2), Rvalue // (lenpixel**2))
    return couleurCentre


def distance(x, y):
    """Calcule la distance (au carré) entre 2 triplets """
    return sum(map(int.__pow__, map(int.__sub__, x, y), [2] * 3))


def couleurProche(couleur, ref=couleursCube):
    """
    Retourne l'indice de la couleur la plus proche parmi la liste ref,
    en utilisant la fonction distance.
    """
    l = [distance(couleur, refCouleur) for refCouleur in ref]
    dmin = min(l)
    return l.index(dmin)


def scan_cube():
    """Retourne la liste des couleurs reconnues, selon ."""
    pict, centre, dist, dp = capture()
    # pict liste les images sans miroir, dist entre 2 centre, dp la zone sûre
    l_couleurs = [cal_couleur(pict[i], centre, dp) for i in range(6)]
    print(l_couleurs)
    res = []
    for img_i in range(6):
        res.append([])
        for i in range(-1, 2):
            for j in range(-1, 2):
                coord = myadd(centre, (j * dist, i * dist))
                couleur = cal_couleur(pict[img_i], coord, dp)
                couleurCube = color_list_name[couleurProche(couleur, l_couleurs)][0]
                res[img_i].append(couleurCube)
    return(res)

capture()
