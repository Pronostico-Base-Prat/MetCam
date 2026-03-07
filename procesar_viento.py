import xarray as xr
import numpy as np
import json
from herbie import Herbie
import os

# Configuración Geográfica de MetCam (Chile + Antártica)
NORTE, SUR = -17, -90
OESTE, ESTE = -115, -50

def generar_datos_metcam():
    print("MetCam: Conectando con la NOAA...")
    
    # Buscamos el modelo GFS más reciente
    try:
        H = Herbie(product='pgrb2.0p25', model='gfs', fxx=0)
        
        # Pedimos solo el viento a 10 metros
        ds = H.xarray(":(U|V)GRD:10 m above ground:")
        
        # Recorte para Chile (ajustando longitud a formato 0-360)
        ds_chile = ds.sel(
            latitude=slice(NORTE, SUR), 
            longitude=slice(360 + OESTE, 360 + ESTE)
        )

        # Preparar estructura para el mapa (Leaflet-Velocity)
        u_data = ds_chile.u10.values
        v_data = ds_chile.v10.values
        
        meteo_json = [
            {
                "header": {
                    "parameterCategory": 2, "parameterNumber": 2, 
                    "lo1": OESTE, "la1": NORTE,
                    "dx": 0.25, "dy": 0.25,
                    "nx": len(ds_chile.longitude), "ny": len(ds_chile.latitude),
                    "refTime": str(ds.time.values)
                },
                "data": u_data.flatten().tolist()
            },
            {
                "header": {
                    "parameterCategory": 2, "parameterNumber": 3, 
                    "lo1": OESTE, "la1": NORTE,
                    "dx": 0.25, "dy": 0.25,
                    "nx": len(ds_chile.longitude), "ny": len(ds_chile.latitude),
                    "refTime": str(ds.time.values)
                },
                "data": v_data.flatten().tolist()
            }
        ]

        # Crear carpeta de datos y guardar
        os.makedirs('datos', exist_ok=True)
        with open('datos/viento_chile.json', 'w') as f:
            json.dump(meteo_json, f)
        
        print("✅ MetCam: Datos actualizados correctamente.")

    except Exception as e:
        print(f"❌ Error en MetCam: {e}")

if __name__ == "__main__":
    generar_datos_metcam()
