import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.utils import class_weight
import numpy as np

path = "../data/csv/merged.csv"

def compute_class_weight_dictionary(y):
    # helper for returning a dictionary instead of an array
    classes = np.unique(y)
    weight = class_weight.compute_class_weight("balanced", classes, y)
    class_weight_dict = dict(zip(classes, weight))
    return class_weight_dict


data = pd.read_csv(path,1,",")
class_weight=compute_class_weight_dictionary(data.delay)

X=data[['direction', 'date_month', 'date_weekday', 'date_hour','date_minute','date_seconde','temp','humidity','visibility','wind','rain']]  # Features
y=data['delay']  # Labels


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3) # 70% training and 30% test

clf=RandomForestClassifier(n_estimators=100,criterion="entropy",bootstrap=True,min_samples_leaf=300,class_weight=class_weight)
clf.fit(X_train,y_train)
y_pred=clf.predict(X_test)
print("class_weight")
print("trained score: ", clf.score(X_train,y_train))
print("test score: ", clf.score(X_test,y_test))

clf=RandomForestClassifier(n_estimators=100,criterion="entropy",bootstrap=True,min_samples_leaf=100)
clf.fit(X_train,y_train)
y_pred=clf.predict(X_test)
print("min leaf = 100")
print("trained score: ", clf.score(X_train,y_train))
print("test score: ", clf.score(X_test,y_test))

print("min_samples_leaf")
for i in range(100,1001,100):
	clf=RandomForestClassifier(n_estimators=100,criterion="entropy",bootstrap=True,min_samples_leaf=i)
	clf.fit(X_train,y_train)
	y_pred=clf.predict(X_test)
	print(i, "samples on leaf")
	print("trained score: ", clf.score(X_train,y_train))
	print("test score: ", clf.score(X_test,y_test))

print("nb_tree")
for i in range(100,401,100):
	clf=RandomForestClassifier(n_estimators=i,criterion="entropy",bootstrap=True)
	clf.fit(X_train,y_train)
	y_pred=clf.predict(X_test)
	print(i, "trees")
	print("trained score: ", clf.score(X_train,y_train))
	print("test score: ", clf.score(X_test,y_test))





#3724, 10911, 9411, 9590, 850 
