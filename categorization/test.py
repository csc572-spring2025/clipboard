import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Bidirectional, LSTM, GlobalAveragePooling1D, Dense, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from sklearn.model_selection import train_test_split

# CONFIGURABLE HYPERPARAMETERS
VOCAB_SIZE    = 30000
EMBED_DIM     = 64
MAX_LENGTH    = 250
TRUNC_TYPE    = 'post'
PADDING_TYPE  = 'post'
OOV_TOKEN     = "<OOV>"
BATCH_SIZE    = 64
EPOCHS        = 40
PATIENCE_ES   = 5   # early stopping
PATIENCE_RLR  = 3   # reduce LR

def load_and_prepare_data(csv_path):
    df = pd.read_csv(csv_path)
    df.dropna(subset=['text','label'], inplace=True)
    texts = df['text'].astype(str).tolist()
    labels = df['label'].astype(str).tolist()
    label_set = sorted(set(labels))
    label_to_index = {lab:i for i,lab in enumerate(label_set)}
    index_to_label = {i:lab for lab,i in label_to_index.items()}
    y = np.array([label_to_index[lab] for lab in labels])
    return texts, y, label_to_index, index_to_label

def build_model(vocab_size, embed_dim, num_classes):
    m = Sequential([
        Embedding(vocab_size, embed_dim, input_length=MAX_LENGTH),
        Bidirectional(LSTM(embed_dim, return_sequences=True)),
        GlobalAveragePooling1D(),
        Dropout(0.5),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])
    m.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    return m

def build_and_train_model(texts, labels, index_to_label, csv_prefix="model"):
    # Tokenize + pad
    tok = Tokenizer(num_words=VOCAB_SIZE, oov_token=OOV_TOKEN)
    tok.fit_on_texts(texts)
    seqs = tok.texts_to_sequences(texts)
    padded = pad_sequences(seqs, maxlen=MAX_LENGTH, padding=PADDING_TYPE, truncating=TRUNC_TYPE)

    X_train, X_val, y_train, y_val = train_test_split(padded, labels, test_size=0.2, random_state=42)

    model = build_model(VOCAB_SIZE, EMBED_DIM, len(index_to_label))

    # Callbacks
    es = EarlyStopping(monitor='val_loss', patience=PATIENCE_ES, restore_best_weights=True)
    mc = ModelCheckpoint(f"{csv_prefix}_best.h5", monitor='val_loss', save_best_only=True)
    rlr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=PATIENCE_RLR, min_lr=1e-6)

    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=[es, mc, rlr],
        verbose=1
    )

    return model, tok, history

# Globals for ease of use
_model = None
_tokenizer = None
_index_to_label = None

def initialize_categorizer(csv_path='training_data_3000.csv'):
    global _model, _tokenizer, _index_to_label
    texts, y, _, _index_to_label = load_and_prepare_data(csv_path)
    _model, _tokenizer, _ = build_and_train_model(texts, y, _index_to_label)

def categorize_text_deep(text: str) -> str:
    if _model is None or _tokenizer is None:
        raise RuntimeError("Model not initialized. Call initialize_categorizer() first.")
    seq = _tokenizer.texts_to_sequences([text])
    pad = pad_sequences(seq, maxlen=MAX_LENGTH, padding=PADDING_TYPE, truncating=TRUNC_TYPE)
    pred = _model.predict(pad, verbose=0)
    return _index_to_label[np.argmax(pred)]

if __name__ == "__main__":
    initialize_categorizer("training_data_3000.csv")
    samples = [
        "def fib(n): return fib(n-1) + fib(n-2) if n>1 else n",
        "\\int_0^\\infty e^{-x} dx",
        "https://openai.com/blog/",
        "Life is what happens when you're busy making other plans."
    ]
    for s in samples:
        print(f"{s}\n → {categorize_text_deep(s)}\n")
