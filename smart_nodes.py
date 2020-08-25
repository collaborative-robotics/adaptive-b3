
import sys
import b3 

import numpy as np
import random
import itertools

#########################################################################
#
#      Basic ('Random') node with stochastic success 
#
#########################################################################
class Rn2(b3.Action): 
    action_thresh = 0.5     # prob of success
    
    def tick(self, tick):
        if(self.BHdebug == 1):
            print "Rn2: Node ticked: ", self.Name
        self.N_ticks += 1  
        #cnt = tick.blackboard.get('treeTickCount')  #  only count the leaf ticks
        #cnt += 1
        #tick.blackboard.set('treeTickCount', cnt)
        self.prob()  # update probability estimate
        #threshold = tick.blackboard.get('thresh', tick.tree.id, self.id)
        a = random.random()        
        if(self.BHdebug == 1):
            print self.Name, " thresh: ", self.action_thresh, " Random: ", a
        if(a < self.action_thresh):
          self.N_success += 1
          #print self.Name + " has succeeded"
          return b3.SUCCESS;  
        else:
          #print self.Name + " has failed"
          return b3.FAILURE;


#########################################################################
#
#      Detect Fire based on how many ticks to arrive
# 
#      > maxwalktime ticks,   too late -> FAIL
#      <= 4 maxwalktime,      in time --> SUCCEED
#
#########################################################################
class detectfire(b3.Action): 
    def tick(self, tick):
        if(self.BHdebug == 1):
            print "detectfire: Node ticked: ", self.Name
        cnt = tick.blackboard.get('treeTickCount')  #  only count the leaf ticks
        traveltime = cnt  # only works when walking is First node in tree. 
        cnt += 1
        tick.blackboard.set('treeTickCount', cnt)
        self.prob()  # update probability estimate
        if(self.BHdebug == 1):
            print "detectfire: travel time: ", cnt, "  distance: ", tick.blackboard.get('distance')
        if (traveltime <= tick.blackboard.get('maxwalktime')):
            return b3.SUCCESS;  
        else:
            return b3.FAILURE;

#########################################################################
#
#      Walk until destination is reached OR distance limit exceeded
#
#######################################################################
class WalkTillDestination(b3.Decorator):
    def __init__(self, child, max_loop=-1):
        super(WalkTillDestination, self).__init__(child)
        self.max_loop = max_loop
        

    def open(self, tick):
        tick.blackboard.set('i', 0, tick.tree.id, self.id)
        tick.blackboard.set('distance', 0)
        

    def tick(self, tick):
        self.N_ticks += 1
        if not self.child:
            print "WalkTillDestination is not set up with a Child! ... quitting"
            quit() 

        #i = tick.blackboard.get('i', tick.tree.id, self.id)
        d = tick.blackboard.get('distance')

        if(tick.blackboard.get('distancetofire') is None):
            print "WalkTillDestination: distancetofire has not been defined. "
            print "           (please set up 'distancetofire' in the blackboard)."
            print "    ... Halting."
            quit()
        
        i=1
        if(self.BHdebug == 1):
            print "WalkTillDestination:  i ", i, "  d ", d
        tmpCost = 0
        while self.max_loop < 0 or i < self.max_loop:
            status = self.child._execute(tick)
            tmpCost += self.child.Cost
            if(self.BHdebug == 1):
                print "WalkTillDest: Cost: ", tmpCost
                print "WalkTillDest: ticks: ", i
            if status == b3.FAILURE:
                i += 1
            else:             
                if(self.BHdebug == 1):
                    print "counted successful step: ", d
                i += 1
                d += 1
                tick.blackboard.set('distance', d)    # step counts iff successful
                if d > tick.blackboard.get('distancetofire'):
                    status = b3.SUCCESS
                    break;
                else:
                    status = b3.FAILURE  #(but keep trying)

        self.Cost = tmpCost  # my cost is total cost of the child ticks. 
        #tick.blackboard.set('i', i, tick.tree.id, self.id)
            
        #tick.blackboard.set('i', 0, tick.tree.id, self.id)  # reset max_loop counter each failure
                                                            # but not total distance traveled
        return status  # succeeded or failed to reach dest before max_loop

        

      
#########################################################################
#
#     Node with variable physics based on state type 
#          P(success) depends on state in node-dependent manner
#
#      Walking version
#
#########################################################################
class walk(b3.Action): 
    def tick(self, tick):
        self.N_ticks += 1 
        tick.blackboard.inc('treeTickCount', 1)  # count the leaf ticks
        if(self.BHdebug == 1):
            print "walk Node: ", self.Name, " distance: ", tick.blackboard.get('distance')
        #threshold = tick.blackboard.get('thresh', tick.tree.id, self.id)
        phys = tick.blackboard.get('WalkPhysics')
        self.get_state(tick.blackboard)  
        #print phys

        if(self.BHdebug == 1):
            print "walk: ", self.Name, " terrain state: ", self.state
            print "     my cost is: ", self.Cost
            
        threshold = phys[self.Name][self.state]  # get success prob based on state 
        a = random.random() 
        self.N_tik2[self.state] += 1 
        if(a < threshold):
          #self.N_success       += 1
          #self.N_suc2[self.state]   += 1
          if(self.BHdebug == 1):
              print self.Name + " has succeeded "
          return b3.SUCCESS
        else:
          if(self.BHdebug == 1):
              print self.Name + " has failed"
          return b3.FAILURE
      
    def get_state(self,bb):    # update your own state
        d = bb.get('distance')
        L = len(bb.get('Terrain'))
        #print "Distance: ", d, " out of ", L
        self.state = bb.get('Terrain')[d]


#########################################################################
#
#     Node with variable physics based on state type 
#          P(success) depends on state in node-dependent manner
#
#      fly to destination
#
#########################################################################
class fly(b3.Action): 
    def tick(self, tick):
        self.N_ticks += 1
        cnt = tick.blackboard.inc('treeTickCount', 1)  #  only count the leaf ticks 
        if(self.BHdebug == 1):
            print "fly: Node ticked: ", self.Name
        a = random.random() 
        #self.N_tik2[state] += 1
        #print self.Name, " P(success): ", self.N_success, " / ", self.N_ticks, " = ", self.Ps
        #print "Node received: ", x
        if(a < 0.9):#  flying mostly succeeds
          self.N_success       += 1
          #self.N_suc2[state]   += 1
          #print self.Name + " has succeeded"
          return b3.SUCCESS
        else:
          #print self.Name + " has failed"
          return b3.FAILURE


      
#########################################################################
#self
#     Node with variable physics based on state type 
#          P(success) depends on state in node-dependent manner
#
#########################################################################
class fightfire(b3.Action): 
    def tick(self, tick):
        cnt = tick.blackboard.inc('treeTickCount',1)  #  only count the leaf ticks
       #threshold = tick.blackboard.get('thresh', tick.tree.id, self.id)
        phys = tick.blackboard.get('FirePhysics')
        if(self.BHdebug == 1):
            print "fightfire: Node ticked: ", self.Name, " Fire state: ", self.state
        threshold = phys[self.Name][self.state]  # get success prob based on state
        #if(state == 3): 
          #print "\n\n\nName: " + self.Name + "  FireState: " , state ," Threshold: ", threshold
        a = random.random()
        #if(self.Name == "")
        self.N_tik2[self.state] += 1
        #print self.Name, " P(success): ", self.N_success, " / ", self.N_ticks, " = ", self.Ps
        #print "Node received: ", x
        if(a < threshold):
          self.N_success       += 1
          self.N_suc2[self.state]   += 1
          #print self.Name + " has succeeded"
          return b3.SUCCESS
        else:
          #print self.Name + " has failed"
          return b3.FAILURE

    def get_state(self,bb):    # update your own state (set at main loop for this leaf)
        pass
        

