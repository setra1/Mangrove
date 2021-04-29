#!C:\python37\python.exe

import os,sys
import cgi
import numpy as np
import attaque as at


import cgitb
cgitb.enable()


print("Content-type:text/html\r\n\r\n")
print
print('<title>Test</title>')
print("Debut de traitements")
data = cgi.FieldStorage()
chemin= data["chemin"].value
tuile= data["tuile"].value
date_ante= data["date_ante"].value
date_post= data["date_post"].value
at.diffndvi(chemin,tuile,date_ante,date_post)

print("fin du traitements")






