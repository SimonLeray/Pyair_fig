#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#Nom :  : script-fig.py
#Description    : Génération de figures standardisées par typologie de station
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


###################     Données d'entrées    ######################


polluant = 'O3'    # PM10, PM2.5, O3, NO2 ou CO
histo    = 1999
ANNEE    = 2015

# Activation de la moyenne glissante, max journalier (True/False)
GLISSANT       = True
sur            = 8        # X unités (QH, H, M, A) 
MAX_JOURNALIER = False
MAX_ANNUEL     = True

# Activation des seuils d'alerte et valeurs réglementaires (True/False)
Valeur_lim = False
Obj_qual   = True
Oms        = True

#Paramètres figure
figname    = polluant + "-histo"
size       = 'S'    # L : Large , S : Small
MARKERSIZE = 2      # Taille des points
COL        = 2      # Nombre de colonne dans la légende
maxi       = None   # max de l'échelle, optionnel. Si = None, calculé auto

#Statistiques : moy, [min - max] (True/False)
stat = False


###################################################################


"""Définition des polluants - Mesures automatiques (analyseurs)"""

#Polluants par typo de stations
NO2_U   = ['NO2_PRE', 'NO2_DAL', 'NO2_NIC', 'NO2_HUG', 'NO2_FON']
NO2_I   = ['NO2_IPA']
NO2_T   = ['NO2_AIN', 'NO2_VIC']
O3_U    = ['O3_PRE', 'O3_DAL', 'O3_NIC', 'O3_HUG', 'O3_FON']
O3_P    = ['O3_GAR']
O3_R    = ['O3_MER']
SO2_U   = ['SO2_PRE', 'SO2_FON']
SO2_P   = ['SO2_GAR']
SO2_I   = ['SO2_IPA', 'SO2_FA']
PM10C_U = ['PM10C_PRE', 'PM10C_DAL', 'PM10C_NIC', 'PM10C_HUG', 'PM10C_FON']
PM10C_P = ['PM10C_GAR']
PM10C_I = ['PM10C_IPA']
PM10C_T = ['PM10C_AIN']
PM25_U  = ['PM25_PRE']
PM25_T  = ['PM25_VIC']
CO_U    = ['CO_NIC']
CO_T    = ['CO_AIN']
TRS_I   = ['TRS_IPA']

#PM10 non corrigé pour l'histo de 1998 à 2006   , attention ordre PM10 et PM10C doit être identique
HISTO   = 2007
PM10NC_U = ['PM10NC_PRE', 'PM10_DAL', 'PM10_NIC', 'PM10_HUG', 'PM10_FON']
PM10NC_P = ['PM10_GAR']
PM10NC_I = ['PM10_IPA']
PM10NC_T = ['PM10_AIN']
PMNC = {'Station(s) urbaine(s)':PM10NC_U, 
       u'Station(s) périurbaine(s)':PM10NC_P, 
        'Station(s) industrielle(s)':PM10NC_I, 
        'Station(s) trafic(s)':PM10NC_T }

#Définition des classes
class Typo():
    def __init__(self, nom, malist):
        self.nom    = nom
        self.malist = malist
    def get_nom(self):
        return self.nom
    def get_malist(self):
        return self.malist

urbain   = Typo('Station(s) urbaine(s)', [NO2_U, O3_U, SO2_U, PM10C_U, PM25_U, CO_U])
periurb  = Typo(u'Station(s) périurbaine(s)', [O3_P, SO2_P, PM10C_P])
trafic   = Typo('Station(s) trafic(s)',[NO2_T, PM10C_T, PM25_T, CO_T])
rural    = Typo('Station(s) rurale(s)', [O3_R])
indus    = Typo('Station(s) industrielle(s)', [NO2_I, SO2_I, PM10C_I, TRS_I])
stations = [urbain, periurb, trafic, indus, rural]


class Polluant():
    def __init__(self, nom, malist, freq):
        self.nom      = nom
        self.malist   = malist
        self.freq     = freq
    def get_nom(self):
        return self.nom
    def get_malist(self):
        return self.malist
    def get_freq(self):
        return self.freq

NO2  = Polluant('NO2', [NO2_U, NO2_I, NO2_T],'H')
O3   = Polluant('O3', [O3_U, O3_P, O3_R],'H')
SO2  = Polluant('SO2', [SO2_U, SO2_P, SO2_I],'H')
PM10 = Polluant('PM10', [PM10C_U, PM10C_P, PM10C_I, PM10C_T],'D')
PM25 = Polluant('PM25', [PM25_U, PM25_T],'D')
CO   = Polluant('CO', [CO_U, CO_T],'H')
TRS  = Polluant('TRS',[TRS_I],'H')
list_polluants = [NO2, O3, SO2, PM10, PM25, CO,TRS]

KEY = { 'NO2':NO2,'O3':O3, 'SO2':SO2, 'PM10':PM10, 'PM25':PM25, 'CO':CO }
Historique_U_P = { 'NO2':histo,'O3':histo, 'SO2':histo, 'PM10':histo, 'PM25':2009, 'CO':2010 }
Historique_T   = { 'NO2':2009, 'PM10':2009, 'PM25':2013, 'PM10':2009, 'CO':2010 }
Historique_I   = { 'NO2':2008, 'SO2':2002, 'PM10':2008, 'TRS':2008}
Historique_R   = {'O3':2003 }


# Définition des fonctions

def compress_mean(df, nom):  # df (index, col1, col2, col3...) ==> return df (index, col) avec col = moy de (col1, col2, col3)
    return pd.DataFrame(df.mean(axis = 1), columns = [nom])

def compress_min(df, nom):  # df (index, col1, col2, col3...) ==> return df (index, col) avec col = max de (col1, col2, col3)
    return pd.DataFrame(df.min(axis = 1), columns = [nom])

def compress_max(df, nom):  # df (index, col1, col2, col3...) ==> return df (index, col) avec col = max de (col1, col2, col3)
    return pd.DataFrame(df.max(axis = 1), columns = [nom])


# Seuils d'alerte NO2, SO2, O3 et PM10 et Valeurs réglementaires
VL      = {'NO2':40,'PM10':40,'PM25':25,'CO':10}
OQ      = {'NO2':40,'O3':120,'PM10':30,'PM25':10,}
OMS     = {'NO2':40,'O3':100,'PM10':20,'PM25':10,'H2S':7}


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

SEUILS  =  {'OMS':u'Seuil de gêne olfactive (OMS) sur 30 min',
            'VC' :u'Valeur cible annuelle',
            'VL' :u'Valeur limite annuelle',
            'OQ' :u'Objectif de qualité annuel',
            'OMS':u'Valeur guide OMS'}

COULEURS = {u'Station(s) rurale(s)':'#00ff00',                   #Vert foncé : C1000 M0 J100 N0
            u'Station(s) trafic(s)':'#ff0000',                   #Rouge : C0 M100 J100 N0
            u'Station(s) urbaine(s)':'#0033ff',                  #Bleu foncé : C100 M80 J0 N0
            u'Station(s) périurbaine(s)':'#802600',              #Marron : C0 M70 J100 N50
            u'Station(s) industrielle(s)':'#ff8000'}             #Orange : C0 M50 J100 No         

COULEURS_VR = {'VL' :'#ffa500',  #Orange
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
tmp = pd.DataFrame()
dfpm10nc = pd.DataFrame()
nom  = KEY[polluant].get_nom()
freq = KEY[polluant].get_freq()
mesure  = KEY[polluant].get_malist()

# Calculs
for mes in mesure:
    if mes in urbain.get_malist():
        histo = Historique_U_P[nom]
        typo  = urbain.get_nom()
    if mes in periurb.get_malist():
        histo = Historique_U_P[nom]
        typo  = periurb.get_nom()
    if mes in trafic.get_malist():
        histo = Historique_T[nom]
        typo  = trafic.get_nom()
    if mes in indus.get_malist():
        histo = Historique_I[nom]
        typo  = indus.get_nom()  
    if mes in rural.get_malist():
        histo = Historique_R[nom]
        typo  = rural.get_nom()

    print nom
    print typo
    print histo 

    # Cas Particules non corrigées avant 2007
    if nom in 'PM10' and histo < 2007:
        pmnc = PMNC[typo]
        df = xr.get_mesures(mes, debut = '2007-01-01', fin = '%i-12-31' % ANNEE, freq = freq)
        dfpm10nc = xr.get_mesures(pmnc, debut = "%i-01-01" % histo, fin = '2006-12-31', freq = freq)     
    else:
        df = xr.get_mesures(mes, debut = "%i-01-01" % histo, fin = "%i-12-31" % ANNEE, freq = freq)


    title = NOMS[nom] + ' - ' + typo
    if nom in 'O3':
        df = df.resample('A', how = 'max')
        df = compress_max(df, title)
    else:
        df = df.resample('A', how = 'mean')
        df = compress_mean(df, title)
        dfpm10nc = dfpm10nc.resample('A', how = 'mean')
        dfpm10nc = compress_mean(dfpm10nc, title)
        df = dfpm10nc.append(df)
        dfpm10nc = pd.DataFrame()

    # Save pour le max de l'échelle et pour conserver l'index
    tmp = tmp.append(df)

    # Plot
    df = df.asfreq('A')
    ax = df.plot(ax = ax, 
        linestyle = '-', 
        linewidth = LINEWIDTH,
        marker = 'o', 
        markeredgewidth = 0,
        color = COULEURS[typo], 
        markersize = MARKERSIZE, 
        clip_on = False)         

# Statistiques
if stat == True:
    print 'moyenne\n', df.mean(),'\n'
    print 'max\n', df.max(),'\n'
    print 'min\n', df.min()

#Echelle
mini = 0
max = tmp.max().max()
if maxi == None:
    if max <= 300:
        maxi = 300
    if max <= 250:
        maxi = 250
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
seuils = pd.DataFrame(index = tmp.index)

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
leg = plt.legend(bbox_to_anchor = (-0.075, 1.11, 1., .10),
                loc  = 3,
                ncol = COL,
                mode = None,
                fontsize = LEGFONTSIZE[size])

# Cloture
leg.draw_frame(False)
fig.savefig('../Figures/'+ figname, dpi = DPI)
plt.clf()