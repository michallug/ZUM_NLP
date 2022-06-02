# -*- coding: utf-8 -*-
"""ZUM_proj2_NLP.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jD8YT60iQDa703lLt9s0pd479j4CZzTl
"""

# pomocnicze
import re
import numpy as np
import pandas as pd
import string
# wizualizacja
import seaborn as sns
from wordcloud import WordCloud
import matplotlib.pyplot as plt
# nltk - do preprocessingu
import nltk
from nltk.stem import WordNetLemmatizer
import spacy
# sklearn - modele do ML
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import BernoulliNB
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import confusion_matrix, classification_report
# preprocessing
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize.treebank import TreebankWordDetokenizer
import gensim
from gensim.utils import simple_preprocess

# model
import tensorflow as tf
import keras
from keras.models import Sequential
from keras import layers
from tensorflow.keras.optimizers import RMSprop, Adam
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras import regularizers
from keras import backend as K
from keras.callbacks import ModelCheckpoint
from sklearn.model_selection import train_test_split

!python -m pip install spacy==2.3.2 -q

!python -m spacy download en_core_web_md

#1B – gotowe dane
dataset = pd.read_csv('Twitter_Data_KAGGLE.csv', index_col=False)
dataset.sample(5) # wyświetl N przykładowych wierszy

# podział danych względem kategorii/sentymentu
# negative(-1), neutral(0), and positive(+1)
data_pos = dataset[dataset['category'] == 1]
data_neg = dataset[dataset['category'] == -1]
data_neu = dataset[dataset['category'] == 0]

# ograniczenie danych do modelowania
data_pos = data_pos.iloc[:50000]
data_neg = data_neg.iloc[:50000]
data_neu = data_neu.iloc[:50000]

dataset = pd.concat([data_pos, data_neg, data_neu])

# Pre-processing danych
# usuwanie NULLi
dataset.dropna(inplace=True)

# zamiana na małe litery
dataset['clean_text'] = dataset['clean_text'].str.lower() # za pomocą klasy string
dataset['clean_text'].head()

# usuwanie stowords
# po instalacji spacy, uruchomić ponownie środowisko wykonawcze
nlp = spacy.load('en_core_web_md')
stopwordlist = nlp.Defaults.stop_words

def cleaning_stopwords(text):
    return " ".join([word for word in str(text).split() if word not in stopwordlist])

dataset['clean_text'] = dataset['clean_text'].apply(cleaning_stopwords)
dataset['clean_text'].head()

# usuwanie znakow interpunkcyjnych
punctuations_list = string.punctuation
punctuations_list += ('“')

def cleaning_punctuations(text):
    translator = str.maketrans('', '', punctuations_list)
    return text.translate(translator)

dataset['clean_text'] = dataset['clean_text'].apply(cleaning_punctuations)
dataset['clean_text'].head()

# usuwanie znaków
def clean_sings(text):
  text = text.replace('ï', '')
  text = text.replace('½', '')
  return text.replace('¿', '')

dataset['clean_text'] = dataset['clean_text'].apply(clean_sings)
dataset['clean_text'].head()

# usuwanie powtarzających się znaków
def cleaning_repeating_char(text):
    return re.sub(r'(.)1+', r'1', text)

# usuwanie linków
def cleaning_URLs(data):
    return re.sub('((www.[^s]+)|(https?://[^s]+))',' ',data)

# usuwanie liczb
def cleaning_numbers(data):
    return re.sub('[0-9]+', '', data)
  
dataset['clean_text'] = dataset['clean_text'].apply(cleaning_repeating_char)
dataset['clean_text'] = dataset['clean_text'].apply(cleaning_URLs)
dataset['clean_text'] = dataset['clean_text'].apply(cleaning_numbers)  

dataset['clean_text'].tail()

# lematyzacja
import nltk
nltk.download('wordnet')

lm = nltk.WordNetLemmatizer()
def lemmatizer_on_text(data):
    text = [lm.lemmatize(word) for word in data]
    return data
dataset['clean_text'] = dataset['clean_text'].apply(lemmatizer_on_text)
dataset['clean_text'].head()

# wycięcie danych dla klasy negative i positive do klasycznego ML
data = dataset.copy()
data.loc[data.index.isin([-1,1])]
#negative(-1), neutral(0), and positive(+1)
data['category'] = data['category'].replace(-1,0) # zamiana etykiety

X = data.clean_text
y = data.category
print(X.head())
print(y.head())

# chmura tagów
data_neg = dataset['clean_text']
plt.figure(figsize = (15,15))
wc = WordCloud(max_words = 1000 , width = 1600 , height = 800,
               collocations=False).generate(" ".join(data_neg))
plt.imshow(wc)

data_pos = dataset['clean_text']
plt.figure(figsize = (15,15))
wc = WordCloud(max_words = 1000 , width = 1600 , height = 800,
               collocations=False).generate(" ".join(data_pos))
plt.imshow(wc)

# podział danych
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

# Zamiana na wektory z użyciem TF-IDF Vectorizer
vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=500000)
vectorizer.fit(X_train)
print('No. of feature_words: ', len(vectorizer.get_feature_names()))

X_train = vectorizer.transform(X_train)
X_test  = vectorizer.transform(X_test)

print(X_train)

# Ewaluacja modelu - funkcja
def model_Evaluate(model):
  # Predykcja danych na danych testowych
  y_pred = model.predict(X_test)

  # Wyświetlenie metryk ewaluacji na podstawie predykcji i ground truth (faktycznych etykiet)
  print(classification_report(y_test, y_pred))

  # Obliczamy i wyświetlamy confusion matrix
  cf_matrix = confusion_matrix(y_test, y_pred)
  #print(cf_matrix.shape)
  categories = ['Negative','Positive']
  group_names = ['True Neg','False Pos', 'False Neg','True Pos']
  group_percentages = ['{0:.2%}'.format(value) for value in cf_matrix.flatten() / np.sum(cf_matrix)]
  labels = [f'{v1}n{v2}' for v1, v2 in zip(group_names, group_percentages)]
  labels = np.asarray(labels).reshape(2,2)
  #print(labels.shape)
  sns.heatmap(cf_matrix, annot = labels, cmap = 'Blues',fmt = '',
  xticklabels = categories, yticklabels = categories)
  plt.xlabel("Predicted values", fontdict = {'size':14}, labelpad = 10)
  plt.ylabel("Actual values" , fontdict = {'size':14}, labelpad = 10)
  plt.title ("Confusion Matrix", fontdict = {'size':18}, pad = 20)

# ETAP 2: KLASYCZNY ML

# Naive Bayes - Bernoulli
BNBmodel = BernoulliNB()
BNBmodel.fit(X_train, y_train)
model_Evaluate(BNBmodel)
y_pred1 = BNBmodel.predict(X_test)

from sklearn.metrics import roc_curve, auc

fpr, tpr, thresholds = roc_curve(y_test, y_pred1)
roc_auc = auc(fpr, tpr)
plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=1, label='ROC curve (area = %0.2f)' % roc_auc)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC CURVE')
plt.legend(loc="lower right")
plt.show()

# Linear Suppor Vector
SVCmodel = LinearSVC()
SVCmodel.fit(X_train, y_train)
model_Evaluate(SVCmodel)
y_pred2 = SVCmodel.predict(X_test)

fpr, tpr, thresholds = roc_curve(y_test, y_pred2)
roc_auc = auc(fpr, tpr)
plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=1, label='ROC curve (area = %0.2f)' % roc_auc)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC CURVE')
plt.legend(loc="lower right")
plt.show()

# Logistic Regression
LRmodel = LogisticRegression()
LRmodel.fit(X_train, y_train)
model_Evaluate(LRmodel)
y_pred3 = LRmodel.predict(X_test)

fpr, tpr, thresholds = roc_curve(y_test, y_pred3)
roc_auc = auc(fpr, tpr)
plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=1, label='ROC curve (area = %0.2f)' % roc_auc)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC CURVE')
plt.legend(loc="lower right")
plt.show()

# ETAP 3: MODEL NN

def clean_data(data):
    
    # Usuwanie url
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    data = url_pattern.sub(r'', data)

    # Usuwanie emaili
    data = re.sub('\S*@\S*\s?', '', data)

    # Usuwanie znaków nowej linii
    data = re.sub('\n', ' ', data)

    # Usuwanie apostrofów
    data = re.sub("\'", "", data)
        
    return data

temp = []

data_to_list = dataset['clean_text'].values.tolist()
for i in range(len(data_to_list)):
    temp.append(clean_data(data_to_list[i]))
list(temp[:5])

def sent_to_words(sentences):
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations
        

data_words = list(sent_to_words(temp))

print(data_words[:10])

for i in range(len(data_words)):
  data_words[i] = [word for word in data_words[i] if word not in stopwordlist]

print(data_words[:10])

def detokenize(text):
    return TreebankWordDetokenizer().detokenize(text)

data = []
for i in range(len(data_words)):
    data.append(detokenize(data_words[i]))
print(data[:5])

# negative(-1), neutral(0), and positive(+1)
dataset['category'] = dataset['category'].replace(1,2) # zamieniamy etykiety
dataset['category'] = dataset['category'].replace(0,1) # zamieniamy etykiety
dataset['category'] = dataset['category'].replace(-1,0) # zamieniamy etykiety
# po: negative(0), neutral(1), and positive(2)

X = dataset.clean_text
y = dataset.category
print(X.head())
print(y.head())
print(dataset.category.unique())

labels = tf.keras.utils.to_categorical(y, 3, dtype="float32")
print(labels)

len(labels) == len(data_words)

# Zamiana danych na tensory
max_words = 5000
max_len = 200

tokenizer = Tokenizer(num_words=max_words)
tokenizer.fit_on_texts(data)
sequences = tokenizer.texts_to_sequences(data)
tweets = pad_sequences(sequences, maxlen=max_len)
print(tweets)

#podział danych
X_train, X_test, y_train, y_test = train_test_split(tweets, labels, random_state=0)
print(len(X_train),len(X_test),len(y_train),len(y_test))

#Single LSTM layer model
model1 = Sequential()
model1.add(layers.Embedding(max_words, 20))
model1.add(layers.LSTM(15,dropout=0.5))
model1.add(layers.Dense(3,activation='softmax')) # warstwa klasyfikacji, 3 kategorie


model1.compile(optimizer='rmsprop',
               loss='categorical_crossentropy', 
               metrics=['accuracy'])

checkpoint1 = ModelCheckpoint("best_model1.hdf5", 
                              monitor='val_accuracy',
                              verbose=1,
                              save_best_only=True,
                              mode='auto',
                              period=1,
                              save_weights_only=False)

history = model1.fit(X_train, 
                     y_train, 
                     epochs=70,
                     validation_data=(X_test, y_test),
                     callbacks=[checkpoint1])

model1.summary()

"""## Ewaluacja najlepszego modelu"""

# ładujemy najlepszy model
best_model = keras.models.load_model("best_model1.hdf5")

test_loss, test_acc = best_model.evaluate(X_test, y_test, verbose=2)
print('Model accuracy: ',test_acc)

predictions = best_model.predict(X_test)

matrix = confusion_matrix(y_test.argmax(axis=1), np.around(predictions, decimals=0).argmax(axis=1))
conf_matrix = pd.DataFrame(matrix, index = ['Neutral', 'Negative','Positive'],columns = ['Neutral', 'Negative','Positive'])
conf_matrix = conf_matrix.astype('float') / conf_matrix.sum(axis=1)[:, np.newaxis]
plt.figure(figsize = (15,15))
sns.heatmap(conf_matrix, annot=True, annot_kws={"size": 15})