import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

path = "../data/csv/merged_3.csv"

data = pd.read_csv(path,1,",")

X=data[['direction', 'date_month', 'date_weekday', 'date_hour','date_minute','date_seconde','temp','humidity','visibility','wind','rain']].values  # Features
y=data['delay'].values # Labels


X_train , X_test, y_train, y_test = train_test_split(X,y)

clf = MLPClassifier(solver = 'adam',max_iter=1000,tol=0.000001,early_stopping=True,validation_fraction=0.1,n_iter_no_change=20)
clf.fit(X_train,y_train)

print("trained score: ", clf.score(X_train,y_train))
print("test score: ", clf.score(X_test,y_test))