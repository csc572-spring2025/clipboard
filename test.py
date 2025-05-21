import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential, load_model, Model
from tensorflow.keras.layers import (
    Embedding, Bidirectional, LSTM, Dense, Dropout,
    Input, GlobalAveragePooling1D, GlobalMaxPooling1D,
    Concatenate, MultiHeadAttention, LayerNormalization
)
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
import pickle
import os
import sys
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# CONFIGURABLE HYPERPARAMETERS
VOCAB_SIZE    = 50000  # Increased vocabulary size
EMBED_DIM     = 128    # Increased embedding dimension
MAX_LENGTH    = 300    # Increased sequence length
TRUNC_TYPE    = 'post'
PADDING_TYPE  = 'post'
OOV_TOKEN     = "<OOV>"
BATCH_SIZE    = 32     # Smaller batch size for better generalization
EPOCHS        = 50     # More epochs with early stopping
PATIENCE_ES   = 7      # Increased patience for early stopping
PATIENCE_RLR  = 5      # Increased patience for learning rate reduction
LEARNING_RATE = 0.001  # Initial learning rate

# Model and tokenizer paths
MODEL_PATH = "model_best.h5"
TOKENIZER_PATH = "tokenizer.pkl"
LABEL_MAP_PATH = "label_map.pkl"

def preprocess_text(text):
    """Enhanced text preprocessing with error handling"""
    try:
        if not isinstance(text, str):
            text = str(text)
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove special characters and digits
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\d+', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Tokenize
        try:
            tokens = word_tokenize(text)
        except:
            # Fallback to simple split if NLTK fails
            tokens = text.split()
        
        # Remove stopwords
        try:
            stop_words = set(stopwords.words('english'))
            tokens = [token for token in tokens if token not in stop_words]
        except:
            # Continue without stopword removal if it fails
            pass
        
        return ' '.join(tokens)
    except Exception as e:
        print(f"Warning: Error in preprocessing text: {str(e)}")
        return text  # Return original text if preprocessing fails

def augment_text(text):
    """Apply simple text augmentation techniques"""
    augmented = []
    
    # Original text
    augmented.append(text)
    
    # Add some noise
    if len(text) > 10:
        # Add random spaces
        words = text.split()
        if len(words) > 1:
            augmented.append(' '.join(words))
    
    # Add some variations
    if text.islower():
        augmented.append(text.upper())
    elif text.isupper():
        augmented.append(text.lower())
    
    return augmented

def load_and_prepare_data(csv_path):
    """Enhanced data loading and preparation with error handling"""
    try:
        print(f"Loading data from {csv_path}...")
        df = pd.read_csv(csv_path)
        
        if df.empty:
            raise ValueError("Empty dataset loaded")
            
        print("Checking for missing values...")
        if df.isnull().any().any():
            print("Warning: Found null values. Removing them...")
            df = df.dropna()
        
        print("Preprocessing texts...")
        # Preprocess and augment texts
        augmented_data = []
        for _, row in df.iterrows():
            try:
                text = row['text']
                label = row['label']
                
                # Preprocess the original text
                processed_text = preprocess_text(text)
                if processed_text:  # Only add non-empty texts
                    augmented_data.append({
                        'text': processed_text,
                        'label': label
                    })
                    
                    # Add augmented versions
                    for aug_text in augment_text(processed_text):
                        if aug_text != processed_text:  # Don't add duplicates
                            augmented_data.append({
                                'text': aug_text,
                                'label': label
                            })
            except Exception as e:
                print(f"Warning: Error processing row: {str(e)}")
                continue
        
        if not augmented_data:
            raise ValueError("No valid data after preprocessing")
        
        # Convert to DataFrame
        df = pd.DataFrame(augmented_data)
        
        # Create label mappings
        label_set = sorted(set(df['label']))
        label_to_index = {lab:i for i,lab in enumerate(label_set)}
        index_to_label = {i:lab for lab,i in label_to_index.items()}
        
        # Convert texts and labels
        texts = df['text'].tolist()
        y = np.array([label_to_index[lab] for lab in df['label']])
        
        return texts, y, label_to_index, index_to_label
        
    except Exception as e:
        print(f"Error in load_and_prepare_data: {str(e)}")
        raise

def build_model(vocab_size, embed_dim, num_classes):
    """Enhanced model architecture with attention mechanism"""
    # Input layer
    inputs = Input(shape=(MAX_LENGTH,))
    
    # Embedding layer
    x = Embedding(vocab_size, embed_dim, input_length=MAX_LENGTH)(inputs)
    
    # Bidirectional LSTM layers
    x = Bidirectional(LSTM(embed_dim, return_sequences=True))(x)
    x = LayerNormalization()(x)
    
    # Multi-head attention
    attention_output = MultiHeadAttention(
        num_heads=4, key_dim=embed_dim
    )(x, x)
    x = LayerNormalization()(attention_output + x)
    
    # Second LSTM layer
    x = Bidirectional(LSTM(embed_dim, return_sequences=True))(x)
    x = LayerNormalization()(x)
    
    # Global pooling
    avg_pool = GlobalAveragePooling1D()(x)
    max_pool = GlobalMaxPooling1D()(x)
    x = Concatenate()([avg_pool, max_pool])
    
    # Dense layers with dropout
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = LayerNormalization()(x)
    
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.3)(x)
    x = LayerNormalization()(x)
    
    # Output layer
    outputs = Dense(num_classes, activation='softmax')(x)
    
    # Create model
    model = Model(inputs=inputs, outputs=outputs)
    
    # Compile model with custom learning rate
    optimizer = Adam(learning_rate=LEARNING_RATE)
    model.compile(
        optimizer=optimizer,
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def train_and_save_model(csv_path='training_data_enhanced.csv'):
    """Train model with enhanced error handling"""
    try:
        print("Loading and preparing data...")
        texts, y, label_to_index, index_to_label = load_and_prepare_data(csv_path)
        
        print(f"Total training examples: {len(texts)}")
        print("Category distribution:")
        for label, idx in label_to_index.items():
            count = sum(y == idx)
            print(f"{label}: {count} examples")
        
        if len(texts) < 10:
            raise ValueError("Insufficient training data")
        
        # Tokenize + pad
        print("\nTokenizing texts...")
        tok = Tokenizer(num_words=VOCAB_SIZE, oov_token=OOV_TOKEN)
        tok.fit_on_texts(texts)
        seqs = tok.texts_to_sequences(texts)
        padded = pad_sequences(seqs, maxlen=MAX_LENGTH, padding=PADDING_TYPE, truncating=TRUNC_TYPE)

        # Split data with stratification
        print("Splitting data...")
        X_train, X_val, y_train, y_val = train_test_split(
            padded, y, 
            test_size=0.2, 
            random_state=42,
            stratify=y
        )

        print("\nBuilding model...")
        model = build_model(VOCAB_SIZE, EMBED_DIM, len(label_to_index))

        # Enhanced callbacks
        es = EarlyStopping(
            monitor='val_loss',
            patience=PATIENCE_ES,
            restore_best_weights=True,
            verbose=1
        )
        
        mc = ModelCheckpoint(
            MODEL_PATH,
            monitor='val_loss',
            save_best_only=True,
            verbose=1
        )
        
        rlr = ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=PATIENCE_RLR,
            min_lr=1e-6,
            verbose=1
        )

        print("\nTraining model...")
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            callbacks=[es, mc, rlr],
            verbose=1
        )

        # Save tokenizer and label map
        print("\nSaving model and supporting files...")
        with open(TOKENIZER_PATH, 'wb') as f:
            pickle.dump(tok, f)
        with open(LABEL_MAP_PATH, 'wb') as f:
            pickle.dump(index_to_label, f)
        
        return history
        
    except Exception as e:
        print(f"Error in train_and_save_model: {str(e)}")
        raise

# Globals for ease of use
_model = None
_tokenizer = None
_index_to_label = None

def initialize_categorizer(*args, **kwargs):
    """Load the pre-trained model, tokenizer, and label map"""
    global _model, _tokenizer, _index_to_label
    
    try:
        # Check if model files exist
        if not all(os.path.exists(p) for p in [MODEL_PATH, TOKENIZER_PATH, LABEL_MAP_PATH]):
            print("Model files not found. Training new model...")
            train_and_save_model()
        
        # Load the model and supporting files
        print("Loading model files...")
        _model = load_model(MODEL_PATH)
        with open(TOKENIZER_PATH, 'rb') as f:
            _tokenizer = pickle.load(f)
        with open(LABEL_MAP_PATH, 'rb') as f:
            _index_to_label = pickle.load(f)
        print("Model loaded successfully!")
        
    except Exception as e:
        print(f"Error in initialize_categorizer: {str(e)}")
        raise

def categorize_text_deep(text: str) -> str:
    """Enhanced text categorization with preprocessing"""
    if _model is None or _tokenizer is None:
        raise RuntimeError("Model not initialized. Call initialize_categorizer() first.")
    
    # Preprocess the input text
    processed_text = preprocess_text(text)
    
    # Tokenize and pad
    seq = _tokenizer.texts_to_sequences([processed_text])
    pad = pad_sequences(seq, maxlen=MAX_LENGTH, padding=PADDING_TYPE, truncating=TRUNC_TYPE)
    
    # Get prediction
    pred = _model.predict(pad, verbose=0)
    return _index_to_label[np.argmax(pred)]

if __name__ == "__main__":
    # Only train if explicitly called
    if len(sys.argv) > 1 and sys.argv[1] == "--train":
        train_and_save_model()
    else:
        initialize_categorizer()
    samples = [
        "def fib(n): return fib(n-1) + fib(n-2) if n>1 else n",
        "\\int_0^\\infty e^{-x} dx",
        "https://openai.com/blog/",
        "Life is what happens when you're busy making other plans."
    ]
    for s in samples:
        print(f"{s}\n → {categorize_text_deep(s)}\n")
