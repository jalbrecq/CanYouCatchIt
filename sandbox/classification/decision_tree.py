import pandas as pd
from sklearn import tree
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
#just to add Graphviz to the Path
import os
os.environ["PATH"] += os.pathsep + 'D:/Program Files (x86)/Graphviz2.38/bin/'

#this function was given by the teacher of ML 
def DT_to_PNG(model, feature_names, file_name):
    """ Exports a DT to a PNG image file for inspection.
    
    Parameters
    ----------
        - model: a decision tree (class sklearn.tree.DecisionTreeClassifier)
        - feature_names: a list of feature names
        - file_name: name of file to be produced (without '.png' extension)
    
    Notes
    -----
    This function requires the pydot Python package and the Graphviz library.
    
    For more information about tree export, see http://scikit-learn.org/stable/
    modules/generated/sklearn.tree.export_graphviz.html#sklearn.tree.export_graphviz
    
    """

    import pydot
    import string
    from sklearn import tree
    from sklearn.externals.six import StringIO
    
    dot_data = StringIO()
    tree.export_graphviz(model, out_file=dot_data, feature_names=feature_names)
    graph = pydot.graph_from_dot_data(dot_data.getvalue())[0]
    graph.write_png('%s.png' % file_name)

path = "../data/csv/merged.csv"

data = pd.read_csv(path,1,",")

X=data[['direction', 'date_month', 'date_weekday', 'date_hour','date_minute','date_seconde','temp','humidity','visibility','wind','rain']]  # Features
y=data['delay']  # Labels


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3) # 70% training and 30% test

#on crée un arbre de décision avec une profondeur de 3 et on le fit avec nos données à entrainer
clf = tree.DecisionTreeClassifier(criterion="entropy",min_samples_leaf=100)
clf = clf.fit(X_train,y_train)
#on montre le résultat sur nos donées d'entrainement et test apres l'avoir entrainé
print(clf.score(X_train,y_train))
print(clf.score(X_test,y_test))
#enregistre l'abre après entrainement en png
DT_to_PNG(clf,X.columns,"tree")

