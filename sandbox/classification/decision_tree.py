import pandas as pd
from sklearn import tree
import matplotlib.pyplot as plt
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


#prend les chemins avec les fichiers cvs
dir_name = os.path.dirname(os.path.abspath(__file__))
csv_train = "/data/train/train_merged.csv"
csv_test = "/data/test/test_merged.csv"

path_train = dir_name+ csv_train
path_test = dir_name + csv_test

#extraction des données du fichier csv
df_train = pd.read_csv(path_train,1,",")
df_test = pd.read_csv(path_test,1,",")

#on split notre target (salary) et nos critères qui vont servir à la prédiction
X = df_train.drop(["stop","theoretical_time","expectedArrivalTime","date","delay"],axis='columns')
Y = df_train["delay"]
W = df_test.drop(["stop","theoretical_time","expectedArrivalTime","date","delay"],axis='columns')
Z = df_test["delay"]

#EXO 3.1
#on crée un arbre de décision avec une profondeur de 3 et on le fit avec nos données à entrainer
clf = tree.DecisionTreeClassifier(min_samples_leaf=250,criterion="entropy")
clf = clf.fit(X,Y)
#on montre le résultat sur nos donées d'entrainement et test apres l'avoir entrainé
print(clf.score(X,Y))
print(clf.score(W,Z))
#enregistre l'abre après entrainement en png
DT_to_PNG(clf,X.columns,"max_depth_3")

