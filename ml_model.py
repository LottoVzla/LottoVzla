import os
import numpy as np
from sqlalchemy.orm import Session
import models

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

MODEL_PATH = "lstm_lotto.h5"
SEQ_LENGTH = 10 # Usaremos los últimos 10 resultados para predecir el siguiente
NUM_CLASSES = 38 # 0-36 + 00

# Mapeo de animales a índices numéricos para la red neuronal
RULETA = ["0", "28", "9", "26", "30", "11", "7", "20", "32", "17", "5", "22", "34", "15", "3", "24", "36", "13", "1", "00", "27", "10", "25", "29", "12", "8", "19", "31", "18", "6", "21", "33", "16", "4", "23", "35", "14", "2"]
MAPPING = {animal: idx for idx, animal in enumerate(RULETA)}
INV_MAPPING = {idx: animal for idx, animal in enumerate(RULETA)}

def prepare_data(history):
    """ Convierte el historial de la BD en secuencias X e Y para entrenar """
    data = [MAPPING[r.animal_number] for r in history if r.animal_number in MAPPING]
    
    X, y = [], []
    for i in range(len(data) - SEQ_LENGTH):
        X.append(data[i:i+SEQ_LENGTH])
        y.append(data[i+SEQ_LENGTH])
        
    X = np.array(X)
    # Reformatear para LSTM: [samples, time steps, features]
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    # Normalizar (opcional, pero útil para LSTM)
    X = X / float(NUM_CLASSES)
    
    y = tf.keras.utils.to_categorical(y, num_classes=NUM_CLASSES)
    return X, y

def train_lstm_model(db: Session):
    if not TF_AVAILABLE:
        return "TensorFlow no está instalado."
        
    history = db.query(models.Result).order_by(models.Result.id.asc()).all()
    if len(history) < SEQ_LENGTH * 2:
        return "No hay suficientes datos para entrenar el modelo LSTM."
        
    X, y = prepare_data(history)
    
    model = Sequential()
    model.add(LSTM(64, return_sequences=True, input_shape=(SEQ_LENGTH, 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(64))
    model.add(Dropout(0.2))
    model.add(Dense(NUM_CLASSES, activation='softmax'))
    
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    
    # Entrenar (epocas bajas por ahora para evitar saturar el CPU)
    model.fit(X, y, epochs=10, batch_size=32, verbose=0)
    
    model.save(MODEL_PATH)
    return "Modelo LSTM entrenado y guardado correctamente."

def predict_lstm(db: Session, limit=3):
    if not TF_AVAILABLE or not os.path.exists(MODEL_PATH):
        return []
        
    history = db.query(models.Result).order_by(models.Result.id.desc()).limit(SEQ_LENGTH).all()
    history = history[::-1] # Invertir para orden cronológico
    
    if len(history) < SEQ_LENGTH:
        return []
        
    data = [MAPPING[r.animal_number] for r in history if r.animal_number in MAPPING]
    if len(data) < SEQ_LENGTH:
        return []
        
    X_pred = np.array(data)
    X_pred = np.reshape(X_pred, (1, SEQ_LENGTH, 1))
    X_pred = X_pred / float(NUM_CLASSES)
    
    model = load_model(MODEL_PATH)
    predictions = model.predict(X_pred, verbose=0)[0]
    
    # Obtener los top N índices
    top_indices = predictions.argsort()[-limit:][::-1]
    
    return [INV_MAPPING[idx] for idx in top_indices]
