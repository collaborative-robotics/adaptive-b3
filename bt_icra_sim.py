#  test

import sys
import b3
import numpy as np
import random
import itertools
import uuid
import matplotlib 
import matplotlib.pyplot as plt 
import smart_nodes as sn
import smart_selectors as ss

#######################################
#
#  Let's select the test-case
#
####################################### 
 
if len(sys.argv) < 2:
  arg = 'INVALID'
else:
  arg = sys.argv[1]
  
valid_arg = False
if arg == 'S0':
    valid_arg = True
if arg == 'S1':
    valid_arg = True
if arg == 'S2':
    valid_arg = True
if arg == 'S2g':
    valid_arg = True
if arg == 'S3':
    valid_arg = True      
if arg == 'S4':
    valid_arg = True
if arg == 'S5':
    valid_arg = True 

if(not valid_arg):
    print "Command Line input", sys.argv, "is invalid. quitting()"
    quit()
    
test = arg
print "Starting "+ test
########################################
#
#    Set up our Test Tree
#
########################################

tr1 = b3.BehaviorTree()

if(test == "S0"):
  run_id = 'S0: dumb selector'
  n1 = sn.walk()
  n2 = sn.walk()
  n3 = sn.walk() 
  # Vanilla selector node
  task =  ss.SmrtSel00([n1, n2, n3])
  tr1.root = b3.Priority([task]) # root doesn't use base class(!)
  test_name = "Dumb Selector"


if(test == "S1"):
  run_id = 'S1: P(S) order'
  n1 = sn.walk()
  n2 = sn.walk()
  n3 = sn.walk() 
  # Vanilla selector node
  task =  ss.SmrtSel01([n1, n2, n3])
  tr1.root = b3.Priority([task]) # root doesn't use base class(!)
  test_name = "P(S) Rank Selector"
  

if(test == "S2" or test == "S2g"):
  run_id = 'S2: P(S|F) order' 
  test_name = "P(S|F) Rank Selector"

  n1 = sn.walk()
  n2 = sn.walk()
  n3 = sn.walk() 
  # selector node
  task =  ss.SmrtSel02([n1, n2, n3])
  if(test == 'S2g'):
      task.Greedy = True
      run_id = 'S2: P(S|F) Greedy'
      test_name = "P(S|F) Greedy Selector"
  tr1.root = b3.Priority([task]) # root doesn't use base class(!)


if(test == "S3"):
  run_id = 'S3: Cost order'
  n1 = sn.walk()
  n2 = sn.walk()
  n3 = sn.walk() 
  #  selector node
  task =  ss.SmrtSel03([n1, n2, n3])
  tr1.root = b3.Priority([task]) # root doesn't use base class(!)
  test_name = "Cost Rank Selector"


if(test == "S4"):
  run_id = 'S4: Utility order'
  n1 = sn.walk()
  n2 = sn.walk()
  n3 = sn.walk() 
  #  selector node
  task =  ss.SmrtSel04([n1, n2, n3])
  tr1.root = b3.Priority([task]) # root doesn't use base class(!)
  test_name = "Utility Rank Selector"


if(test == "S5"):
  run_id = 'S5: Utility(F) order'
  n1 = sn.walk()
  n2 = sn.walk()
  n3 = sn.walk() 
  #  selector node
  task =  ss.SmrtSel05([n1, n2, n3])
  tr1.root = b3.Priority([task]) # root doesn't use base class(!)
  test_name = "Utility(F) Rank Selector"

n1.Name = "Node 1"  
n2.Name = "Node 2"
n3.Name = "Node 3"
task.Name = "Task Node"

task.Utility_Mode = 'RATIO'      # utility = P(S) / Cost
task.Utility_Mode = 'NEG_COST'   # utility = -1*P(S)*Cost 

TEST_MODE = 0
 
n1.BHdebug = 0
n2.BHdebug = 0
n3.BHdebug = 0
task.BHdebug = TEST_MODE

n1.Cost = 2
n2.Cost = 4
n3.Cost = 1
 
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

##   TESTING
if(TEST_MODE == 1):
   t = [1,1,1,1,1,2,2,2,2,2,3,3,3,3,3]
   t = t + [1,1,1,1,1,2,2,2,2,2,3,3,3,3,3]

terr_len  = len(t)

num = np.zeros(3)

for i in t:
  num[i-1] += 1

print "terrain statistics: "
print num

bb = b3.Blackboard() 
  
bb.set('treeTickCount', 0)
bb.set('distance', 0)
bb.set('Terrain', t)
bb.set('TotalCost',0)

#  Terrain Physics Matrix

#                               snow    grass   parking
#   'mixed' Physics              (1)      (2)      (3)
physics = { 'Node 1': [99,       0.8,     0.1,     0.1],
            'Node 2': [99,       0.1,     0.8,     0.1], 
            'Node 3': [99,       0.1,     0.1,     0.8]}

##
##    13-June   introduce assymetry into physics matrix
#                               snow    grass   parking
#   'mixed' Physics              (1)      (2)      (3)
#physics = { 'Node 1': [99,       0.6,     0.1,     0.1],
            #'Node 2': [99,       0.4,     0.7,     0.4], 
            #'Node 3': [99,       0.1,     0.1,     0.8]}

bb.set('WalkPhysics',physics)

#   Run experiments over the range and log the tick counts

logfile = '14jun_NEGCOST_sim_log.txt'

#########################################################
#  set up the log file
log = open(logfile,'a')
if(TEST_MODE == 1):
   Ntests = 50
else:
   Ntests = 250
    

test_tot_ticks = 0
total_ticks = 0
test_tot_cost = 0
total_cost = 0
test_tot_utility = 0.0
total_utility = 0.0

data = np.zeros((terr_len,3))

print '\n\n       Terrain Length:,',terr_len, '\n\n'
done = False

for iter in range(0,Ntests):
  print "Running Test number: ",iter
  done = False
  task.Greedy = False 
  j = -1
  while (not done):   # walk along the terrain to its end
    j += 1
    if((j > 25) and (test == 'S2g')):
        task.Greedy = True
    tstart = bb.get('treeTickCount')
    #print "step ",j,"  Track Type:  ",track_names[t[j]-1] ,
    while tr1.tick(t,bb) != b3.SUCCESS:  
        test_tot_cost += task.Cost
        test_tot_utility += task.Utility
    test_tot_cost += task.Cost
    test_tot_utility += task.get_Utility()
    
    
    tend = bb.get('treeTickCount')
    ticks_per_step = tend-tstart
    test_tot_ticks += tend-tstart
    #print "   ", tend-tstart , " ticks"
    #print "The BT was ticked ", bb.get('treeTickCount'), " times"
    #  store away run data
    data[j][0] = j
    data[j][1] += ticks_per_step  # collecting for average
    data[j][2] = t[j]  #current terrain
    bb.set('treeTickCount',0)  #
    
    if(bb.get('distance') == terr_len-1):
        done = True
    bb.inc('distance',1)   # count step when SUCCESS
    
  # after each simulation run
  
  bb.set('distance',0)
  total_ticks += test_tot_ticks
  total_cost += test_tot_cost
  total_utility += test_tot_utility/test_tot_ticks   # Util per tick
  test_tot_ticks = 0
  test_tot_cost = 0
  test_tot_utility = 0.0
  
  #n1.report_stats()
  #n2.report_stats()
  #n3.report_stats()
  for node in [n1, n2, n3, task]:
      node.p_reset()
     
log.close



print "Finished Simulation:   ", test_name
print "Total tick count:      ", total_ticks
#print "Total LEAF tick count: ", total_leaf_ticks
    
##  Average the number of ticks at each time over all tests
for j in range(0,terr_len):
  data[j][1] /= Ntests 
  
Npts = bb.get('treeTickCount')

#print "Average run Leaf tick count:", total_leaf_ticks/Ntests
print "Total Cost:                 ", total_cost
print "Total Utility (x1000):      ", 1000.0 * total_utility
print "Average Cost:               ", float(total_cost)/Ntests
print "Average Utility (x1000):    ", 1000.0 * total_utility/Ntests 
print ""

print "                  avg ticks    avg cost    avg Util/tick x 1000 "
print ""
s =  "{}        {}            {}       {:04.2f}  \n".format(run_id, total_ticks/Ntests, total_cost/Ntests, 1000*total_utility/Ntests) 

print s
if(not TEST_MODE):
    log.write(s)
log.close()


#print "P(S)_1", n1.prob(), ' U1 ', n1.get_Utility()
#print "P(S)_2", n2.prob(), ' U2 ', n2.get_Utility()
#print "P(S)_3", n3.prob(), ' U3 ', n3.get_Utility()



## Two subplots, the axes array is 1-d
#f, axarr = plt.subplots(2, sharex=True)
#axarr[0].plot(x, y)
#axarr[0].set_title('Sharing X axis')
#axarr[1].scatter(x, y)

#########   Graph the data
#fig = plt.figure()
INCLUDE_TERRAIN = True
if(INCLUDE_TERRAIN):
    f, ax  = plt.subplots(2, sharex=True)
    ax[0].plot(data[:,0],data[:,2],'ro')
    ax[0].set_title(test_name + ' / Terrain')
    ax[0].axis([0,terr_len,0,4])
    ax[1].plot(data[:,0],data[:,1],'bd')
    ax[1].set_title('Avg Number of ticks, '+test_name )
    ax[1].axis([0,terr_len,0,15])
    #f.title(logfile) 
    plt.show()
else:
    # Just a figure and one subplot
    f, ax = plt.subplots()
    #ax.plot(x, y)
    #ax.set_title('Simple plot') 
    ax.plot(data[:,0],data[:,1],'bd')
    ax.set_title(test_name + ': Avg ticks at each step')
    ax.axis([0,terr_len,0,15])
    ax.set_xlabel('Step')
    ax.set_ylabel('Tick count average')
    #f.title(logfile) 
    plt.show()
