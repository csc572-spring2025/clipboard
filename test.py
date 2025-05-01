import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, GlobalAveragePooling1D, Dense
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

def load_and_prepare_data(csv_path):
    """
    Loads text and label data from a CSV file.

    CSV must contain 'text' and 'label' columns.
    """
    df = pd.read_csv(csv_path)
    df.dropna(subset=['text', 'label'], inplace=True)

    texts = df['text'].astype(str).tolist()
    labels = df['label'].astype(str).tolist()

    label_set = sorted(set(labels))
    label_to_index = {label: i for i, label in enumerate(label_set)}
    index_to_label = {i: label for label, i in label_to_index.items()}
    y = np.array([label_to_index[label] for label in labels])

    return texts, y, label_to_index, index_to_label

def build_and_train_model(texts, labels, vocab_size=10000, max_length=100):
    tokenizer = Tokenizer(num_words=vocab_size, oov_token="<OOV>")
    tokenizer.fit_on_texts(texts)
    sequences = tokenizer.texts_to_sequences(texts)
    padded_sequences = pad_sequences(sequences, maxlen=max_length, padding='post')

    X_train, X_val, y_train, y_val = train_test_split(padded_sequences, labels, test_size=0.2, random_state=42)

    model = Sequential([
        Embedding(vocab_size, 32),
        GlobalAveragePooling1D(),
        Dense(32, activation='relu'),
        Dense(len(set(labels)), activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    model.fit(X_train, y_train, epochs=10, validation_data=(X_val, y_val), verbose=1)

    return model, tokenizer

# Global variables for reuse
model = None
tokenizer = None
index_to_label = None
MAX_LEN = 100

def initialize_categorizer(csv_path='training_data.csv'):
    global model, tokenizer, index_to_label, MAX_LEN
    texts, y, _, index_to_label = load_and_prepare_data(csv_path)
    model, tokenizer = build_and_train_model(texts, y, max_length=MAX_LEN)

def categorize_text_deep(text: str) -> str:
    """
    Predicts the category of the input string using the trained model.
    """
    if model is None or tokenizer is None:
        raise Exception("Model not initialized. Call initialize_categorizer() first.")

    seq = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(seq, maxlen=MAX_LEN, padding='post')
    pred = model.predict(padded, verbose=0)
    return index_to_label[np.argmax(pred)]

# Example usage
if __name__ == "__main__":
    initialize_categorizer("training_data.csv")

    test_samples = [
        "def multiply(a, b): return a * b",
        "\\sum_{i=1}^{n} i^2",
        "Visit https://example.com",
        "Happiness is only real when shared."
    ]

    for sample in test_samples:
        print(f"{sample}\n → Category: {categorize_text_deep(sample)}\n")
