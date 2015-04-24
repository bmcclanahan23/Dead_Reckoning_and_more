# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 18:26:44 2015

@author: Brian
"""
import pickle
from sklearn.neighbors import KDTree,KNeighborsClassifier
from numpy import array,fill_diagonal,Inf,argsort,unique,zeros,sum,argmax,mean
from sklearn import cross_validation
from sklearn import svm
from sklearn.metrics.pairwise import rbf_kernel


#fused

classification_data  = []
labels = []

#Chris!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#put the labels of your landmarks here 
locations = [1,2,3,5,6]

for row in [1,2,3,5,6]: 
    all_data = pickle.load(open('spot_%d.pickle'%row))
    for entry in all_data['sig_data']:        
        classification_data.append(entry['wifi_stuff'])
        labels.append(row)
            
classification_data = array(classification_data)
classification_data = classification_data[:,1:]
data_mean = classification_data.mean(axis=0)
data_std = classification_data.std(axis=0)
classification_data = (classification_data-data_mean)/data_std
labels = array(labels)



skf = cross_validation.StratifiedKFold(labels, n_folds=10,shuffle=True)

num_neighs = 3
acc1 = []
acc2 = []
acc3 = []
mean_posterior = []

label_to_index= {}
u_labels = unique(labels)
for index in range(u_labels.shape[0]): 
    label_to_index[u_labels[index]] = index
for train_index, test_index in skf:   
    kdt = KDTree(classification_data[train_index,:], leaf_size=20, metric='euclidean')
    kdt = KNeighborsClassifier(n_neighbors=3,algorithm='kd_tree',leaf_size=10)
    kdt.fit(classification_data[train_index,:],labels[train_index])

    rbf_similarity = rbf_kernel(classification_data,gamma=1.0/100.0)
    rbf_similarity[:,test_index] = 0
   
    nn_train = argsort(rbf_similarity[train_index,:],axis=1)[:,-num_neighs:]
    nn_test = argsort(rbf_similarity[test_index,:],axis=1)[:,-num_neighs:]
    
    train_predictions = zeros(nn_train.shape[0])
    test_predictions = zeros(nn_test.shape[0])
    
    for index in range(nn_train.shape[0]):
        itter_labels = labels[nn_train[index,:]]
        u_labels = unique(itter_labels)
        lab_counts = zeros(u_labels.shape[0])
        for entry in range(lab_counts.shape[0]): 
            lab_counts[entry] = sum(u_labels[entry]==itter_labels)
        train_predictions[index] = u_labels[argmax(lab_counts)]
        
    for index in range(nn_test.shape[0]):
        itter_labels = labels[nn_test[index,:]]
        u_labels = unique(itter_labels)
        lab_counts = zeros(u_labels.shape[0])
        for entry in range(lab_counts.shape[0]): 
            lab_counts[entry] = sum(u_labels[entry]==itter_labels)
        test_predictions[index] = u_labels[argmax(lab_counts)]
        
        
    fill_diagonal(rbf_similarity,0)    
        
    
    model =  svm.SVC(kernel='rbf',C=20,gamma=.0001,probability=True)
    model.fit(classification_data[train_index,:],labels[train_index])
    
    acc1.append(kdt.score(classification_data[test_index,:],labels[test_index]))   
    acc2.append(sum(test_predictions==labels[test_index])/float(test_predictions.shape[0]))
    acc3.append(model.score(classification_data[test_index,:],labels[test_index]))    
    print 'knn train score ',kdt.score(classification_data[train_index,:],labels[train_index])
    print 'knn test score ',acc1[-1]
    print ' '    
    
    #print 'knn 2 train score ',sum(train_predictions==labels[train_index])/float(train_predictions.shape[0])
    #print 'knn 2 test score ',acc2[-1]
    #print ' '

    print 'svm train score ',model.score(classification_data[train_index,:],labels[train_index])
    print 'svm test score ',acc3[-1]
    print ' '
    predictions = model.predict(classification_data[test_index,:])
    pred_probs = model.predict_proba(classification_data[test_index,:])
    itter_mean_posterior = []
    for index in range(predictions.shape[0]): 
        itter_mean_posterior.append(pred_probs[index,:][label_to_index[predictions[index]]])
    mean_posterior.append(mean(itter_mean_posterior))
    
print 'accuracy 1 ',mean(acc1)
print 'accuracy 2 ',mean(acc3)

model =  svm.SVC(kernel='rbf',C=20,gamma=.0001,probability=True)
model.fit(classification_data,labels)

pickle.dump([model,data_mean,data_std],open('svm_model.pickle','wb'))
