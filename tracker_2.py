from socket import *
from tlslite.api import *
from tlslite import X509, X509CertChain, parsePEMKey
import threading
import json
import pickle 
from numpy import array,where,max,min,sum,pi,cos,sin,array_equal,zeros,copy,argmax
from scipy.io import loadmat
from sklearn import svm
import matplotlib.pyplot as plt 
import time

def client_thread(client_sock,data,std,model,wifi_keys,positions,headings,landmarks,data_mean,data_std,label_to_loc):
   connection = TLSConnection(client_sock)
   
   
   #make certificate later 
   #get certificate
   s = open("C:/OpenSSL-Win64/bin/mywebsitename.crt").read()
   x509 = X509()
   x509.parse(s)
   certChain = X509CertChain([x509])
   s = open("C:/OpenSSL-Win64/bin/mywebsitename.key").read()
   privateKey = parsePEMKey(s, private=True)
   #handshake
   connection.handshakeServer(certChain=certChain, privateKey=privateKey,reqCert=False)
   print connection.session.serverCertChain
  
   #helper variables 
   number_of_spots = 6 #place the number of spots here 
   counter = 0   #counter for while loop iteration 
   heading = [0,1] #a reference heading (direction) used for the direction calculations in the iterations 
   itter_heading = array([0.0,0.0])   #the variable used for the current heading (direction) of the user in the iteration 
   pos =  array([0,0]) #variable used to store the position of the user 
   leap = 0.0 #used to store how many steps a user has taken since last reading 
   last_step = 0 #used to store the last known value of the step counter 
   old_reading = zeros(12) # used to store the last known wifi sensor values 
   step_size = 0.865 #the size of a step in units of two feet 
   
   old_past_location = -1   #the landmark that was detected in a previous iteration of the while loop 
   past_location = -1 #the landmark that was detected in the current iteration if a landmark was detected in the current iteration otherwise this variable will take the value of old_past_location 
   steps_since_past_location = 0 #the number of steps taken since a landmark was last detected 
   steps_since_past_location_threshold = 10  #the number of steps a user must take before the same landmark can be detected twice
                                             #this variable is used to avoid the detection of a landmark multiple times as a user is walking through items
                                             #by avoiding multiple simultaneous detections, the users location won't be set to the corresponding position of the landmark multiple times.
   while counter <  1500:
        
        found_lm = False #variable used to specify if a landmark has been found in this iteration 
        counter += 1 #loop counter 
        
        #read a data record from the TLS connection and add it to the data list 
        test = connection.read() 
        data.append(json.loads(test))
        
        #get the direction the user is standing in. 
        #below I get the users orientation as an angle from the direction of north. This angle is stored in 
        #data[-1]['all_data']['fused_0']. Here data[-1] indexes the last element of the list, data[-1]['all_data'] accesses a value in a dictionary( which is like a hash make with key value pairs)
        #data[-1]['all_data']['fused_0'] accesses a value in a dictionary that's in a dictionary. Looking at the json output of our sent data should make this more clear. 
        da_angle =  -(data[-1]['all_data']['fused_0']+30)*pi/180.0
        itter_heading[0] = cos(da_angle)*heading[0]-sin(da_angle)*heading[1]
        itter_heading[1] = sin(da_angle)*heading[0]+cos(da_angle)*heading[1]
     
        #here I collect all of the wifi signals and put them in an array to be queried by the SVM. These wifi signals have been hard coded into the Android code. So you will have to make your own list and pass it into this function.
        #the syntax for the list is like this ['key id 1','key id 2','key id 3']
        test_post = array([data[-1]['all_data'][key] for key in wifi_keys]).reshape((1,len(wifi_keys)))
        test_post[test_post==-200] = -100.0
        
        #If the new wifi signals are different from the old wifi signals then enter the list 
        if not array_equal(test_post,old_reading):
        
            #get probabilities for each of the landmarks based on the wifi signals 
            probs = model.predict_proba((test_post[0,1:]-data_mean)/data_std)    
            print probs
            #get the index of the landmark with highest probability 
            ma = argmax(probs)
            
            #if the probability of the the most probable landmark is above some threshold (here .75)
            #then possibly predict that the user is at the landmarks location and set pos accordingly 
            if probs[0,ma] >0.75:
                found_lm = True 
                
                #If the user has walked a certain amount of steps after the last landmark was detected, then that same landmark can be detected again, otherwise it can not. 
                #New landmarks can always be detected. If a landmark is detected then pos will be set to the position of that landmark 
                if not (past_location == model.classes_[ma] and steps_since_past_location <= steps_since_past_location_threshold):
                    print 'you are here ',model.classes_[ma]                    
                    pos = label_to_loc[model.classes_[ma]]
                    steps_since_past_location=0
                    past_location = model.classes_[ma]
                   
                #book keeping variables                 
                positions.append(pos)
                headings.append(itter_heading)
                landmarks.append(1)
            
            #save the value of the old wifi readings for next iteration 
            old_reading = copy(test_post) 

        #Below I look at the step counter to see if the user has taken any steps since the last loop iteration  
        if data[-1][u'all_data'][u'stepc']> 0.0:
            leap = float(data[-1][u'all_data'][u'stepc']) - last_step if last_step!=0 else 1  
        
        #If the user has taken steps then move them in the direction that thay are facing by however many steps they have taken.
        #The number of steps that they have taken is stored in leap  
        if leap>0.0:
             #If the last landmark detected is the same then increment the following counter  
             if past_location == old_past_location:
                 steps_since_past_location+=1
             #print out the number of steps the user has taken in total
             print  data[-1][u'all_data'][u'stepc']
             
             #change the users location 
             num_steps = leap*step_size
             pos = itter_heading*num_steps+pos
             #record the users last step for future iterations 
             last_step = data[-1][u'all_data'][u'stepc']       

             #book keeping variables              
             positions.append(pos)
             headings.append(itter_heading)
             landmarks.append(0)
             old_past_location = past_location
   #close the connection  
   print 'you are here'     
   connection.close()


#create an INET, STREAMing socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#bind the socket to a public host,
# and a well-known port
serversocket.bind(('', 444))
#become a server socket
serversocket.listen(5)
means = pickle.load(open('loc_means.pickle','rb'))
stds = pickle.load(open('loc_stds.pickle','rb'))

#load svm model and pass into the thread 
model,data_mean,data_std = pickle.load(open('svm_model.pickle','rb'))

#get wifi lsit key data 
key_data = pickle.load(open('spot_1.pickle','rb'))

#Chris!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#You have to create a list for your wifi keys here. See line 63 above 
wifi_keys = key_data['wifi_keys']

#Below this label_to_loc diction gives the locations of the landmarks. The key is the landmark label and the value is the landmark location 

#label_to_loc = {11:[0,0],12:[0,7],13:[0,12],14:[0,20],21:[-5,-2],22:[-5,7],23:[-5,13],24:[-5,20],31:[-10,-2],32:[-10,7],33:[-10,13],34:[-10,20]}
#label_to_loc = {1:[0,0],2:[0,9],3:[0,20],4:[-10,20],5:[-7,10],6:[-10,-2]}
label_to_loc = {1:[0,0],2:[0,9],3:[0,20],5:[-7,10],6:[-10,-2]}


#this list will contain all client threads 
threads = []
print 'listening...' 
counter = 0
while counter < 1:
    counter +=1 
    #accept connections from outside
    (clientsocket, address) = serversocket.accept()
    print 'connection made' 
    #now do something with the clientsocket
    #in this case, we'll pretend this is a threaded server
    
    data = [] #this list will be populated to hold all data records from the server 
    positions = [] #this list will hold all positions the user has taken 
    headings = [] #This list will hold all directions the user has had 
    landmarks=[] #This list will contain a 1 at position i if a landmark was detected at loop iteration i 
    ct = threading.Thread(target=client_thread,args = (clientsocket,data,stds,model,wifi_keys,positions,headings,landmarks,data_mean,data_std,label_to_loc))
    threads.append(ct)
    ct.start()
ct.join()





