#!C:\python37\python.exe

import os,sys
import cgi
import numpy as np
import geopandas as gpd
import rasterio
import rasterio.mask
import fiona
import CalculNDVIMangrove as mangrove
from osgeo import ogr
from osgeo import gdal
gdal.SetConfigOption('CPL_DEBUG','ON')
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


import cgitb
cgitb.enable()


os.environ['HOME'] = 'C:\test'
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.colors import ListedColormap


print("Content-type:text/html\r\n\r\n")
print
print('<title>Test</title>')
print("test")
data = cgi.FieldStorage()
image1= data["image1"].value
image2= data["image2"].value
maxi= data["maxi"].value
mini= data["mini"].value
#image1= "STDmean_annual_20170101.tif"
#image2= "STDmean_annual_20190101.tif"
#maxi= "0.1"
#mini= "-0.2"

union=mangrove.unionDeuxCouches("shp/couche1.shp","shp/couche2.shp")
regrouper=mangrove.regrouperEntite("shp/couche_union.shp")

print("difference....")
difference=mangrove.differenceDeuxNDVI(image1,image2)
print("filtre")
bornPlus=float(maxi)
bornMoins=float(mini)
filtre=mangrove.filtrerNDVI(difference,bornPlus,bornMoins)
print("sotck")
Imageresultat=mangrove.stockerRaster(image1,filtre)
print("tracer image")
src=rasterio.open(Imageresultat).read(1)
cmap = ListedColormap(["darkgreen","red","yellow"])
fig, ax = plt.subplots(figsize=(10, 5))
chm_plot = ax.imshow(src,cmap=cmap)
ax.set_title("Résultat 2019-2017")
# Add a legend for labels
legend_labels = {"darkgreen": ">Max","red": "<Min", "yellow": "Autre"}

patches = [Patch(color=color, label=label)
           for color, label in legend_labels.items()]

ax.legend(handles=patches,
          bbox_to_anchor=(1.35, 1),
          facecolor="white")

ax.set_axis_on()
plt.savefig( "ndvifichier.png", format='png' )

psqlCon = psycopg2.connect("dbname=ndvi user=postgres password=admin");
psqlCon.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);
psqlCursor      = psqlCon.cursor();
tableName       = "couche";
dropTableStmt   = "DROP TABLE %s;"%tableName;
psqlCursor.execute(dropTableStmt);
psqlCursor.close();
psqlCon.close();


def testLoad(serverDS, table, sourceFile):
    ogr.RegisterAll()
    shapeDS = ogr.Open(sourceFile)
    sourceLayer = shapeDS.GetLayerByIndex(0)
    options = []
    name = serverDS.CopyLayer(sourceLayer,table,options).GetName()
    return name

if __name__ == '__main__':
    serverName = 'localhost'
    database = 'ndvi'
    port = '5432'
    usr = 'postgres'
    pw = 'admin'
    table = 'couche'
    connectionString = "PG:dbname='%s' host='%s' port='%s' user='%s' password='%s'" % (database,serverName,port,usr,pw)
    ogrds = ogr.Open(connectionString)
    name = testLoad(ogrds,table,'shp/couche_union.shp')


print("termine")






