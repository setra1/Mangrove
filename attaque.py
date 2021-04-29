from zipfile import ZipFile as zf
import os
import fnmatch
import sys
import glob
import re
import rasterio

"""
Utilisation du code : 

1-pour dezipper des archives 
	python attaque.py dz /repertoire_ou_se_trouve_les_archives
	
2-pour calculer les differences de ndvi avec une reference
	python attaque.py at /repertoire_ou_se_trouve_les_archives_decompressees /tuile_concerne
	
2-pour calculer les differences de ndvi avec une reference
	python attaque.py di /repertoire_ou_se_trouve_les_archives_decompressees /tuile_concerne /date_anterieure /date_posterieur

exemple 
	python attaque.py dz D:\test\ 
	
	python attaque.py at D:\test\ T38LPH
	
	python attaque.py di D:\test\ T38LPH 20200621 20181202
"""
def open_fic(fic):
    return rasterio.open(fic)

def read_fic(fic):
	return rasterio.open(fic).read(1).astype('float32')

def get_metadata(fic):
	img = open_fic(fic)
	mtdt = img.meta
	mtdt.update(driver='Gtiff',dtype='float32')
	return mtdt
	
def write_result_fic(calculation,metadata,outPath):
	wrf = rasterio.open(outPath,'w',**metadata)
	wrf.write(calculation,1)
	wrf.close()

def extractallzip(rprt):
	for fold in os.listdir(rprt):
		if fnmatch.fnmatch(fold,'*.zip'):
			print('Extracting '+fold+'...')
			zf(os.path.join(rprt+fold),'r').extractall(rprt)
			print(fold+' extracted !')
			
def getType(rprt,tile,date): #methode qui renvoie si une image a ete telecharger sur le site de Theia ou sur SentinelDataHub
	condSafe = '*'+str(date)+'*'+str(tile)+'*.SAFE'
	condTheia = '*'+str(date)+'*'+str(tile)+'*_D_*'
	for fold in os.listdir(rprt):
		if os.path.isdir(os.path.join(rprt,fold))==True:
			if fnmatch.fnmatch(fold,condSafe):
				typo = 'safe'
			elif fnmatch.fnmatch(fold,condTheia):
				typo = 'theia'	
	return typo
			
def getBand(rprt,tile,date,typo): #methode qui renvoie les bandes IR et R correspondantes selon sa date et sa tuile
	os.chdir(rprt)
	patSafeIR = '**/'+str(tile)+'*'+str(date)+'*_B08_10m.jp2'
	patSafeR = '**/'+str(tile)+'*'+str(date)+'*_B04_10m.jp2'
	patTheiaIR = '**/*'+str(date)+'*'+str(tile)+'*_FRE_B8.tif'
	patTheiaR = '**/*'+str(date)+'*'+str(tile)+'*_FRE_B4.tif'
	if typo == 'safe':
		patIR = patSafeIR
		patR = patSafeR
	elif typo == 'theia':
		patIR = patTheiaIR
		patR = patTheiaR
	bandIR = glob.glob(patIR,recursive = True)[0]
	bandR = glob.glob(patR,recursive = True)[0]
	return [bandIR,bandR]
	
def getDateTypeList(rprt,tile): #methode qui renvoie les dates correspondantes a une tuile pour preparer le calcul de difference de ndvi pour une attaque
	condSafe = '*'+str(tile)+'*.SAFE'
	confTheia = '*'+str(tile)+'*_D_*'
	dateSafe = 'L2A_(.+?)T'
	dateTheia = '_(.+?)-'
	dates = []
	for fold in os.listdir(rprt):
		if os.path.isdir(os.path.join(rprt,fold))==True:
			if len(str(fold)) == 65:
				cond = condSafe
				date = dateSafe
				typo = 'safe'
			elif len(str(fold)) == 48:
				cond = confTheia
				date = dateTheia
				typo = 'theia'
			else:
				sys.exit('Aucune image sentinel2 trouvée')
			if fnmatch.fnmatch(fold,cond):
				andro = re.search(date,fold).group(1)
				dates.append([andro,typo])
	return dates
	
def calcndvi(folder,tile,date,typo): #calcul du NDVI d'une image Sentinel2
	imgNDVI = folder+'ndvi_'+tile+'_'+date+'.tif'
	if not os.path.exists(imgNDVI):
		pathIR = getBand(folder,tile,date,typo)[0]
		pathR = getBand(folder,tile,date,typo)[1]
		bandIR = read_fic(pathIR)
		bandR = read_fic(pathR)
		NDVI = (bandIR-bandR)/(bandIR+bandR)
		write_result_fic(NDVI,get_metadata(pathIR),imgNDVI)
	return imgNDVI

def calcdiff(rast1,rast2,rast3): #difference de deux rasters (rast3 = rast1 - rast2)
	if not os.path.exists(rast3):
		ras1 = read_fic(rast1)
		ras2 = read_fic(rast2)
		ras3 = ras1-ras2
		write_result_fic(ras3,get_metadata(rast1),rast3)
	return rast3	

def attack(rprt,tuile,dateRef): #methode pour calculer la difference de ndvi d'une serie temporelle par rapport a une date reference sur une tuile
	
	imref = calcndvi(rprt,tuile,dateRef,getType(rprt,tuile,dateRef))
	
	dates = getDateTypeList(rprt,tuile)	#liste des dates
	
	for date in dates:#calcul de ndvi et de difference
		imDIFFRef = rprt+'diff_ndvi_'+tuile+'_'+dateRef+'_'+date[0]+'.tif'
		if os.path.exists(imDIFFRef): #verification si la date a ete deja calcule
			print ('Difference de NDVI entre les dates '+dateRef+' et '+date[0]+' de la tuile '+tuile+' deja calculee')
		else: 
			if dateRef != date[0]:
				print ('Calcul de la difference de NDVI du '+date[0]+' avec la date reference ...')
				calcdiff(imref,calcndvi(rprt,tuile,date[0],date[1]),imDIFFRef)
				print ('Calcul de la difference avec la tuile '+tuile+' du '+date[0]+' effectue !')

def diffndvi(rprt,tuile,dateant,datepost): #methode pour calculer la difference de ndvi entre deux dates d'une tuile, difference = date anterieur - date posterieur
	
	imDIFF = rprt+'diff_ndvi_'+tuile+'_'+dateant+'_'+datepost+'.tif'
	if os.path.exists(imDIFF): #verification si la date a ete deja calcule
		print('Difference de NDVI entre les dates '+dateant+' et '+datepost+' de la tuile '+tuile+' deja calculee')
	else:	
		print ('Calcul de la difference de NDVI...')
		calcdiff(calcndvi(rprt,tuile,dateant,getType(rprt,tuile,dateant)),calcndvi(rprt,tuile,datepost,getType(rprt,tuile,datepost)),imDIFF)
		print ('Image difference de NDVI calculee !')
	
if __name__ == '__main__':
	
	if sys.argv[1] == 'dz': 
		extractallzip(sys.argv[2])
	elif sys.argv[1] == 'at': 
		attack(sys.argv[2],sys.argv[3],sys.argv[4])
	elif sys.argv[1] == 'di':
		diffndvi(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
	else:
		print('Arguments invalides !')
