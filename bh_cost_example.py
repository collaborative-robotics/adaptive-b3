
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
elif arg == 4:
    test = "Smart Selector 4: Utility"
elif arg == 3:
    test = "Smart Selector 3: Cost"
elif arg == 5:
    test = "tmpTest"
else:
    print "invalid CL argument"
    quit() 

print "Starting "+ test
 

######  Set up tree

tr1 = b3.BehaviorTree()
bb = b3.Blackboard() 



if(1):      # argv = 1
  # Tree structure and nodes
  W1 = walk()
  W2 = walk()
  W3 = walk()
  A = fightfire()
  B = fightfire()
  C = fightfire() 
  DF = detectfire()
  # Vanilla selector node
  walker = b3.Priority([W1, W2, W3])
  walktrip = WalkTillDestination(walker)
  extinguish = b3.Priority([A, B, C]) 
  walk_to_fire = b3.Sequence([walktrip, DF, extinguish])
  flyer = fly()
  fly_to_fire = b3.Sequence([flyer, extinguish])
  tr1.root =  b3.Priority([walk_to_fire, fly_to_fire])
  
  #  NAMES
  tr1.root.Name = "Tree Root"
  A.Name = "ExtA"
  B.Name = "ExtB"
  C.Name = "ExtC"
  detectfire.Name = "detect fire"
  extinguish.Name = "Extinguish" 
  walk.Name = "walk/step"
  walker.Name = "walker"
  walktrip.Name = "walk until destination"
  flyer.Name = "flyer"
  walk_to_fire.Name = "walk_to_fire"
  fly_to_fire.Name = "fly_to_fire"
  W1.Name = "w1"
  W2.Name = "w2"
  W3.Name = "w3"
  test_name = test
  
  # changes to above
  if(test == "Smart Selector 1"):     # argv = 1
    # change the root node!!
    
    tr1.root =  SmrtSel01([fly_to_fire, walk_to_fire])
    walk_to_fire.BHdebug = 0
    fly_to_fire.BHdebug = 0 
    
  # changes to Dumb selector
  if(test == "Smart Selector 1: P(s)"):     # argv = 2 
      # change the root node!! 
    tr1.root =  SmrtSel01([fly_to_fire, walk_to_fire])
    # also change the 2nd level priority nodes to learning 
    walker= SmrtSel02([W1, W2, W3])
    walker.Name = "walker"
    extinguish = SmrtSel02([A, B, C])  #  two parents!!!
    extinguish.Name = "Extinguish" 
    
    #   Debugging 
    
    walk_to_fire.BHdebug = 1
    fly_to_fire.BHdebug = 1
    tr1.root.BHdebug = 1
    tr1.root.Name = "Tree Root"
    
   
  if(test ==  "Smart Selector 3: Cost"):
    print "Initializing "+test
    # also change the 2nd level priority nodes to learning 
    walker = SmrtSel02([W1, W2, W3])
    walker.Name = "walker"
    extinguish = SmrtSel02([A, B, C])  #  two parents!!!
    extinguish.Name = "Extinguish"  
      
      
    # change the root node!!  Use Utility (P(s)/Cost)
    head =   SmrtSel03([fly_to_fire, walk_to_fire])
    tr1.root = b3.Priority([head]) # root doesn't use baseclass so stub it.
      
    head.Name = "Head"
    tr1.root.Name = "Tree Root"
      
    #   Debugging 
      
    walktrip.BHdebug = 0
    walk_to_fire.BHdebug = 1
    fly_to_fire.BHdebug = 1
    flyer.BHdebug = 0
    tr1.root.BHdebug = 0
      
      
  if(test == "Smart Selector 4: Utility"):
    print "Initializing "+test
    # also change the 2nd level priority nodes to learning 
    walker = SmrtSel02([W1, W2, W3])
    walker.Name = "walker"
    extinguish = SmrtSel02([A, B, C])  #  two parents!!!
    extinguish.Name = "Extinguish"  
        
        
        # change the root node!!  Use Utility (P(s)/Cost)
    head =   SmrtSel04([fly_to_fire, walk_to_fire])
    tr1.root = b3.Priority([head]) # root doesn't use baseclass so stub it.
      
    head.Name = "Head"
    tr1.root.Name = "Tree Root"
      
    #   Debugging 
        
    walktrip.BHdebug = 0
    walk_to_fire.BHdebug = 1
    fly_to_fire.BHdebug = 1
    flyer.BHdebug = 0
    tr1.root.BHdebug = 0
       
  if (test == "tmpTest"):
    print "Initializing temporary test tree"
    #  start over with very simple tree
    ta = Rn2()
    ta.action_thresh = 0.8
    ta.Cost = 10
    ta.Name = "Tmp Node A"
    tb = Rn2()
    tb.action_thresh = 0.1
    tb.Cost = 1
    tb.Name = "Tmp Node B"
    
    # set up the root node!!  Use Utility (P(s)/Cost)
    head =   SmrtSel03([ta, tb])
    head.BHdebug = 0
    
    tr1.root = b3.Priority([head]) # root doesn't use baseclass so stub it.
    
    head.Name = "Head"
    tr1.root.Name = "Tree Root" 
  
  
##  set up costs
  
W1.Cost = 1
W2.Cost = 1
W3.Cost = 1

#      Fly Cost   Wk/Fly ratio
# low      260 =  Variable!!
# medium   275 =  55%
# high     290 =  84%
flyer.Cost = 275
  
A.Cost = 1
B.Cost = 1
C.Cost = 1
 

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
#  Walking Physics
walkingphysics = { 'w1': [0.1,     0.1,     0.8,   0],
	           'w2': [0.1,     0.8,     0.1,   0], 
	           'w3': [0.8,     0.1,     0.1,   0]}

bb.set('WalkPhysics',walkingphysics)


#   Fire fighting Physics
#  The idea is that each leaf will perform differently on each fire type
#                         none       fta         ftb        ftc   
#   'mixed' Physics
fire_physics = { 'ExtA': [1.0,        1.0,        0.0,     0.0],
    	         'ExtB': [1.0,	      0.0,        1.0,     0.0], 
	         'ExtC': [1.0,        0.0,        0.0,     1.0]}

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
Ntests = 400
tick_total = 0
ticks_meth1 = 0
ticks_meth2 = 0
test_fails = 0
data = np.zeros((Ntests,5))
dummy = np.zeros(5)

bb.set('TotalCost',0)    

for iter in range(0,Ntests): 
  # randomize the fire type 
  a = random.random() 
  firetype = 0
  if a < 0.3333*0.5:
     firetype = fta
  if 0.3333*.5 < a < 0.6666*0.5:
     firetype = ftb
  if 0.66666*0.5 < a < 0.500:
     firetype = ftc
  bb.set('FireState', firetype) 

  # set terrain state for current step
  bb.set('TerrainState', t)
  tstart = bb.get('treeTickCount')

  #print "step ",j,"  Track Type:  ",track_names[t[j]-1] ,
  #
  #  slight modification, try each extinguisher in turn until 
  #     fire is out
  #
  #  tick the tree 
  #############################
  # just one tick should run the whole thing. 
  #############################
  if tr1.tick(dummy,bb) != b3.SUCCESS:
    print "mainloop: Tree FAIL"
    test_fails += 1
  
  #  Record some stats from this test
  tend = bb.get('treeTickCount')
  ticks_per_step = tend-tstart
  tick_total += tend 
  
  ticks_meth1 += walk_to_fire.N_ticks_all
  ticks_meth2 += fly_to_fire.N_ticks_all
  
  p1 = walk_to_fire.prob()
  p2 = fly_to_fire.prob()
  u1 = walk_to_fire.get_Utility()
  u2 = fly_to_fire.get_Utility()
  
  print "mainloop: probabilities:   walk_to_fire {:4.2f}  fly_to_fire {:4.2f}: ".format(p1,p2)
  print "mainloop: utilities:       walk_to_fire {:8.2e}  fly_to_fire {:8.2e}: ".format(u1,u2)
  
  data[iter][0] = p1
  data[iter][1] = p2
  data[iter][2] = tend
  data[iter][3] = tr1.root.prob()
  data[iter][4] = bb.get('TotalCost')
  
  walk_to_fire.N_ticks_all = 0              # reset tick counts but not learning info
  fly_to_fire.N_ticks_all = 0
  bb.set('treeTickCount',0)  # 
     
log.close

print "Finished Simulation: ", test_name
print "Average tree tick count:    ", tick_total/Ntests
print "walk_to_fire ticks:             ", ticks_meth1
print " fly_to_fire ticks:             ", ticks_meth2
print ""
print "Walk / Fly Ratio:               ", float(ticks_meth1) / float(ticks_meth2)
print ""
print "Failed tests:               ", test_fails
print "Total Cost:                 ", max(data[:,4])
  
Npts = bb.get('treeTickCount')


if(0):
    #########   Graph the data
    #fig = plt.figure()

    # Two subplots, the axes array is 1-d
    f, ax = plt.subplots(2, sharex=True)
    #ax[0].plot(x, y)
    #ax[0].set_title('Sharing X axis')
    #ax[1].scatter(x, y)


    indx = range(0,Ntests) 
    p1_line    = ax[0].plot(indx, data[:,0], label="Walking to Fire")
    p2_line    = ax[0].plot(indx, data[:,1], label='Flying to Fire')
    ticks_line = ax[0].plot(indx, data[:,2]/350,label='ticks')
    proot_line = ax[0].plot(indx, data[:,3], label='P(root)')

    #ax[1].plot(indx, data[:,4], label='Cumulative Cost')

    #p1_leg = plt.legend(handles=(p1_line,p2_line,ticks_line,proot_line), loc=1)

    ax[0].legend()
    ax[1].legend()
    
    #f, ax  = plt.subplots(2, sharex=True)
    #ax[0].plot(data[:,0],data[:,2],'ro')
    ax[0].set_title(test_name + ' / Costs: Flying = ' + str(flyer.Cost) + '/  Walk time limit: ' + str(bb.get('maxwalktime')) ) 
    ax[0].axis([0,Ntests,-0.1,1.1])
    #ax[1].axis([0,Ntests,0,40000])
    #ax[1].plot(data[:,0],data[:,1],'bd')
    #ax[1].set_title('Avg Number of ticks')
    ##ax[1].axis([0,n,0,10]) 
    #gfile = raw_input("Enter graphics filename: ")
    #plt.savefig(gfile + '.png' , dpi=200)
    plt.show()

