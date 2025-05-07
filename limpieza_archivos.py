import os
import re
import glob

def limpiar_archivo(ruta_archivo):
    """
    Limpia un archivo de texto:
    - Elimina la primera línea
    - Elimina la línea que contiene "reviews" y todo lo que está debajo
    """
    try:
        # Leer el archivo
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            lineas = archivo.readlines()
        
        if not lineas:
            print(f"El archivo {ruta_archivo} está vacío")
            return
        
        # Eliminar la primera línea
        lineas = lineas[1:]
        
        # Buscar la línea que contiene "reviews"
        indice_reviews = None
        for i, linea in enumerate(lineas):
            if re.search(r'\d+,?\d*\s+reviews', linea, re.IGNORECASE):
                indice_reviews = i
                break
        
        # Si encontramos la línea, eliminamos desde ahí hasta el final
        if indice_reviews is not None:
            lineas = lineas[:indice_reviews]
        
        # Guardar el archivo con los cambios
        with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
            archivo.writelines(lineas)
        
        print(f"Archivo {ruta_archivo} procesado correctamente")
    
    except Exception as e:
        print(f"Error al procesar el archivo {ruta_archivo}: {str(e)}")

def procesar_carpeta(ruta_carpeta):
    """
    Procesa todos los archivos .txt en la carpeta especificada
    """
    # Obtener la lista de archivos .txt en la carpeta
    patron_busqueda = os.path.join(ruta_carpeta, "*.txt")
    archivos = glob.glob(patron_busqueda)
    
    if not archivos:
        print(f"No se encontraron archivos .txt en la carpeta {ruta_carpeta}")
        return
    
    print(f"Se encontraron {len(archivos)} archivos para procesar")
    
    # Procesar cada archivo
    for archivo in archivos:
        limpiar_archivo(archivo)
    
    print("Procesamiento completado")

if __name__ == "__main__":
    # Ruta de la carpeta con los archivos (modifica si es necesario)
    carpeta_data = "data"
    
    # Verificar si la carpeta existe
    if not os.path.exists(carpeta_data):
        print(f"La carpeta {carpeta_data} no existe")
    else:
        procesar_carpeta(carpeta_data)