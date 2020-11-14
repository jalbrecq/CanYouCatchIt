import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.utils import class_weight
from sklearn.svm import SVC
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler


path = "../data/csv/merged_3.csv"

data = pd.read_csv(path,1,",")

X=data[['direction', 'date_month', 'date_weekday', 'date_hour','date_minute','date_seconde','temp','humidity','visibility','wind','rain']].values  # Features
y=data['delay'].values # Labels

label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)
X = StandardScaler().fit_transform(X)

X_train , X_test, y_train, y_test = train_test_split(X,y)

clf = SVC(C=1.0, kernel='linear',gamma='scale')
clf.fit(X_train,y_train)

print("trained score: ", clf.score(X_train,y_train))
print("test score: ", clf.score(X_test,y_test))