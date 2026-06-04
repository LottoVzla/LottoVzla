import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from . import models
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def scrape_results(db: Session):
    url = "https://loteriadehoy.com/animalito/lottoactivo/resultados/"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Lógica de extracción de resultados.
        # Nota: Ajustar selectores según el DOM real de la web.
        # Ejemplo simulado basado en estructuras comunes:
        results = soup.find_all('div', class_='resultado-item') # Ajustar clase real
        
        for item in results:
            time = item.find('span', class_='hora').text.strip()
            animal_text = item.find('span', class_='animal').text.strip()
            # Parsear "00 - BALLENA" -> "00", "BALLENA"
            parts = animal_text.split('-')
            if len(parts) >= 2:
                number = parts[0].strip()
                name = parts[1].strip()
                
                # Guardar animal si no existe
                animal = db.query(models.Animal).filter(models.Animal.number == number).first()
                if not animal:
                    animal = models.Animal(number=number, name=name)
                    db.add(animal)
                    db.commit()
                
                # Guardar resultado del día actual
                import datetime
                today_str = datetime.date.today().strftime("%Y-%m-%d")
                
                existing_result = db.query(models.Result).filter(
                    models.Result.date == today_str,
                    models.Result.time == time
                ).first()
                
                if not existing_result:
                    new_result = models.Result(date=today_str, time=time, animal_number=number)
                    db.add(new_result)
                    db.commit()
                    
        return {"status": "success", "message": "Resultados scrapeados correctamente"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def download_images():
    # En una implementación real se extraen las URLs de las imágenes y se descargan a la carpeta `images`
    pass
