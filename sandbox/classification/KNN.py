import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

path = "../data/csv/merged_3.csv"
data = pd.read_csv(path,1,",")

X=data[['direction', 'date_month', 'date_weekday', 'date_hour','date_minute','date_seconde','temp','humidity','visibility','wind','rain']].values  # Features
y=data['delay'].values # Labels

X_train , X_test, y_train, y_test = train_test_split(X,y)

knn = KNeighborsClassifier(n_neighbors=50,leaf_size=300)
knn.fit(X_train, y_train)

print("trained score: ", knn.score(X_train,y_train))
print("test score: ", knn.score(X_test,y_test))

