#!C:\python37\python.exe

import os,sys
import cgi
import numpy as np
import geopandas as gpd
import rasterio
import rasterio.mask
import fiona
import CalculNDVIMangrove as mangrove


import cgitb
cgitb.enable()


print("Content-type:text/html\r\n\r\n")
print
print('<title>traitement 2</title>')
data = cgi.FieldStorage()
poly= data["poly"].value
decouper=mangrove.decoupeRaster(poly,"raster/resulat_ndvi_apres_filtre.tif")
compter=mangrove.compterValeursBornes("raster/RGB.byte.masked.tif")
surface=mangrove.calculSurface(compter)
conversionHa=mangrove.conversionSurfaceEnHa(surface)
conversionKm=mangrove.conversionSurfaceEnKm(surface)
print("""
   <table class="table table-bordered">
    <thead>
        <th>Nbr/Surface</th>
        <th>Valeur 1</th>
        <th>Valeur 2</th>
        <th>Autre</th>
    </thead>
    <tr>
        <td><strong>Nombre pixel</strong></td>
        <td>
""")
print(compter[0])
print("""</td><td>""")
print(compter[1])
print("""</td><td>""")
print(compter[2])
print("""</td></tr>""")
print("""<tr><td><strong>Surface en M<sup>2</sup></strong></td><td>""")
print(surface[0])
print("""</td><td>""")
print(surface[1])
print("""</td><td>""")
print(surface[2])
print("""</td></tr>""")
print("""<tr><td><strong>Surface en Ha</strong></td><td>""")
print(round(conversionHa[0],4))
print("""</td><td>""")
print(round(conversionHa[1],4))
print("""</td><td>""")
print(round(conversionHa[2],4))
print("""</td></tr>""")
print("""<tr><td><strong>Surface en Km<sup>2</sup></strong></td><td>""")
print(round(conversionKm[0],4))
print("""</td><td>""")
print(round(conversionKm[1],4))
print("""</td><td>""")
print(round(conversionKm[2],4))
print("""</td></tr></table>""") 
entetes = [
     u'Nbr/Surface',
     u'Valeur 1',
     u'Valeur 2',
     u'Autre',
]
valeurs =np.array([['Nombre pixel',compter[0],compter[1],compter[2]],['Surface en M²',surface[0],surface[1],surface[2]],['Surface en Ha',round(conversionHa[0],4),round(conversionHa[1],4),round(conversionHa[2],4)],['Surface en Km²',round(conversionKm[0],4),round(conversionKm[1],4),round(conversionKm[2],4)]]) 

f = open('difference.csv', 'w')
ligneEntete = ";".join(entetes) + "\n"
f.write(ligneEntete)
for valeur in valeurs:
     ligne = ";".join(valeur) + "\n"
     f.write(ligne)

f.close()
  








