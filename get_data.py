from socket import *
from tlslite.api import *
from tlslite import X509, X509CertChain, parsePEMKey
import threading
import json
import pickle 
from numpy import array,where,max,min,sum


#function for client thread 
def client_thread(client_sock,data,std):
    #create a tls connection 
    connection = TLSConnection(client_sock)
   
    #get certificate
    s = open("C:/OpenSSL-Win64/bin/mywebsitename.crt").read()
    x509 = X509()
    x509.parse(s)
    certChain = X509CertChain([x509])
    #get key
    s = open("C:/OpenSSL-Win64/bin/mywebsitename.key").read()
    privateKey = parsePEMKey(s, private=True)
    #handshake
    connection.handshakeServer(certChain=certChain, privateKey=privateKey,reqCert=False)
    #print message establishing the connection has been successfully made 
    print connection.session.serverCertChain
    counter = 0
    while counter <  50:
        
        #collected data being sent in a list 
        counter += 1
        test = connection.read()
        data.append(json.loads(test))
        print data[-1]
        
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
    data = []
    ct = threading.Thread(target=client_thread,args = (clientsocket,data,stds,))
    threads.append(ct)
    ct.start()
ct.join()





