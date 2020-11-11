import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics

path = "../data/csv/merged.csv"

data = pd.read_csv(path,1,",")

X=data[['direction', 'date_month', 'date_weekday', 'date_hour','date_minute','date_seconde','temp','humidity','visibility','wind','rain']]  # Features
y=data['delay']  # Labels

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5,random_state=10) # 70% training and 30% test

clf=RandomForestClassifier(n_estimators=100,criterion="entropy")
clf.fit(X_train,y_train)
y_pred=clf.predict(X_test)
print("Accuracy:",metrics.accuracy_score(y_test, y_pred))