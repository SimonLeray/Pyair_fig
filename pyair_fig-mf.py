#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#Nom :  : script-fig.py
#Description    : Génération de figures météo standardisées
#Copyright  : 2015, LIMAIR
#Auteur     :  Simon Leray

import matplotlib as mpl
mpl.use('Agg')
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib import pyplot as plt
import numpy as np
import scipy as sp
import pandas as pd
import mx.DateTime as mxDT
from pyair import meteo_france
mf = meteo_france.METEO_FRANCE()


###################     Données d'entrées    ######################

# Variables  T, U et RR1 extraites de la base méteo france 
station = 'LIMOGES-BELLEGARDE'
parametres = ['T']  # variables(s) à tracer : T, U, RR1

# Période
debut = '2015-06-28'
fin = '2015-06-30'

# Activation du cumul des précipitations (True/False)
cumul_precip = False

# Statistiques : moy, [min, max] (True/False)
stat = False

#Paramètres figure
figname    = 'limoges'
size     = 'L'    # L : Large , S : Small
MARKERSIZE = 2    # Taille des points
COL        = 3    # Nombre de colonne dans la légende


#################  Paramétrage de Matplotlib   ####################

NOMS = {
    "T": u"Température (°C)",
    "U":u"Humidité relative (%)",
    "RR1":u"Hauteur de précipitations (mm)",
    "cumul":u"Cumul de précipitations (mm)"}

COULEURS = {"T"    : '#ff0000',  #Rouge : C0 M100 J100 N0
            "RR1"  : '#0033ff',  #Bleu foncé : C100 M80 J0 N0
            "U"    : '#00ff00',  #Vert foncé : C1000 M0 J100 N0
            "cumul": '#00ffff'}  #Marron : C0 M70 J100 N50

SIZE = {'L':(6.2992, 3.5433),'S':(6.2992/2, 3.5433/1.5)} #  L (16cm,9cm) 
AXE  = {'L':[0.12, 0.2, 0.85, 0.62],'S':[0.12, 0.25, 0.85, 0.54]} #  L [Xmin, Ymin, Xmax, Ymax] 

FIGSIZE       = SIZE[size]
DPI           = 300
BOXLINESIZE   = 0.5
LINEWIDTH     = 0.3
XFONTSIZE     = {'L':5.8,'S':4.8}
UNITSIZE      = {'L':6.4,'S':6.4}
LEGFONTSIZE   = {'L':5.5,'S':4.5}
LEGMARKERSIZE = 0.78

mpl.rcParams['axes.formatter.use_locale'] = True
mpl.rcParams['xtick.labelsize']           = XFONTSIZE[size]
mpl.rcParams['xtick.direction']           = 'in'
mpl.rcParams['ytick.labelsize']           = XFONTSIZE[size]
mpl.rcParams['ytick.direction']           = 'in'
mpl.rcParams['axes.linewidth']            = 0.5
mpl.rcParams['axes.axisbelow']            = True
mpl.rcParams['legend.fontsize']           = 'x-small'
mpl.rcParams['legend.borderpad']          = 0.5        # border whitspace in fontsize units
mpl.rcParams['legend.markerscale']        = 1.5        # the relative size of legend markers vs. original
mpl.rcParams['legend.numpoints']          = 2          # the number of point in the legend for lines
mpl.rcParams['legend.handlelength']       = 2          # the length of the legend lines
mpl.rcParams['legend.labelspacing']       = 0.010      # the vertical space between the legend entries
mpl.rcParams['legend.handletextpad']      = 0.60       # the space between the legend line and legend text
mpl.rcParams['legend.borderaxespad']      = 0.02       # the border between the axes and legend edge
mpl.rcParams['legend.shadow']             = False

#################       Création Figure        ####################

def new_fig():
    fig = plt.figure(num = None,
                    figsize   = FIGSIZE, 
                    dpi       = DPI,
                    facecolor = 'w',
                    edgecolor = 'w')
    ax  = fig.add_axes(AXE[size])
    ax.set_axis_bgcolor('white')

    #Décollement des axes
    ax.spines['left'].set_position(('axes',-0.04))
    ax.spines['bottom'].set_position(('axes',-0.07))
    ax.spines['bottom'].set_color('black')
    ax.spines['top'].set_color('white')
    ax.spines['right'].set_color('white')
    ax.spines['left'].set_color('black')
    ax.spines['bottom'].set_visible(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.tick_params(direction = 'out',
                   length      = 6,
                   color       = 'black',
                   which       = 'both',
                   bottom      = True,
                   top         = False,
                   right       = False,
                   left        = True,
                   labelbottom = True,
                   labeltop    = False,
                   labelright  = False,
                   labelleft   = True)
    return fig, ax

##################           MAIN            ######################

# Extraction des donnees méteo
df = mf.get_mesures(station,
                    parametres = parametres,
                    debut = debut,
                    fin = fin)
df = df.resample('H', how = 'mean')

if cumul_precip == True:
    df['cumul']=np.cumsum(df['RR1'])

# Statistiques
if stat == True:
	print 'moyenne\n', df.mean(),'\n'
	print 'max\n', df.max(),'\n'
	print 'min\n', df.min(),'\n'
	if 'RR1' in parametres:
	    print 'cumul de précipitations :\n', df['RR1'].sum()

# Init
fig, ax = new_fig()
tmp     = pd.DataFrame()  # tampon pour le calcul du max(échelle)

for parametre, data in df.iterkv():
    label   = NOMS[parametre] + ' / ' + station
    data.plot(ax = ax, 
            label           = label,
            color           = COULEURS[parametre],
            linestyle       = '-',
            linewidth       = LINEWIDTH,
            marker          = 'o',
            markeredgewidth = 0,
            markersize      = MARKERSIZE,
            clip_on         = False)

    #Sauvegarde pour calculer le max de l'échelle de concentration
    tmp = tmp.append(df[parametre]) 

# Echelle
min = tmp.min().min()
if min < -5:
    ax.set_ylim(ymin = -10)
elif min < 0:
    ax.set_ylim(ymin = -5) 
else:
    ax.set_ylim(ymin = 0)

max = tmp.max().max()
if max <= 300:
    maxi = 300
if max <= 200:
    maxi = 200
if max <= 100:
    maxi = 100
if max <= 50:
    maxi = 50
if max <= 30:
    maxi = 30 
if max <= 10:
    maxi = 10
if max <= 1:
    maxi = 1
ax.set_ylim(ymax = maxi)

# Grille
ax.xaxis.grid(False, which = 'both')
ax.yaxis.grid(True, which = 'both', color = 'darkgrey')
ax.set_xlabel('')
ax.set_ylabel('')

# Taille axes
for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(XFONTSIZE[size])
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(XFONTSIZE[size])

# Légende
leg = plt.legend(bbox_to_anchor = (-0.075, 1.08, 1., .10),
                loc  = 3,
                ncol = COL,
                mode = None,
               fontsize = LEGFONTSIZE[size])
leg.draw_frame(False)

# Cloture
fig.savefig('../Figures/' + figname, dpi = DPI)
plt.clf()