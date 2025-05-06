import time
import os
import asyncio
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

def extract_urls_from_sitemap(sitemap_url):
    urls = []
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        sitemaps = root.findall('.//ns:sitemap', namespace)
        if sitemaps:
            for sitemap in sitemaps:
                loc = sitemap.find('./ns:loc', namespace)
                if loc is not None and loc.text:
                    child_urls = extract_urls_from_sitemap(loc.text)
                    urls.extend(child_urls)
        else:
            url_elements = root.findall('.//ns:url/ns:loc', namespace)
            for url_elem in url_elements:
                if url_elem.text:
                    urls.append(url_elem.text)
                    
        return urls
    except Exception as e:
        print(f"Error al procesar sitemap {sitemap_url}: {e}")
        return []

async def extract_static_text_playwright(url, output_dir="/app/data"):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Navegar a la URL
            await page.goto(url, wait_until="networkidle")
            
            # Obtener contenido renderizado
            content = await page.content()
            await browser.close()
            
            # Procesar con BeautifulSoup
            soup = BeautifulSoup(content, 'lxml')
            
            # Eliminar elementos no deseados
            for element in soup(['script', 'style', 'noscript', 'iframe']):
                element.decompose()
                
            # Extraer texto estructurado
            all_text = ""
            
            # Título de la página
            title = soup.find('title')
            if title and title.text:
                all_text += f"# {title.text.strip()}\n\n"
            
            # Extraer textos por tipos de elementos
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'li', 'a', 'div', 'span']:
                elements = soup.find_all(tag)
                for el in elements:
                    text = el.get_text(strip=True)
                    if text and len(text) > 1:  # Ignorar textos muy cortos
                        if tag.startswith('h'):
                            level = int(tag[1])
                            prefix = '#' * level
                            all_text += f"\n\n{prefix} {text}\n"
                        elif tag == 'p':
                            all_text += f"\n{text}\n"
                        elif tag == 'li':
                            all_text += f"\n- {text}"
                        else:
                            all_text += f"{text}\n"
            
            # Limpiar líneas duplicadas
            lines = all_text.split('\n')
            clean_lines = []
            prev_line = ""
            
            for line in lines:
                line = line.strip()
                if line and line != prev_line:
                    clean_lines.append(line)
                    prev_line = line
                    
            clean_text = '\n'.join(clean_lines)
            
            # Crear nombre de archivo
            parsed_url = urlparse(url)
            path = parsed_url.path.strip('/')
            if path:
                filename = f"{path.replace('/', '_')}.txt"
            else:
                filename = "index.txt"
                
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, filename)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(clean_text)
                
            print(f"Texto extraído de {url} guardado en {file_path}")
            return clean_text, file_path
            
    except Exception as e:
        print(f"Error al extraer texto de {url}: {e}")
        return None, None

async def main():
    sitemap_url = "https://www.serviexpress.net.co/sitemap_index.xml"
    output_dir = "/app/data"
    
    os.makedirs(output_dir, exist_ok=True)
    
    if os.path.exists(f"{output_dir}/extraction_completed.txt"):
        print("Los datos ya fueron extraídos. Contenedor mantenido activo.")
        while True:
            await asyncio.sleep(3600)
    
    print(f"Extrayendo URLs del sitemap {sitemap_url}...")
    urls = extract_urls_from_sitemap(sitemap_url)
    
    print(f"Se encontraron {len(urls)} URLs en el sitemap.")
    
    with open(f"{output_dir}/all_urls.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(urls))
    
    for i, url in enumerate(urls):
        print(f"Procesando {i+1}/{len(urls)}: {url}")
        await extract_static_text_playwright(url, output_dir)
        await asyncio.sleep(2)
    
    with open(f"{output_dir}/extraction_completed.txt", "w") as f:
        f.write("Extracción completada el " + time.strftime("%Y-%m-%d %H:%M:%S"))
    
    print(f"Proceso completado. Se extrajeron {len(urls)} páginas.")
    print("Contenedor mantenido activo.")
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())