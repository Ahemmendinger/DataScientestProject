#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 19 15:08:24 2021

@author: ahemmendinger
"""

import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import NLTKWordTokenizer
import joblib
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
stop_words.update(["'ve", "", "'ll", "'s", ".", ",", "?", "!", "(", ")", "..", "'m", "n", "u"])
 
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier



def preprocess_text(text):
    tokenizer = NLTKWordTokenizer()
    text = text.lower()
    tokens = tokenizer.tokenize(text)
    tokens = [t for t in tokens if t not in stop_words]
    
    return ' '.join(tokens)



if __name__ == '__main__' :
    df = pd.read_csv('others/DisneylandReviews.csv', encoding='cp1252')
    df = df.drop(['Review_ID', 'Year_Month', 'Reviewer_Location'], axis=1)
    df['Review_Text'] = df['Review_Text'].apply(preprocess_text)
    
    ###### Modèle unique ######
    
    
    features = df['Review_Text']
    target = df['Rating']
    
    X_train, X_test, y_train, y_test = train_test_split(features, target)
    pipeline_one_model = Pipeline([('count',CountVectorizer(max_features=2000)),
                                   ('log_reg',LogisticRegression())
                                   ])
    pipeline_one_model.fit(X_train,y_train)
    joblib.dump(pipeline_one_model,'models/pipeline_one_model')
    
    
    ###### Modèles par branche #####
    
    for branch in df['Branch'].unique():
        count_vectorizer = CountVectorizer(max_features=2000)
        model = RandomForestClassifier()
        pipeline = Pipeline([('count',count_vectorizer),('RFC',model)])
        df_temp = df[df['Branch'] == branch]
        X_train, X_test, y_train, y_test = train_test_split(df_temp['Review_Text'], df_temp['Rating'])
        pipeline.fit(X_train,y_train)
        joblib.dump(pipeline,f'models/pipeline_{branch}')
    
    







