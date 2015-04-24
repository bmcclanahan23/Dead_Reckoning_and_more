import pickle 
from numpy import array,mean ,where

#Chris!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#name landmark 1, spot_1.pickle  name landmark 2, spot_2.pickle   etc
filename = 'spot_6.pickle'
sig_data = []
key_list = data[0]['all_data'].keys()
key_list =  sorted(key_list )
wifi_keys = [x for x in key_list if x.count(':') == 5]
other_keys = [x for x in key_list if not x in wifi_keys]
for instance in data[10:]: 
    sig_data.append({'other_stuff':[instance['all_data'][key] for key in other_keys], 'wifi_stuff':[instance['all_data'][key] for key in wifi_keys]})
    spot_array =  array(sig_data[-1]['wifi_stuff'])
    rows = where(spot_array==-200)
    spot_array[rows] = -100
    sig_data[-1]['wifi_stuff'] = spot_array
 

spot_mean = mean(spot_array,axis=0)
pickle.dump({'sig_data':sig_data,'key_list':key_list ,'wifi_keys':wifi_keys,'other_keys':other_keys},open(filename,'wb'))




