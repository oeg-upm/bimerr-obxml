import os
import time
 
start = time.time() #start time

os.system('java -jar helio.jar --mappings=../Mappings --config=config.json --write=rdf.ttl --close --clear')
 
end = time.time()
print("Elapsed time is  {}".format(end-start))