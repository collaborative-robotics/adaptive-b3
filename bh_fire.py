
# Simulate the fire extinguisher scenario from Periera and Engel 2015

import sys
import b3
import numpy as np
import random
import itertools
import uuid
import matplotlib 
import matplotlib.pyplot as plt 
from pylab import rcParams   
      
#########################################################################
#
#      Basic node with stochastic success 
#
#########################################################################
class Rn2(b3.Action): 
    def tick(self, tick):
        print "Rn2: Node ticked: ", self.Name
        self.N_ticks += 1  
        #cnt = tick.blackboard.get('treeTickCount')  #  only count the leaf ticks
        #cnt += 1
        #tick.blackboard.set('treeTickCount', cnt)
        self.prob()  # update probability estimate
        threshold = tick.blackboard.get('thresh', tick.tree.id, self.id)
        a = random.random()        
        print self.Name, " thresh: ", threshold, " Random: ", a
        if(a < threshold):
	  self.N_success += 1
	  #print self.Name + " has succeeded"
	  return b3.SUCCESS;  
	if (a >= threshold):
	  #print self.Name + " has failed"
	  return b3.FAILURE;


      
#########################################################################
#
#     Node with variable physics based on state type 
#          P(success) depends on state in node-dependent manner
#
#########################################################################
class Rn3(b3.Action): 
    def tick(self, tick):
        self.N_ticks += 1  
        cnt = tick.blackboard.get('treeTickCount')  #  only count the leaf ticks
        cnt += 1
        tick.blackboard.set('treeTickCount', cnt)
        #threshold = tick.blackboard.get('thresh', tick.tree.id, self.id)
        phys = tick.blackboard.get('Physics')
        state = tick.blackboard.get('State')
        print "Rn3: Node ticked: ", self.Name, " Fire state: ", state
        threshold = phys[self.Name][state]  # get success prob based on state
        #if(state == 3): 
	  #print "\n\n\nName: " + self.Name + "  FireState: " , state ," Threshold: ", threshold
        a = random.random()
        #if(self.Name == "")
        self.N_tik2[state] += 1
        #print self.Name, " P(success): ", self.N_success, " / ", self.N_ticks, " = ", self.Ps
        #print "Node received: ", x
        if(a < threshold):
	  self.N_success       += 1
	  self.N_suc2[state]   += 1
	  #print self.Name + " has succeeded"
	  return b3.SUCCESS
	else:
	  #print self.Name + " has failed"
	  return b3.FAILURE


#########################################################################
#
#      Selector 2:  Choose leafs in order of Ps(Node,state)
#
#########################################################################	

class SmrtSel02(b3.Composite):
    def __init__(self, children=None):
        super(SmrtSel02, self).__init__(children)

    def tick(self, tick):
        print "Sel 02: Node ticked: ", self.Name
        state = tick.blackboard.get('State') 
        leafPs = []
        #if (self.Name == "Extinguish"):
	  #print "Extinguish: "
	j = 0
        for node in self.children:
	  #print "I'm looking at leaf: "+node.Name
	  plist = node.prob_state() # get P(s) for this node and all states
	  node.P_selector = plist[state] # this specific state
	  leafPs.append(node)
	rank = sorted(leafPs, key=lambda node: node.P_selector)  # sort by P(s|F)
	print "smart selector: Rank: | " ,
	for n in rank:
	  print n.Name , n.P_selector , " | " ,
	print ""
	N = len(rank)
	for j in range(0,N):  # execute the leafs in order of probability
	  print "Sel02: I'm ticking ", rank[N-1-j].Name
	  status = rank[N-1-j]._execute(tick)
          if status != b3.FAILURE:
	        if(self.Name == "Extinguish"):
		    print "Extinguish: Fire State: ", state , " SUCCESS "
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
        print "Sel01: Node ticked: ", self.Name
        leafPs = []
        # go through the leafs and get estimated P(s) for each 
        for node in self.children:
	  #print "Selecting from "+node.Name
	  # prob independent of state / experience
	  #p = tick.blackboard.get('thresh', tick.tree.id, node.id)
	  # prob depends on experience only 
	  node.P_selector = node.prob()
	  #print "Returned probability: ",p
	  leafPs.append(node)
	# sort the probabilities (lowest first)
	rank = sorted(leafPs, key=lambda node: node.P_selector)  # sort by P(s|F)
	#print "smart selector: Rank: ", rank
	#print leafPs
	N = len(rank)
	for j in range(0,N):
	  # Try them in descending order of probability
	  #print "About to run "+leafPs[rank[N-1-j]].Name
	  status = rank[N-1-j]._execute(tick)
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
  test = "Smart Selector S1: P(s)"
else:
  test = "Smart Selector S2: P(s|F)"	

print "Starting "+ test
 
 

#############################################################################
 

logfile = 'learnExp.csv'



#############################################################################

######  Set up tree

tr1 = b3.BehaviorTree()


if(test == "Dumb Selector"):      # argv = 1
  A = Rn3()
  B = Rn3()
  C = Rn3() 
  # Vanilla selector node
  extinguish = b3.Priority([A, B, C])
  vict = Rn2()  # based on fixed P(s)
  save = b3.Succeeder()  
  saver = b3.Priority([vict, save])
  changer = b3.Succeeder()  
  tr1.root =  b3.Sequence([saver, extinguish, changer])
  test_name = test
elif(test == "Smart Selector S1: P(s)"):     # argv = 2
  A = Rn3()
  B = Rn3()
  C = Rn3() 
  # Vanilla selector node
  extinguish = SmrtSel01([A, B, C])
  vict = Rn2()  # based on fixed P(s)
  save = b3.Succeeder()  
  saver = b3.Priority([vict, save])
  changer = b3.Succeeder()  
  tr1.root =  b3.Sequence([saver, extinguish, changer])
  test_name = test
elif(test == "Smart Selector S2: P(s|F)"):   # argv = 3
  A = Rn3()
  B = Rn3()
  C = Rn3() 
  # Vanilla selector node
  extinguish = SmrtSel02([A, B, C])
  vict = Rn2()  # based on fixed P(s) 
  save = b3.Succeeder()  
  saver = b3.Priority([vict, save])
  changer = b3.Succeeder()  
  tr1.root =  b3.Sequence([saver, extinguish, changer])
  test_name = test
 
 
# standard names
A.Name = "ExtA"
B.Name = "ExtB"
C.Name = "ExtC"
extinguish.Name = "Extinguish"
vict.Name = "Victim?"
save.Name = "Save"
saver.Name = "Saver"
changer.Name = "Room Change"


#########################   set up rescue rescue rooms 
num_rooms = 1000
victim = np.zeros(num_rooms)
fires  = np.zeros(num_rooms)
# name the fire types
fta = 1
ftb = 2
ftc = 3
 

#############################################################################
 
bb = b3.Blackboard() 
  
##   Set probability of detecting a victim (if present) to 100%
# set probability of detecting a fire (if present) to 1.0 

bb.set('treeTickCount', 0)


#  The idea is that each leaf will perform differently on each fire type

#                         none       fta         ftb        ftc   
#   'mixed' Physics
fire_physics = { 'ExtA': [1.0,        1.0,        0.0,     0.0],
    	         'ExtB': [1.0,	      0.0,        1.0,     0.0], 
	         'ExtC': [1.0,        0.0,        0.0,     1.0]}
 

bb.set('Physics',fire_physics)

#   Run experiments over the range and log the tick counts


#########################################################
#  set up the log file
log = open(logfile,'w')

n = 400   # compare to P&E fig 4. (400) 
Ntests = 20
tick_total = 0
data = np.zeros((n,3))
dummy = np.zeros(5)

for iter in range(0,Ntests): 
  # randomize the Test setup
  for i in range(0,num_rooms):  #  add victims and fires
      a = random.random()
      if a > 0.500:
	victim[i] = 1
      a = random.random()  # independent of victim!
      if a < 0.3333*0.5:
	fires[i] = fta
      if 0.3333*.5 < a < 0.6666*0.5:
	fires[i] = ftb
      if 0.66666*0.5 < a < 0.500:
	fires[i] = ftc
  for j in range(0,n):
        print "\n\nRoom {}, victim: {}, firestate: {}\n\n".format(j,victim[j],fires[j])
        # determine if a victim will be detected in room
        bb.set('thresh', 1.0 - victim[j], tr1.id, vict.id)  # fail if victim present
        # determine fire state in current room
        bb.set('State', int(fires[j])) 
	tstart = bb.get('treeTickCount')
	#print "step ",j,"  Track Type:  ",track_names[t[j]-1] ,
	#
	#  slight modification, try each extinguisher in turn until 
	#     fire is out
	#     
	while tr1.tick(dummy,bb) != b3.SUCCESS:
	  print "Tree FAIL"
	  pass
	tend = bb.get('treeTickCount')
	ticks_per_step = tend-tstart
	#print "   ", tend-tstart , " ticks"
	#print "The BT was ticked ", bb.get('treeTickCount'), " times"
	data[j][0] = j
	data[j][1] += ticks_per_step
	data[j][2] = fires[j]
	tick_total += ticks_per_step
	bb.set('treeTickCount',0)  #
  for node in extinguish.children:
        node.p_reset() # reset action leafs probability estimates
     
     
log.close

print "Finished Simulation: ", test_name
print "Total tick count:    ", tick_total

# average the tick counts at each point in time
for j in range(0,n):
  data[j][1] /= Ntests 
  
Npts = bb.get('treeTickCount')

#########   Graph the data
#fig = plt.figure()
 

f, ax  = plt.subplots(2, sharex=True)
ax[0].plot(data[:,0],data[:,2],'ro')
ax[0].set_title(test_name + ' / Fire Type')
ax[0].axis([0,n,0,4])
ax[1].plot(data[:,0],data[:,1],'bd')
ax[1].set_title('Avg Number of ticks')
ax[1].axis([0,n,0,5]) 
gfile = raw_input("Enter graphics filename: ")
plt.savefig(gfile + '.png' , dpi=200)
plt.show()

