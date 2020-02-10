# -*- coding: utf-8 -*-
"""
Created on Wed May 11 14:11:24 2016

@author: Maxime
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm


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


def stats(data):
    n = len(data)
    mu, std = norm.fit(data)
            
    X = np.linspace(min(data), max(data), n)
    Y = norm.pdf(X, mu, std) * n
    plt.hist(data, bins = n)
    #plt.plot(X,Y, label = "$\mu={}$\n$\sigma={}$\n$min = {}$\n$max = {}$".format(int(mu),int(std*10)/10, min(data), max(data)))
    plt.legend(loc = 'upper right')
    plt.xlabel("Temps d'exécution en secondes")
    plt.ylabel("Fréquence * {}".format(n))
    plt.title("Histogramme du temps d'exécution sur {} résolutions ".format(n))
    
    plt.show()

temps, nb_mvts = statsRead(1000)
stats(temps)