#  test

import sys
import b3
import numpy as np
import random
import itertools
import uuid
import matplotlib 
import matplotlib.pyplot as plt 
      
      
#########################################################################
#
#      Basic node with stochastic success 
#
#########################################################################
class Rn2(b3.Action): 
    def tick(self, tick):
        self.N_ticks += 1  
        cnt = tick.blackboard.get('treeTickCount')  #  only count the leaf ticks
        cnt += 1
        tick.blackboard.set('treeTickCount', cnt)
        self.prob()  # update probability estimate
        threshold = tick.blackboard.get('thresh', tick.tree.id, self.id)
        a = random.random()        
        #print self.Name, " P(success): ", self.N_success, " / ", self.N_ticks, " = ", self.Ps
        #print "Node received: ", x
        if(a < threshold):
	  self.N_success += 1
	  #print self.Name + " has succeeded"
	  return b3.SUCCESS;  
	if (a >= threshold):
	  #print self.Name + " has failed"
	  return b3.FAILURE;


      
#########################################################################
#
#     Node with variable physics based on terrain type 
#          P(success) depends on terrain in node-dependent manner
#
#########################################################################
class Rn3(b3.Action): 
    def tick(self, tick):
        self.N_ticks += 1  
        cnt = tick.blackboard.get('treeTickCount')  #  only count the leaf ticks
        cnt += 1
        tick.blackboard.set('treeTickCount', cnt)
        self.prob()  # update probability estimate
        #threshold = tick.blackboard.get('thresh', tick.tree.id, self.id)
        phys = tick.blackboard.get('Physics')
        terrain = tick.blackboard.get('Terrain')
        threshold = phys[self.Name][terrain-1]  # get success prob based on terrain
        #print "Name: " + self.Name + "  Terrain: " + track_names[terrain-1] + " Threshold: ", threshold
        a = random.random()        
        self.N_tik2[terrain-1] += 1
        #print self.Name, " P(success): ", self.N_success, " / ", self.N_ticks, " = ", self.Ps
        #print "Node received: ", x
        if(a < threshold):
	  self.N_success         += 1
	  self.N_suc2[terrain-1] += 1
	  #print self.Name + " has succeeded"
	  return b3.SUCCESS
	else:
	  #print self.Name + " has failed"
	  return b3.FAILURE


#########################################################################
#
#      Selector 2:  Choose leafs in order of Ps(Node,terrain)
#
#########################################################################	

class SmrtSel02(b3.Composite):
    def __init__(self, children=None):
        super(SmrtSel02, self).__init__(children)

    def tick(self, tick):
        terrain = tick.blackboard.get('Terrain')
        nodePs = {}
        for node in self.children:
	  plist = node.prob_terrain() # get P(s) for this node and this terrain
	  p = plist[terrain-1] # specific terrain
	  nodePs[p] = node
	rank = sorted(nodePs)
	#print "smart selector: Rank: ", rank
	N = len(rank)
	for j in range(0,N):
	  status = nodePs[rank[N-1-j]]._execute(tick)
          if status != b3.FAILURE:
                return status
        return b3.FAILURE


#########################################################################
#
#      Selector 1:  Choose leafs in order of estimated probability(success)
#
#########################################################################	

class SmrtSel01(b3.Composite):
    def __init__(self, children=None):
        super(SmrtSel01, self).__init__(children)

    def tick(self, tick):
        nodePs = {}
        # go through the leafs and get estimated P(s) for each 
        for node in self.children:
	  #print "Selecting from "+node.Name
	  # prob independent of terrain / experience
	  #p = tick.blackboard.get('thresh', tick.tree.id, node.id)
	  # prob depends on experience only 
	  p = node.prob()
	  #print "Returned probability: ",p
	  nodePs[p] = node
	# sort the probabilities (lowest first)
	rank = sorted(nodePs)
	#print "smart selector: Rank: ", rank
	#print nodePs
	N = len(rank)
	for j in range(0,N):
	  # Try them in descending order of probability
	  print "About to run "+nodePs[rank[N-1-j]].Name
	  status = nodePs[rank[N-1-j]]._execute(tick)
          if status != b3.FAILURE:
                return status
        return b3.FAILURE



#######################################
#
#  Let's select the test-case
#
####################################### 
test = ""

if len(sys.argv) < 2:
  arg = 99
else:
  arg = int(sys.argv[1])
  
if arg == 1:
  test = "Dumb Selector"
elif arg == 2:
  test = "Smart Selector: P(s)"
else:
  test = "Smart Selector2: P(s|F)"	

print "Starting "+ test
########################################
#
#    Set up our Test Tree
#
########################################

tr1 = b3.BehaviorTree()

if(test == "Dumb Selector"):
  n1 = Rn3()
  n2 = Rn3()
  n3 = Rn3() 
  # Vanilla selector node
  tr1.root =  b3.Priority([n1, n2, n3])
  test_name = test
elif(test == "Smart Selector2: P(s|F)"):
  n1 = Rn3()
  n2 = Rn3()
  n3 = Rn3()  
#  Smart version one:  rank order by P(N,t)
  tr1.root =  SmrtSel02([n1, n2, n3])
  test_name = test
elif(test == "Smart Selector: P(s)"):
  n1 = Rn3()
  n2 = Rn3()
  n3 = Rn3()  
  #  Smart version one:  rank order by P(N)
  tr1.root  = SmrtSel01([n1, n2, n3])
  test_name = test

n1.Name = "Node 1"  
n2.Name = "Node 2"
n3.Name = "Node 3"
 

#############################################################################
 

logfile = 'learnExp.csv'


#############################################################################


#  The 'target' is a track of terrains consisting of "snow",s,  "grass",g, "parkinglot",p
s = 1
g = 2
p = 3
track_names = ['Snow      ', 'Grass     ', 'ParkingLot']
 


t =   [2]*6 + [3]*10 + [1] + [2]*2 + [1]*6 + [3]+ [2]*3 + [1]*6 + [2] 
#+ [1]*3 + [3]*6 + [2]

t = [2]*10 + [1]*10 + [3]*10 + [2,2,2, 1,1,1,1,1,1,1,3,1,1,1,1,1,2,2,2,1,1,1,1,1]

t1 = t + t + t + t;

t = t1
n  = len(t)

num = np.zeros(3)

for i in t:
  num[i-1] += 1

print "terrain statistics: "
print num

bb = b3.Blackboard() 
  
  
threshold_value = 0.75

#  basic thresholds for the Rn2 nodes (not dependent on terrain)
  
bb.set('thresh', 0.95, tr1.id, n1.id)
bb.set('thresh', 0.15, tr1.id, n2.id)
bb.set('thresh', 0.05, tr1.id, n3.id)

bb.set('treeTickCount', 0)


#  The idea is that each leaf will perform differently on each terrain 


#                      snow    grass   parking
#   'mixed' Physics
physics = { 'Node 1': [0.1,     0.1,     0.9],
	    'Node 2': [0.1,     0.75,     0.1], 
	    'Node 3': [0.5,     0.7,     0.1]}


#                      snow    grass   parking
#   'mixed' Physics
physics = { 'Node 1': [.9,    .1,     .1],
	    'Node 2': [.1,    .9,     .1], 
	    'Node 3': [.1,    .1,     .9]}


#                      snow    grass   parking
#   Basic Physics
physics = { 'Node 1': [0.1,     0.1,     0.8],
	    'Node 2': [0.1,     0.8,     0.1], 
	    'Node 3': [0.8,     0.1,     0.1]}


bb.set('Physics',physics)

#   Run 100 experiments over the range and log the tick counts


#########################################################
#  set up the log file
log = open(logfile,'w')
Ntests = 250
tick_total = 0
data = np.zeros((n,3))

for iter in range(0,Ntests): 
  for j in range(0,n):
	track = t[j]
	bb.set('Terrain',track)
	tstart = bb.get('treeTickCount')
	#print "step ",j,"  Track Type:  ",track_names[t[j]-1] ,
	while tr1.tick(t,bb) != b3.SUCCESS:  
	  pass
	tend = bb.get('treeTickCount')
	ticks_per_step = tend-tstart
	#print "   ", tend-tstart , " ticks"
	#print "The BT was ticked ", bb.get('treeTickCount'), " times"
	data[j][0] = j
	data[j][1] += ticks_per_step
	data[j][2] = track
	tick_total += tend
	bb.set('treeTickCount',0)  #
  for node in tr1.root.children:
     node.p_reset()
     
log.close

print "Finished Simulation: ", test_name
print "Total tick count:    ", tick_total

for j in range(0,n):
  data[j][1] /= Ntests 
  
Npts = bb.get('treeTickCount')



## Two subplots, the axes array is 1-d
#f, axarr = plt.subplots(2, sharex=True)
#axarr[0].plot(x, y)
#axarr[0].set_title('Sharing X axis')
#axarr[1].scatter(x, y)

#########   Graph the data
#fig = plt.figure()
f, ax  = plt.subplots(2, sharex=True)
ax[0].plot(data[:,0],data[:,2],'ro')
ax[0].set_title(test_name + ' / Terrain')
ax[0].axis([0,n,0,4])
ax[1].plot(data[:,0],data[:,1],'bd')
ax[1].set_title('Avg Number of ticks')
ax[1].axis([0,n,0,15])
#f.title(logfile) 
plt.show()
