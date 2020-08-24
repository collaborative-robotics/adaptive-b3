
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
      
from smart_selectors import *
from smart_nodes     import *
      

#######################################
#
#  Let's select the test-case
#
####################################### 
test = ""

file = open("data.txt", "a")

for n in sys.argv:
    print "Arg: ", n
    
if len(sys.argv) < 2:
  arg = 99
else:
  arg = int(sys.argv[1])
  if len(sys.argv) == 3:
     walktime_arg = int(sys.argv[2])
  else:
     walktime_arg = 50
  
  
if arg == 0:
    test = "Dumb Selector"
elif arg == 1:
    test = "Smart Selector 1: P(s)"
elif arg == 2:
    test = "Smart Selector 2: P(s|F)"
elif arg == 3:
    test = "Smart Selector 3: Cost"
elif arg == 4:
    test = "Smart Selector 4: Utility"
elif arg == 5:
    test = "Smart Selector 5: Conditional Utility"
elif arg == 6:
    test = "tmpTest"
else:
    print "invalid CL argument"
    quit() 

print "Command line choice: "+ test
 

######  Set up tree

tr1 = b3.BehaviorTree()
bb = b3.Blackboard() 
 
#########################
#  Leafs
W1 = walk()
W2 = walk()
W3 = walk()
A = fightfire()
B = fightfire()
C = fightfire() 
fly_to_dest = fly()


if (test == "Dumb Selector"):
    id = "Sel00"
    extinguish = SmrtSel00([A,B,C])
    walker = SmrtSel00([W1, W2, W3])
    walk_trip = WalkTillDestination(walker, walktime_arg)  # walk till destination or walktime_arg
    transport = SmrtSel00([walk_trip,fly_to_dest])
    #transport = SmrtSel01([walk_trip, fly_to_dest])
    task = b3.Sequence([transport, extinguish])
    tr1.root = b3.Priority([task]) # root doesn't use b
 
if( test == "Smart Selector 1: P(s)"):
    id = "Sel01"
    extinguish = SmrtSel01([A,B,C])
    walker = SmrtSel01([W1, W2, W3])
    walk_trip = WalkTillDestination(walker, walktime_arg)  # walk till destination or walktime_arg
    transport = SmrtSel01([walk_trip,fly_to_dest])
    #transport = SmrtSel01([walk_trip, fly_to_dest])
    task = b3.Sequence([transport, extinguish])
    tr1.root = b3.Priority([task]) # root doesn't use baseclass so stub it.

if (test == "Smart Selector 2: P(s|F)"):    # rebuild tree with smart sel 2
    id = "Sel02"
    extinguish = SmrtSel02([A,B,C])
    walker = SmrtSel02([W1, W2, W3])
    walk_trip = WalkTillDestination(walker, walktime_arg)  # walk till destination or walktime_arg
    transport = SmrtSel01([walk_trip,fly_to_dest])
    #transport = SmrtSel01([walk_trip, fly_to_dest])
    task = b3.Sequence([transport, extinguish])
    tr1.root = b3.Priority([task]) # root doesn't use baseclass so stub it.

if (test == "Smart Selector 3: Cost"):    # rebuild tree with smart sel 2
    id = "Sel03"
    extinguish = SmrtSel03([A,B,C])
    walker = SmrtSel02([W1, W2, W3])
    walk_trip = WalkTillDestination(walker, walktime_arg)  # walk till destination or walktime_arg
    transport = SmrtSel03([walk_trip,fly_to_dest])
    #transport = SmrtSel01([walk_trip, fly_to_dest])
    task = b3.Sequence([transport, extinguish])
    tr1.root = b3.Priority([task]) # root doesn't use baseclass so stub it.

if (test == "Smart Selector 4: Utility"):    # rebuild tree with smart sel 2
    id = "Sel04"
    extinguish = SmrtSel04([A,B,C])
    walker = SmrtSel04([W1, W2, W3])
    walk_trip = WalkTillDestination(walker, walktime_arg)  # walk till destination or walktime_arg
    transport = SmrtSel04([walk_trip,fly_to_dest])
    #transport = SmrtSel01([walk_trip, fly_to_dest])
    task = b3.Sequence([transport, extinguish])
    tr1.root = b3.Priority([task]) # root doesn't use baseclass so stub it.
    
if (test == "Smart Selector 5: Conditional Utility"):    # rebuild tree with smart sel 2
    id = "Sel05"
    extinguish = SmrtSel05([A,B,C])
    walker =     SmrtSel05([W1, W2, W3])
    walk_trip = WalkTillDestination(walker, walktime_arg)  # walk till destination or walktime_arg
    transport = SmrtSel04([walk_trip,fly_to_dest])
    #transport = SmrtSel01([walk_trip, fly_to_dest])
    task = b3.Sequence([transport, extinguish])
    tr1.root = b3.Priority([task]) # root doesn't use baseclass so stub it.

test_name = test
#  NAMES
A.Name = "ExtA"
B.Name = "ExtB"
C.Name = "ExtC"
transport.Name = "Transport"
task.Name = "Root Task"
extinguish.Name = "Extinguish" 
walker.Name = "walker"
walk_trip.Name = "walk until destination"
fly_to_dest.Name = "fly_to_dest"
W1.Name = "w1"
W2.Name = "w2"
W3.Name = "w3"

#debug
walk_trip.BHdebug = 0
walker.BHdebug = 0
fly_to_dest.BHdebug = 0
task.BHdebug = 0
transport.BHdebug = 0
extinguish.BHdebug = 1

	
##  set up COSTS

W1.Cost = 1
W2.Cost = 1
W3.Cost = 1

W1.BHdebug = 1
W2.BHdebug = 1
W3.BHdebug = 1


#      Fly Cost   Wk/Fly ratio
# low      260 =  Variable!!
# medium   275 =  55%
# high     290 =  84%
fly_to_dest.Cost = 350

A.Cost = 10
B.Cost = 10
C.Cost = 10

A.BHdebug = 0
B.BHdebug = 0
C.BHdebug = 0

#########################   
# name the fire types
fta = 1
ftb = 2
ftc = 3


#############################################################################

#   populate the blackboard

##   Set probability of detecting a victim (if present) to 100%
# set probability of detecting a fire (if present) to 1.0 

bb.set('treeTickCount', 0)
bb.set('distancetofire', 100)  # 100 successful steps required to reach fire 
	
#                      snow    grass   parking  (col 4 not used)
#  Walking Physics  (ter state 0 is undfined)
walkingphysics = { 'w1': [0,  0.1,     0.1,     0.8],
	           'w2': [0,  0.1,     0.8,     0.1], 
	           'w3': [0,  0.8,     0.1,     0.1]}

bb.set('WalkPhysics',walkingphysics)


#   Fire fighting Physics
#  The idea is that each leaf will perform differently on each fire type
#                         none       fta         ftb        ftc   
#   'mixed' Physics
fire_physics = { 'ExtA': [1.0,        0.95,        0.05,     0.05],
    	         'ExtB': [1.0,	      0.05,        0.9,      0.05], 
	         'ExtC': [1.0,        0.05,        0.05,     0.925]}

bb.set('FirePhysics',fire_physics)

##############   Walking Track
#

t = [2]*10 + [1]*10 + [3]*10 + [2,2,2, 1,1,1,1,1,1,1,3,1,1,1,1,1,2,2,2,1,1,1,1,1]
t1 = t + t + t + t;
t = t1
n  = len(t)


bb.set('maxwalktime', walktime_arg)


#   Run experiments over the range and log the tick counts


######################################################### 

#n = 400   #
Ntests = 1000
tick_total = 0
ticks_meth1 = 0
ticks_meth2 = 0
data = np.zeros((Ntests,5))
dummy = np.zeros(5)


total_cost = 0
total_ticks = 0
total_utility = 0

test_fails = 0


bb.set('TotalCost',0)    
bb.set('distance', 0)

for iter in range(0,Ntests): 
  ## randomize the fire type 
  a = random.random() 
  firetype = 0
  if a < 0.3333:
    firetype = fta
  if 0.3333 < a < 0.6666:
     firetype = ftb
  if 0.66666 < a < 1.10:
     firetype = ftc
   
  # set up the fire type in extingish leafs
  A.state = firetype
  B.state = firetype
  C.state = firetype
  #bb.set('FireState', firetype) 

  # set terrain state for current step
  bb.set('Terrain', t)
  
 
  #
  #  tick the tree 
  #############################
  # just one tick should run the whole thing. 
  #############################
  print "Ticking Tree Root"
  tstart = bb.get('treeTickCount')
  if tr1.tick(dummy,bb) != b3.SUCCESS:
    print "mainloop: Tree FAIL"
    test_fails += 1
  
  total_cost += task.Cost
  total_ticks += bb.get('treeTickCount')
  total_utility += task.get_Utility()
  
  #  Record some stats from this test
  tend = bb.get('treeTickCount')
  ticks_per_step = tend-tstart
  tick_total += tend  
   
  bb.set('treeTickCount',0)  # 
  
     
#log.close

print "total_ticks: ", total_ticks, "  tick_total: ", tick_total

print "Finished Simulation: ", test_name
print "Average tree tick count:    ", tick_total/Ntests
print "Total Cost:                 ", total_cost
print "Total Utility (x1000):      ", 1000.0 * total_utility
print "Average Cost:               ", total_cost/Ntests
print "Average Utility (x1000):    ", 1000.0 * total_utility/Ntests
print "walk_to_fire ticks:             ", walk_trip.N_ticks
print " fly_to_fire ticks:             ", fly_to_dest.N_ticks
print ""

print "           avg ticks    avg cost    avg Util    walk ticks   fly ticks    fails"
print ""
s =  "{}        {}            {}       {:04.2f}        {}            {}        {}\n".format(id, tick_total/Ntests, total_cost/Ntests, 1000*total_utility/Ntests, walk_trip.N_ticks, fly_to_dest.N_ticks, test_fails) 

print s
file.write(s)
file.close()


#print "Walk / Fly Ratio:               ", float(ticks_meth1) / float(ticks_meth2)
print ""
print "Failed tests:               ", test_fails
print "Total Cost:                 ", max(data[:,4])
  
Npts = bb.get('treeTickCount')

 
