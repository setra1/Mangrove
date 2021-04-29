# -*- coding: utf-8 -*-
"""

@author: IRD
"""
import geopandas as gpd
import rasterio
import rasterio.mask
import fiona
import numpy as np
from shapely.ops import cascaded_union, unary_union
from shapely.geometry import shape
from shapely.geometry import mapping, Polygon

    
def differenceDeuxNDVI(a,b):
    """Comparer la difference de a et b
    
      Cette fonction prend en paramêtre le chemin des deux images NDVI
    """
    #Lire l'image 1 avec rasterio
    mat1=(rasterio.open(a)).read(1)
    #Lire l'image 2 avec rasterio
    mat2=(rasterio.open(b)).read(1)
    #Verifier la taille de chaque image
    if mat1.shape==mat2.shape:
        #Initialier le contenu de matrice resultat en nombre decimal
        mat3=mat2-mat1
        #retourner un resultat de type matrice
        return mat3
    else:
        "les images ne sont pas de même taille"
        return False
   

def filtrerNDVI(a,b,c):
    """filtrer le NDVI a par deux valeurs les seuils b,c
    Cette fonction prend en parametre l'image à filtrer,la valeur de la borne positive et la borne negative
    
    """
    if b>2.0:
        #Verifier si la borne positive est correcte
        print("la valeur de la borne positive ne depasse pas 2")
    elif c<-2.0:
         #Verifier si la borne negative est correcte
        print("la valeur de la borne negative ne depasse pas -2")
    else:
        #creer une image à partir des trois seuils dans le parametre de la fonction filtre NDVI
        img3=np.where((a>=b),3.0,(np.where(a<=c, 4.0,5.0)))
        #Retourner le resultat du seuil
        return img3


def stockerRaster(a,b):
    """Pour ecrire une image raster
     Parametre: a=l'image raster à copier ses informations geometriques
                b=la matrice comme contenu de la nouvelle image
    valeur de retour: le nom de la nouvelle image
    """
    localname = 'raster/resulat_ndvi_apres_filtre.tif'
    with rasterio.open(a) as src:
        profile = src.profile.copy()
        profile.update({
                'dtype': 'float64',
                'count':1,
                'height': b.shape[0],
                'width': b.shape[1]})  

        with rasterio.open(localname, 'w', **profile) as dst:
            dst.write_band(1, b)
        
    return localname



def unionDeuxCouches(a,b):
    """Pour union des deux couches des differentes dates
    
       Cette fonction prend en parametre le chemin des deux couches
    """
    #Lire le shapefile 1 et prendre en parametre a
    shapefile1 = gpd.read_file(a)
    #Lire le shapefile 2 et prendre en parametre b
    shapefile2 = gpd.read_file(b)
    #Verifier si les deux couches vecteurs ont de la même systeme de coordonnées
    if shapefile1.crs==shapefile2.crs:
        #Créer l'union des deux couches
        couche_union = gpd.overlay(shapefile1, shapefile2, how='union')
        #couche_union.plot(alpha=0.5, edgecolor='k', cmap='tab10'); pour l' afficher en plot
        #Definir le nom de la sortie
        out = r"shp/couche_union.shp"
        #Creer le fichier en sortie
        ecrire_union=couche_union[:]
        ecrire_union.to_file(out)
    else:
        print("Vérifier le systeme de coordonnées de ces deux couches vecteurs")
        
 
 

def regrouperEntite(a):
    """Pour regrouper les entites de la couche vecteur obtenue en union des deux couches
     cette fonction possede un parametre a,c'est le chemin de la couche à regrouper
    """
    polygons =[shape(feature['geometry']) for feature in fiona.open(a)]
    union_poly = unary_union(polygons) # or cascaded_union(polygons)
    schema = {
        'geometry': 'Polygon',
        'properties': {'id': 'int'},
    }
    with fiona.open('shp/my_shp6.shp', 'w', 'ESRI Shapefile', schema) as c:
        c.write({
            'geometry':mapping(union_poly),
            'properties': {'id': 1},
        })
        




def decoupeRaster(a,b):
    """Decouper une raster à l'aide de couche vecteur
       a est le chemin de vecteur
       b est le chemin du raster à decouper
    """
    chaineFormat=""
    nbr=0
    for i,caractere in enumerate(a):
            if caractere==',':
                nbr=nbr+1   


    mat=np.zeros(shape=(nbr+1,2))
    compteur=0
    for i,caractere in enumerate(a):
        if i>=9 and i<len(a)-1:
            if caractere==',':
                res=chaineFormat.split()
                coordonnees=np.array([(float(res[0]),float(res[1]))])
                mat[compteur]=coordonnees
                compteur=compteur+1
                chaineFormat=""
            elif caractere==')':
                res=chaineFormat.split()
                coordonnees=np.array([float(res[0]),float(res[1])])
                mat[compteur]=coordonnees
                break
            else:
                chaineFormat=chaineFormat+caractere
                        
                
    chaine={}
    chaine["type"]="Polygon"
    chaine["coordinates"]=[mat]
    shapes=[chaine]
    #instruction pour lire et decouper le raster    
    with rasterio.open(b) as src:
        out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
        out_meta = src.meta
        out_meta.update({"driver": "GTiff","height": out_image.shape[1],"width": out_image.shape[2],"transform": out_transform})
    #intruction pour ecrire le raster en sortie
    with rasterio.open("raster/RGB.byte.masked.tif", "w", **out_meta) as dest:
        dest.write(out_image)



def compterValeursBornes(a):
    """Compter le nombre de pixel pour chaque borne
     parametre:a est la matrice contenant le pixel à compter
     valeur de retour:un tableau de 3lignes
    """
    #Initialiser la valeur de chaque borne
    v1=0
    v2=0
    v3=0
    #Initialiser un tableau pour le nombre de pixel de chaque borne
    #Lire l'image contenant le pixel à compter
    mat2=np.array((rasterio.open(a)).read(1))
    #Boucle sur la ligne et colonne de l'image sous forme matrice
    for i in range(0,mat2.shape[0]):
        for j in range(0,mat2.shape[1]):
           #Verifier si la position en cours est égale à 3 
           if mat2[i,j]==3.0:
               v1=v1+1
           #Verifier si la position en cours est égale à 4
           elif mat2[i,j]==4.0:
               v2=v2+1
            #si la valeur encours ni 3,4,donc elle doit compter en v3
           else:
               v3=v3+1
    #retourner le tableau
               
    nombre=np.array([v1,v2,v3])
    return nombre



def calculSurface(a):
    """calculer la surface par rapport à la resolution et le nombre de pixel
     parametre:l'array nombre de pixel
     valeur de retour:un tableau de 3lignes(chaque ligne est en m²)
    """
     #chaque element du tableau * 100      100=10m*10m
    surface=a*100
    #retourner le resultat
    return surface


def conversionSurfaceEnHa(surface):
    """convertir la surface en hectar
       Parametre (surface):le resultat en m² de la fonction calculSurface
       valeur de retour:un tableau de 3lignes
    """
    #la formule de la conversion m² en ha 
    ha=surface*0.0001
    #retourner le resultat
    return ha


def conversionSurfaceEnKm(surface):
    """convertir la surface en hectar
       Parametre (surface):le resultat en m² de la fonction calculSurface
       valeur de retour:un tableau de 3lignes
    """
    #la formule de la conversion m² en km
    km=surface*0.000001
    #retourner le resultat
    return km



