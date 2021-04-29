#!C:\python37\python.exe

import os,sys
import cgi
import numpy as np
import rasterio

import cgitb
cgitb.enable()

print ("Content-type: text/html;\n\n")
print

print ("""
<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
		<meta charset="utf-8">
		<title>Mangrove</title>
		<link rel="stylesheet" href="assets/css/bootstrap.min.css">
		<link rel="stylesheet" href="assets/css/main.css">
        <script src="assets/js/jquery.min.js"></script>
         <script src="http://dev.openlayers.org/releases/OpenLayers-2.13.1/OpenLayers.js"></script>	
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.0/jquery.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/js/bootstrap.min.js"></script>        
	</head>
    <script>
    $(document).ready(function(){
        $("#etape2").hide();
        $("#etape3").hide();
        $("#Message").hide();
        $("#Message2").hide();
        $("#reponses").hide();
        $("#fichiers").hide();
        $("#wait").css("display", "none");
       
        $("#btn").click(function(){
            $("#wait").css("display", "block");
            image2=$("#image2").val();
            image1=$("#image1").val();
            maxi=$("#maxi").val();
            mini=$("#mini").val();
            avantValidation(image1,image2,maxi,mini);//lancer le traitement etape 1
       });
       $("#btnValider").click(function(){
         traitementValider();
       });
       $("#btnNonValider").click(function(){
         traitementNonVlider();
           
       });
       $("#Continuer").click(function(){
        polygone=$("#ZoneSelectionner").val();
        if(polygone===""){
           alert("Veuillez selectionner un vrai poligone");
        }else{
           traitementApresValider();
        }   
       });
       
    });
    function avantValidation(image1,image2,maxi,mini){
           $.ajax({
              url : 'traitement1.py',
              type : 'POST',
              data : 'image2='+image2+'&image1='+image1+'&maxi='+maxi+'&mini='+mini,
              dataType : 'html',
              success: function(response) {
                $('#Resultat').html(response);
                console.log( response );
                $("#wait").css("display", "none");//loader
                alert("ok");
                $("#reponses").show();//aficher les resultats type image
                $("#etape1").hide();
                $("#etape2").show();
              },
              error: function( response ) {
                $("#wait").css("display", "none");//loader
                setTimeout(function(){ alert("ok"); }, 9000);
                $("#reponses").show();//aficher les resultats type image
            
                $("#etape1").hide();
                $("#etape2").show();
                init();
              }			
          });
    
    }
    function traitementValider(){
        $("#etape1").hide();
        $("#etape2").hide();
        $("#etape3").show();
        $("#Message2").show();
    }
    function traitementNonVlider(){
        $("#etape2").hide();
        $("#etape1").show();
        $("#Message").show();
    }
    
    function traitementApresValider(){
          
         $("#wait").css("display", "block");
         polygone=$("#ZoneSelectionner").val();
            $.ajax({
                  url : 'traitement2.py',
                  type : 'POST',
                  data : 'poly='+polygone,
                  dataType : 'html',
                  success: function(response) {
                    $('#Resultat').html(response);
                    $("#wait").css("display", "none");
                    alert("ok");
                    $("#fichiers").show();
                  },
                  error: function( response ) {
                    alert("non ok");
                    //console.log( response );
                  }			
              }); 
         
    
    }
   
    </script>
     <script type="text/javascript">
	

	     
        var carte;
        function init() {
			var bounds=new OpenLayers.Bounds(318500.00,7223130.00,1087715.73,8674988.64);
			var options={
				maxExtent:bounds,
				projection:"epsg:32738",
				units:"m",
				controls:[
					new OpenLayers.Control.Navigation(),
					new OpenLayers.Control.LayerSwitcher(),
					new OpenLayers.Control.PanZoomBar(),
					new OpenLayers.Control.MousePosition(),
					
				],
			};
            carte = new OpenLayers.Map('carte',options);
			
			
             var mangrove_madagascar= new OpenLayers.Layer.WMS(
				"mangrove_madagascar", "http://localhost:8080/geoserver/mangrove/wms?",
				{ 
					layers: "mangrove:mangrove_madagascar",
					format:"image/png",
					transparent:true,	
					srs:"epsg:32738",
					visibility: true,
					width:800,
					height:500
				},
				{isBaseLayer: false}
			);
            
            var couche= new OpenLayers.Layer.WMS(
				"couche", "http://localhost:8080/geoserver/mangrove/wms?",
				{ 
					layers: "mangrove:couche",
					format:"image/png",
					transparent:true,	
					srs:"epsg:32738",
					visibility: true,
					width:800,
					height:500
				},
				{isBaseLayer: false}
			);
            
            var raster_mangrove= new OpenLayers.Layer.WMS(
				"mangrove_ndvi", "http://localhost:8080/geoserver/mangrove/wms?",
				{ 
					layers: "mangrove:mangrove_ndvi",
					format:"image/png",
					transparent:true,	
					srs:"epsg:32738",
					visibility: true
				},
				{isBaseLayer: true}
			);
			
			highlightLayer = new OpenLayers.Layer.Vector("Highlighted Features", {
                displayInLayerSwitcher: false,
                isBaseLayer: false
                }
            );

				 
			
            carte.addLayers([mangrove_madagascar,couche,raster_mangrove,highlightLayer]); 
			
			//district.setVisibility(false);
			//communes.setVisibility(true);
			carte.addControl(new OpenLayers.Control.MousePosition());
            carte.zoomToMaxExtent();
            //event 
			var infoControls = {
            click: new OpenLayers.Control.WMSGetFeatureInfo({
                url: 'http://localhost:8080/geoserver/mangrove/wms',
                title: 'Identify features by clicking',
                layers: [couche],
                queryVisible: true,
                infoFormat:'application/json',
				output:'features',
				format:new OpenLayers.Format.JSON,
                eventListeners: {
                    getfeatureinfo: function(event) { 
						getFeaturesTohilight(event);
						
                       
                }}
            }),
           };
 
          for (var i in infoControls) {
                infoControls[i].events.register("getfeatureinfo", this, showInfo);
                carte.addControl(infoControls[i]);
            }
 
            infoControls.click.activate();;
 
        }

        function showInfo(gid,event,zone) {	
			
						carte.addPopup(new OpenLayers.Popup.FramedCloud(
								"chicken",
								carte.getLonLatFromPixel(event.xy),
								new OpenLayers.Size(800,600),
								gid,
								null,
								true
						));
            
			
        }
 
		function getFeaturesTohilight(event){//trouver le nom de shape cliqué et appeler la fonction highlightAndShowInfos
			var zone;
			var layers = carte.getLayersBy("visibility", true);
			
			for(var i=0;i<layers.length;i++){
				if(layers[i].name=="couche"){
					zone="couche";  
					highlightAndShowInfos(event,zone);
				}
			}
		}
		function highlightAndShowInfos(event,zone){ //pour chercher le gid et polygone de la zone cliquée,puis appeler le showInfo
			var coords=carte.getLonLatFromPixel(event.xy)+"";			
			var lng=coords.split(",")[0].split("=")[1];
			var lat=coords.split(",")[1].split("=")[1];
			coords=lng+","+lat; 
			alert(coords);
			$.get("highlighting.php?point="+coords+"&zone="+zone)
			  .done(function(data) {
                alert(data);			  
				var in_options = { 'internalProjection': new OpenLayers.Projection("EPSG:32738"), 'externalProjection': new OpenLayers.Projection("EPSG:32738") };
				var polygon=data.split("===")[0];
				var gid=data.split("===")[1];				
				var feature =  new OpenLayers.Format.WKT(in_options).read(polygon);//ici c'est le polygone
                $("#ZoneSelectionner").val(polygon);
                /*highlightLayer.destroyFeatures();
                 highlightLayer.addFeatures([feature]);
                 highlightLayer.redraw();
				 showInfo(gid,event,zone);*/
			  });
		}
    </script>
	<body>

		<div class="content" style="height: 100%;">
           <header class="navbar-fixed-top">
                <div class="navbar navbar-default top-menu" style="height: 50px;">
                    <div class="navbar navbar-left">
                    </div>
                    <div class="navbar navbar-right">
                      
                    </div>
                </div>
            </header>
            <section class="container-fluid corps" style="background-color:rgba(84, 75, 75, 0.12);">
				<div class="row row-col">
					<div class="col-lg-4 col-md-4 col-sm-12 col-xs-12 left" style="background-color: RGBA(31, 31, 65, 0.03)">
						<h1>Param&egravetres</h1>
						<div class="container">
							<div class="row">
								<form class="form" action="test2.py" method="post">
									<fieldset>
										<legend style="font-size: 12px;font-weight: 700">R&eacutesultats NDVI</legend>
                                        <div style="border:1px solid #cccccc;padding-top: 6px">
										<div class="form-group">
											<label for="">Donn&eacutees 2 :</label>
											<select class="form-control" name="image2" id="image2">
												<option value="STDmean_annual_20190101.tif">STDmean_annual_20190101.tif</option>
												<option value="STDmean_annual_20170101.tif">STDmean_annual_20170101.tif</option>
											</select>
											<label for="">Donn&eacutees 1 :</label>
											<select class="form-control" name="image1" id="image1">
												<option value="STDmean_annual_20190101.tif">STDmean_annual_20190101.tif</option>
												<option value="STDmean_annual_20170101.tif">STDmean_annual_20170101.tif</option>
											</select>
                                           </div> 
										</div>
									</fieldset>
									<fieldset id="field">
										<legend style="font-size: 12px;font-weight: 700">Valeurs max, min </legend>
                                        <div style="border:1px solid #cccccc;padding-top: 6px">
										<div class="form-group">
                                            <div id="Message"><span style="color:#26ca42">Entrer les nouvelles valeurs</span><br><br></div>
											<label for="">Max :</label>
											<input type="number" name="max" id="maxi" value="" step="0.1">
											<label for="">Min :</label>
											<input type="number" name="min" id="mini" value="" step="0.1"><br>
										</div>
                                        </div>
									</fieldset>
                                    <input type="hidden" name="ZoneSelectionner" id="ZoneSelectionner" value="">
                                    <div id="etape1">
									<button type="button" name="button" id="btn">Lancer</button>
                                    </div>
                                    <div id="etape2">
                                        
                                        <button type="button" name="valider" id="btnValider">Oui</button>
                                        <button type="button" name="nonvalider" id="btnNonValider">Non</button>
                                    </div>
                                    <div id="Message2"><span style="color:#26ca42">Selectionner la zone à calculer</span><br><br></div>
                                    <div id="etape3">
                                        <button type="button" name="Continuer" id="Continuer">Continuer</button>
                                    </div>
                                    <div id="wait" style="width:125px;height:50px;position:absolute;left:82%;margin: -43px;"><img src='assets/images/ZZ5H.gif' width="50" height="50" />  En cours...</div>

									<div class="form-group">
									</div>
								</form>
							</div>
						</div>
                        <div class="tab-menu" id="reponses">
						<h1>R&eacutesultats</h1>
						
							<div class="col-md-12 col-sm-6">
								<div class="list">
									<ul class="list-menu">
										<li id="visual">Visualisation</li>
										<li id="pixel">Nbr pixel</li>
										<li id="surface">Surface</li>
									</ul>
								</div>
								<div class="content-tabs">
									<div class="menu active">
										<div class="container-fluid">
											<div class="col-md-8 left" id="affichage" style="background-image:url('ndvifichier.png');">
                                               
                                            </div>
                                             <div class="col-md-4 right" id="liens">
												<a href="ndvifichier.png" target="_blank">Visualiser</a>
												<a href="raster/resulat_ndvi_apres_filtre.tif">T&eacutelecharger</a>
											</div>
                                            
											
										</div>
									</div>
									<div class="menu">
										<h2>Nombre de pixel</h2>
									</div>
									<div class="menu">
                                    <div id="fichiers"><a href="difference.csv"><img src="assets/images/csv.JPG" width="30px" height="30px"></a></div>
                                    <div id="Resultat"></div>
									</div>
								</div>
							</div>
						</div>
					</div>
					<div class="col-lg-8 col-md-8 col-sm-6 right">
                            <div class="row-fluid">
                        <!-- block -->
                        <div class="block">
                           
                            <div class="block-content collapse in">
                                <div >
											<div class="form-row">
								  
								  
						</div>
	
									  
										<div id="layerswitcher" class="olControlLayerSwitcher"></div>
										<div id="map" style="border: 1px solid #cccccc;;">
                                            <div id="carte"  style="width:100%; height:600px;"></div>
                                            <div id="wrapper">				
										</div> 
                                        </div>
									 
										
                                    </div>
                                </div>
                               
                            </div>
                        </div>
					</div>
				</div>
			</section>
		</div>
		<script type="text/javascript" src="assets/js/main.js"></script>
	</body>
</html>
""")


