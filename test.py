import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, GlobalAveragePooling1D, Dense
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Training data
TRAIN_DATA = [
    # Quotes
    ("To be or not to be, that is the question.", "quote"),
    ("Life is what happens when you're busy making other plans.", "quote"),
    
    # URLs
    ("https://www.example.com", "url"),
    ("Check out http://openai.com for more info", "url"),
    
    # Code
    ("def hello():\n    print('Hello')", "code"),
    ("for i in range(10): print(i)", "code"),

    # LaTeX
    ("\\frac{a}{b}", "latex"),
    ("E = mc^2 \\text{ is a famous equation}", "latex"),
    
    # Plain text
    ("I had lunch with John yesterday.", "text"),
    ("The weather is nice today.", "text"),
]

# Extract texts and labels
texts, labels = zip(*TRAIN_DATA)
label_set = sorted(set(labels))
label_to_index = {label: i for i, label in enumerate(label_set)}
index_to_label = {i: label for label, i in label_to_index.items()}
y = np.array([label_to_index[label] for label in labels])

# Tokenize text
tokenizer = Tokenizer()
tokenizer.fit_on_texts(texts)
X = tokenizer.texts_to_sequences(texts)
X = pad_sequences(X, padding='post')

# Build the model
model = Sequential([
    Embedding(input_dim=len(tokenizer.word_index)+1, output_dim=16),
    GlobalAveragePooling1D(),
    Dense(16, activation='relu'),
    Dense(len(label_set), activation='softmax')
])
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(X, y, epochs=30, verbose=0)

def categorize_text_deep(text: str) -> str:
    """
    Categorize input text using a deep learning model.

    Parameters:
        text (str): Input string to classify.

    Returns:
        str: Predicted category.
    """
    seq = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(seq, maxlen=X.shape[1], padding='post')
    pred = model.predict(padded, verbose=0)
    return index_to_label[np.argmax(pred)]

# Example usage
if __name__ == "__main__":
    samples = [
        "https://github.com/openai",
        "def foo(x): return x * x",
        "\\sum_{i=1}^{n} i^2",
        "It is during our darkest moments that we must focus to see the light.",
        "What's your plan for the weekend?"
    ]
    for s in samples:
        print(f"{s}\n → Category: {categorize_text_deep(s)}\n")
