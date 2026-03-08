import xarray as xr
import numpy as np
import json
from herbie import Herbie
import os

# Configuración Geográfica de MetCam
NORTE, SUR = -17, -90
OESTE, ESTE = -115, -50

def generar_datos_metcam():
    print("MetCam: Conectando con la NOAA...")
    
    try:
        # 1. Herbie descarga el modelo más reciente disponible
        H = Herbie(product='pgrb2.0p25', model='gfs', fxx=0)
        
        # 2. Leemos U y V (Viento a 10m)
        ds = H.xarray(":(U|V)GRD:10 m above ground:")
        
        # 3. Normalizamos longitudes a -180 a 180 para facilitar el recorte
        ds = ds.assign_coords(longitude=(((ds.longitude + 180) % 360) - 180))
        ds = ds.sortby('longitude')
        ds = ds.sortby('latitude', ascending=False) # Norte a Sur

        # 4. Recorte preciso para Chile y Antártica
        ds_chile = ds.sel(
            latitude=slice(NORTE, SUR), 
            longitude=slice(OESTE, ESTE)
        )

        # 5. Extraer valores (buscando el nombre de la variable automáticamente)
        # Buscamos variables que contengan 'u' y 'v'
        u_var = [v for v in ds_chile.data_vars if v.startswith('u')][0]
        v_var = [v for v in ds_chile.data_vars if v.startswith('v')][0]
        
        u_data = ds_chile[u_var].values
        v_data = ds_chile[v_var].values
        
        # 6. Estructura para Leaflet-Velocity
        meteo_json = [
            {
                "header": {
                    "parameterCategory": 2, "parameterNumber": 2, 
                    "lo1": float(ds_chile.longitude.min()), 
                    "la1": float(ds_chile.latitude.max()),
                    "dx": 0.25, "dy": 0.25,
                    "nx": int(len(ds_chile.longitude)), 
                    "ny": int(len(ds_chile.latitude)),
                    "refTime": str(ds.time.values[0]) if hasattr(ds.time, 'values') else str(ds.time.values)
                },
                "data": np.nan_to_num(u_data).flatten().tolist()
            },
            {
                "header": {
                    "parameterCategory": 2, "parameterNumber": 3, 
                    "lo1": float(ds_chile.longitude.min()), 
                    "la1": float(ds_chile.latitude.max()),
                    "dx": 0.25, "dy": 0.25,
                    "nx": int(len(ds_chile.longitude)), 
                    "ny": int(len(ds_chile.latitude)),
                    "refTime": str(ds.time.values[0]) if hasattr(ds.time, 'values') else str(ds.time.values)
                },
                "data": np.nan_to_num(v_data).flatten().tolist()
            }
        ]

        os.makedirs('datos', exist_ok=True)
        with open('datos/viento_chile.json', 'w') as f:
            json.dump(meteo_json, f)
        
        print("✅ MetCam: ¡Datos actualizados y guardados!")

    except Exception as e:
        print(f"❌ Error crítico en MetCam: {e}")

if __name__ == "__main__":
    generar_datos_metcam()
