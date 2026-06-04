import random
import datetime
from sqlalchemy.orm import Session
from collections import Counter
import models

# Rueda de 38 animales (0, 00, 1-36)
RULETA = ["0", "28", "9", "26", "30", "11", "7", "20", "32", "17", "5", "22", "34", "15", "3", "24", "36", "13", "1", "00", "27", "10", "25", "29", "12", "8", "19", "31", "18", "6", "21", "33", "16", "4", "23", "35", "14", "2"]

def strategy_ruleta_espacial(history, limit=3):
    """ Motor 1 (45%): Distancias 4, 7, 10, 14 """
    if not history: return random.sample(RULETA, limit)
    
    last_num = history[-1].animal_number
    if last_num not in RULETA: return random.sample(RULETA, limit)
    
    idx = RULETA.index(last_num)
    n = len(RULETA)
    
    candidatos = []
    for d in [4, 7, 10, 14]:
        candidatos.extend([RULETA[(idx + d) % n], RULETA[(idx - d) % n]])
        
    counts = Counter(candidatos)
    return [num for num, count in counts.most_common(limit)]

def strategy_frecuencia_diaria(history_today, limit=3):
    """ Motor 2 (15%): Animales más salidores del día """
    if not history_today: return []
    counts = Counter([r.animal_number for r in history_today])
    return [num for num, count in counts.most_common(limit)]

def strategy_ciclos_transicion(history_all, last_num, limit=3):
    """ Motor 3 (10%): Qué número sale después del último número """
    if not history_all or not last_num: return []
    siguientes = []
    for i in range(len(history_all) - 1):
        if history_all[i].animal_number == last_num:
            siguientes.append(history_all[i+1].animal_number)
    
    counts = Counter(siguientes)
    return [num for num, count in counts.most_common(limit)]

def strategy_termometro(history_all, limit=3):
    """ Motor 4 (5%): Números Calientes (más frecuentes globales) """
    if not history_all: return []
    counts = Counter([r.animal_number for r in history_all])
    return [num for num, count in counts.most_common(limit)]

def strategy_piramide(limit=3):
    """ Motor 5 (5%): Pirámide Numerológica del día """
    today = datetime.date.today().strftime("%d%m%Y")
    # Algoritmo simple de reducción
    row = [int(x) for x in today]
    while len(row) > 2:
        new_row = []
        for i in range(len(row) - 1):
            s = row[i] + row[i+1]
            new_row.append(s if s < 10 else s - 9)
        row = new_row
    
    base_num = str(row[0]) + str(row[1])
    # Buscar animales que contengan este dígito
    candidatos = [r for r in RULETA if str(row[0]) in r or str(row[1]) in r]
    if not candidatos: return random.sample(RULETA, limit)
    return random.sample(candidatos, min(limit, len(candidatos)))

def strategy_suma_aritmetica(history, limit=3):
    """ Motor 6 (5%): Suma de los últimos 2 sorteos """
    if len(history) < 2: return []
    try:
        n1 = int(history[-1].animal_number) if history[-1].animal_number != "00" else 37
        n2 = int(history[-2].animal_number) if history[-2].animal_number != "00" else 37
        s = (n1 + n2) % 38
        res = "00" if s == 37 else str(s)
        return [res]
    except:
        return []

def strategy_ecos_tiempo(history, limit=3):
    """ Motor 7 (5%): Rezagos temporales """
    # Retorna números que salieron hace exactamente 24 horas (ayer a la misma hora)
    # Por ahora mock simplificado
    return []

def strategy_lstm(db: Session, limit=3):
    """ 
    Motor 8 (8%): Red Neuronal LSTM.
    Usa el modelo pre-entrenado en Keras para predecir.
    """
    try:
        from .ml_model import predict_lstm
        return predict_lstm(db, limit=limit)
    except Exception as e:
        print(f"Error LSTM: {e}")
        return []

def calculate_best_predictions(db: Session, current_hour: str):
    """ Integrador de todas las estrategias con pesos """
    
    # Obtener historial completo y del día
    history_all = db.query(models.Result).order_by(models.Result.id.asc()).all()
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    history_today = [r for r in history_all if r.date == today_str]
    
    if not history_all:
        return random.sample(RULETA, 3)

    last_num = history_all[-1].animal_number

    # Ejecutar motores
    m1 = strategy_ruleta_espacial(history_all, 5)
    m2 = strategy_frecuencia_diaria(history_today, 5)
    m3 = strategy_ciclos_transicion(history_all, last_num, 5)
    m4 = strategy_termometro(history_all, 5)
    m5 = strategy_piramide(5)
    m6 = strategy_suma_aritmetica(history_all, 2)
    m8 = strategy_lstm(db, 3) # LSTM Real
    
    # Sistema de puntaje
    scores = {r: 0.0 for r in RULETA}
    
    # Pesos
    def assign_points(lista, peso):
        if not lista: return
        p = peso / len(lista)
        for num in lista:
            if num in scores: scores[num] += p

    assign_points(m1, 45.0)
    assign_points(m2, 15.0)
    assign_points(m3, 10.0)
    assign_points(m4, 5.0)
    assign_points(m5, 5.0)
    assign_points(m6, 5.0)
    assign_points(m8, 8.0) # LSTM

    # Ordenar y obtener los 3 mejores
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [x[0] for x in sorted_scores[:3]]
