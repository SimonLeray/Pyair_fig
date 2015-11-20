#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#Nom :  : script-fig.py
#Description    : Génération de figures standardisées
#Copyright  : 2015, LIMAIR
#Auteur     :  Simon Leray

import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
import scipy as sp
import pandas as pd
from pyair import reg
from pyair import xair

xr = xair.XAIR(user='RSDBA', pwd='RSDBA', adr='172.16.45.33')

###################################################################

"""Définition des polluants - Mesures automatiques (analyseurs)"""
class Polluant():
    def __init__(self, nom, freq):
        self.nom    = nom
        self.freq = freq
    def get_nom(self):
        return self.nom
    def get_freq(self):
        return self.freq

NO2    = Polluant('NO2','H')
O3     = Polluant('O3','H')
SO2    = Polluant('SO2','H')
PM10   = Polluant('PM10','H')
PM10NC = Polluant('PM10NC','H')
PM25   = Polluant('PM25','H')
CO     = Polluant('CO','H')
TRS    = Polluant('TRS','H')
H2S    = Polluant('H2S','15T')

"""Seuils d'alerte NO2, SO2, O3 et PM10 et Valeurs réglementaires"""
MVR     = {'NO2':135, 'SO2':200, 'O3':150, 'PM10':-999, 'PM10NC':-999}
IR      = {'NO2':200, 'SO2':300, 'O3':180, 'PM10':50,   'PM10NC':50}
A       = {'NO2':400, 'SO2':500, 'O3':240, 'PM10':80,   'PM10NC':80}
VL      = {'NO2':40,'O3':120,'PM10':40,'PM25':25,'CO':10}
OQ      = {'NO2':40,'PM10':30,'PM25':10,}
OMS     = {'NO2':40,'O3':100,'PM10':20,'PM25':10,'H2S':7}


###################     Données d'entrées    ######################


# Liste des polluants demandés [(famille, polluant)]
# Exemple : [(NO2,('NO2_AIN','NO2_FON')),(TRS,'TRS_IPA')]
""" ATTENTION : vérif. si STATION de mesure dans le dict NOMS """

pol = xr.liste_mesures(reseau='OZONE').MESURE
polluants = [(O3,pol)]
#polluants = [(PM10,('PM10_PRE','PM10_HUG','PM10_FON','PM10_NIC','PM10_GAR','PM10_DAL','PM10_AIN','PM10_IPA'))]
#polluants = [(SO2,('SO2_IPA','SO2_GAR'))]

# Période, fréquence 
debut = '2015-07-01'
fin   = '2015-07-31'
frequence = 'H'   # H,D,M,A
mes_valides = 0.75  # Critère : 75 % de mesures valide pour moyenner

# Activation de la moyenne glissante, max journalier (True/False)
GLISSANT       = True
sur            = 8        # X unités (QH, H, M, A) 
MAX_JOURNALIER = True
MAX_ANNUEL     = False

# Activation des seuils d'alerte et valeurs réglementaires (True/False)
ALERTE     = False
Valeur_lim = True
Obj_qual   = False
Oms        = False

#Paramètres figure
figname    = 'O3juillet2015'
size       = 'L'    # L : Large , S : Small
MARKERSIZE = 2      # Taille des points
COL        = 2      # Nombre de colonne dans la légende
maxi       = None   # max de l'échelle, optionnel. Si = None, calculé auto

#Statistiques : moy, [min - max] (True/False)
stat = False


#################  Paramétrage de Matplotlib   ####################

# Nom : colonne STATION disponible avec xr.liste_stations
NOMS = {
    "AINE": u"Limoges / Place d'Aine",
    "PRESID": u"Limoges / Présidial",
    "MADOUM": "Limoges / Madoumier",
    "GARROS": "Limoges / Palais sur Vienne",
    "DALTON": "Brive la Gaillarde / Dalton",
    "NICOLA": u"Guéret / Nicolas",
    "HUGO": "Tulle / Hugo",
    "VICTOR": "Tulle / Victor",
    "FONTAI": "Saint Junien / Fontaine",
    "IPAPER": "Saillat sur Vienne / IPaper",
    "MERA": u"La Nouaille / MERA",
    "RIVAILLES": u"Limoges / Palais sur Vienne",
    "ALVEOL2015":u"Alvéol / Le Vignaud",
    "O3": r'$\rm{O_3}$',
    "NO2": r'$\rm{NO_2}$',
    "PM10": r"$\rm{PM10}$", #" - AVEC fraction semi-volatile",
    "PM10NC": r"$\rm{PM10}$ - SANS fraction semi-volatile",
    "PM25": r"$\rm{PM2.5}$",
    "SO2": r'$\rm{SO_2}$',
    "H2S": r'$\rm{H_2S}$',
    "CO": "CO",
    "TRS":"TRS"}

SEUILS  =  {'MVR':u"Seuil de mise en vigilance régionale",
            'IR' :u"Seuil d'information et de recommandations",
            'A'  :u"Seuil d'alerte",
            'OMS':u'Seuil de gêne olfactive (OMS) sur 30 min',
            'VC' :u'Valeur cible annuelle',
            'VL' :u'Valeur limite annuelle',
            'OQ' :u'Objectif de qualité annuel',
            'OMS':u'Valeur guide OMS'}

COULEURS        = ['#ff0000',  #Rouge : C0 M100 J100 N0
                   '#00ff00',  #Vert foncé : C1000 M0 J100 N0
                   '#0033ff',  #Bleu foncé : C100 M80 J0 N0
                   '#802600',  #Marron : C0 M70 J100 N50
                   '#ff80ff',  #Rose clair : C0 M50 J0 N0
                   '#ff8000',  #Orange : C0 M50 J100 No
                   '#00ffff',  #Cyan : C100
                   '#808080']  #Gris : Noir50

COULEURS_VR = {'MVR':'#ff0000',  #Rouge
               'IR' :'#cc0000',  #Strong red +
               'A'  :'#6a0000',  #Very dark red
               'VL' :'#ffa500',  #Orange
               'OQ' :'#cc0000',  #Strong red
               'OMS':'#800000',  #Marron  
               'VTR':'#ff0000'}  #Strong red

SIZE = {'L':(6.2992, 3.5433),'S':(6.2992/2, 3.5433/1.5)} #  L (16cm,9cm) 
AXE  = {'L':[0.12, 0.2, 0.85, 0.62],'S':[0.12, 0.24, 0.85, 0.54]} #  L [Xmin, Ymin, Xmax, Ymax] 

FIGSIZE       = SIZE[size]
DPI           = 300
LINEWIDTH     = 0.3
XFONTSIZE     = {'L':5.8,'S':5.8}
UNITSIZE      = {'L':6.4,'S':6.4}
LEGFONTSIZE   = {'L':5.5,'S':3.5}
LEGMARKERSIZE = 0.78

mpl.rcParams['axes.formatter.use_locale'] = True
mpl.rcParams['xtick.labelsize']           = XFONTSIZE[size]
mpl.rcParams['xtick.direction']           = 'in'
mpl.rcParams['ytick.labelsize']           = XFONTSIZE[size]
mpl.rcParams['ytick.direction']           = 'in'
mpl.rcParams['axes.linewidth']            = 0.5
mpl.rcParams['axes.axisbelow']            = True
mpl.rcParams['legend.fontsize']           = 'x-small'
mpl.rcParams['legend.borderpad']          = 0.5  # border whitspace in fontsize units
mpl.rcParams['legend.markerscale']        = 1  # the relative size of legend markers vs. original
mpl.rcParams['legend.numpoints']          = 2 # the number of point in the legend for lines
mpl.rcParams['legend.handlelength']       = 2  # the length of the legend lines
mpl.rcParams['legend.labelspacing']       = 0.010  # the vertical space between the legend entries
mpl.rcParams['legend.handletextpad']      = 0.60  # the space between the legend line and legend text
mpl.rcParams['legend.borderaxespad']      = 0.02  # the border between the axes and legend edge
mpl.rcParams['legend.shadow']             = False

#################       Création Figure        ####################

def new_fig():
    fig = plt.figure(num = None,
                    figsize   = FIGSIZE, 
                    dpi       = DPI,
                    facecolor = 'w',
                    edgecolor = 'w')
    ax  = fig.add_axes(AXE[size])
    ax.set_color_cycle(COULEURS)
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

##################          MAIN             ######################

# init
fig, ax = new_fig()
tmp     = pd.DataFrame()  # tampon pour le calcul du max(échelle)

# Boucle de calcul
#i=0
for famille, polluant in polluants:
    nom  = famille.get_nom()
    freq = famille.get_freq()
    df   = xr.get_mesures(mes = polluant, debut = debut, fin = fin, freq = freq)
    df   = df.resample(frequence)
    
    # Moyenne glissante et max journalier
    if GLISSANT == True:
        df = reg.moyennes_glissantes(df,sur = sur)
    if MAX_JOURNALIER == True:
        df = df.resample('D',how = 'max')
    if MAX_ANNUEL == True:
        df = df.resample('A',how = 'max')

    # Pour les PM10 avec et sans fraction semi-volatile
    #if i==0:                  
    #    fillC = df
    #else:
    #    fillNC = df
    #i += 1
    
    # Statistiques
    if stat == True:
        print 'moyenne\n', df.mean(),'\n'
        print 'max\n', df.max(),'\n'
        print 'min\n', df.min()

    # Plot
    for mes, data in df.iterkv():
        labels  = xr.liste_mesures(mesure = mes)[['STATION']]
        station = NOMS[labels['STATION'][0]]
        param   = NOMS[nom]
        label   = "%s - %s" % (param, station)
        
        # Suppression des valeurs négatives
        val = df[mes]
        val[data<0]=0
        val.plot(ax = ax, 
                label           = label,
                linestyle       = '-',
                linewidth       = LINEWIDTH,
                marker          = 'o',
                markeredgewidth = 0,
                markersize      = MARKERSIZE,
                clip_on         = False)
    
    # Sauvegarde pour calculer le max de l'échelle de concentration
    tmp = tmp.append(df)   

# Remplissage de l'aire entre PM10C et PM10NC
#ax.fill_between(df.index,fillC.PM10C_PRE,fillNC.PM10NC_PRE, facecolor = '#ffa64d', alpha =0.5)

#Echelle
mini = 0
max = tmp.max().max()
if maxi == None:
    if max <= 300:
        maxi = 300
    if max <= 200:
        maxi = 200
    if max <= 100:
        maxi = 100
    if max <= 50:
        maxi = 50
    if max <= 10:
        maxi = 10
    if max <= 1:
        maxi = 1
ax.set_ylim(ymin = mini, ymax = maxi)

# Taille axes
for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(XFONTSIZE[size])
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(XFONTSIZE[size])

# Unit
if nom == 'CO':
    unit = r'$\rm{mg/m^3}$'
else:
    unit = r'$\rm{\mu g/m^3}$'

plt.text(-0.05, 1.03, unit, 
        ha = 'center',
        va = 'bottom',
        fontsize = UNITSIZE[size],
        transform = ax.transAxes)

# Seuils
seuils = pd.DataFrame(index = df.index)

if ALERTE == True:
    if nom not in ('PM10','PM10NC'):
        seuils['MVR'] = MVR[nom]
    seuils['IR'] = IR[nom]
    seuils['A']  = A[nom]
if Valeur_lim == True:
    seuils['VL'] = VL[nom]
if Obj_qual == True and nom != 'CO':
    seuils['OQ'] = OQ[nom]
if Oms == True and nom != 'CO':
    seuils['OMS'] = OMS[nom]

for seuil, data in seuils.iterkv():
    label = SEUILS[seuil]  + ' (%i' % data[0] + ' ' + unit + ")"
    if data[0] <= maxi or data[0]+10 >= maxi:
        data.plot(ax = ax, 
                label           = label,
                linestyle       = '-',
                linewidth       = LINEWIDTH+0.5,
                markeredgewidth = 0,
                markersize      = MARKERSIZE,
                color           = COULEURS_VR[seuil],
                clip_on         = False)

# Grille
ax.xaxis.grid(False, which = 'both')
ax.yaxis.grid(True, which = 'both', color = 'darkgrey')
ax.set_xlabel('')
ax.set_ylabel('')

# Légende
leg = plt.legend(bbox_to_anchor = (-0.075, 1.08, 1., .10),
                loc  = 3,
                ncol = COL,
                mode = None,
                fontsize = LEGFONTSIZE[size])

# Cloture
leg.draw_frame(False)
fig.savefig('../Figures/'+ figname, dpi = DPI)
plt.clf()
