# PyAir_fig
Python plotting from package PyAir


PyAir is a python package developped by Lionel Roubeyrie. It provides facilities for the connection to the ISEO XAIR database, - and for getting values/informations - in the computation of Air Quality values for the French reglementation.

Pyair_fig allows to use PyAir and plot output.

Typycal usage :

####### Liste des polluants demandés [(famille, polluant)]
####### Exemple : [(NO2,('NO2_AIN','NO2_FON')),(TRS,'TRS_IPA')];
polluants = [(PM10,('PM10_PRE','PM10_HUG','PM10_FON'))];

####### Période, fréquence 
debut = '2015-07-01';
fin   = '2015-07-31';
frequence = 'H'   # H,D,M,A;

####### Activation de la moyenne glissante, max journalier (True/False)
GLISSANT       = True;
sur            = 8        # X unités (QH, H, M, A) ;
MAX_JOURNALIER = True;
MAX_ANNUEL	   = False;

####### Activation des seuils d'alerte et valeurs réglementaires (True/False)
ALERTE     = False
Valeur_lim = False
Obj_qual   = False
Oms        = True

####### Paramètres figure
figname    = 'O3-juillet2015'
size       = 'L'    # L : Large , S : Small
MARKERSIZE = 2      # Taille des points
COL        = 2      # Nombre de colonne dans la légende
maxi       = None   # max de l'échelle, optionnel. Si = None, calculé auto

####### Statistiques : moy, [min - max] (True/False)
stat = False
