#!/usr/bin/python2

# Author: Blake Hannaford
# Date: 2020-9-10

#  Now (11-Sep-20) introducting ROS and CRTK again
# test version without ROS or CRTK

# based on crtk_cp_example.py:
# Author: Anton Deguet
# Date: 2015-02-22

# (C) Copyright 2015-2019 Johns Hopkins University (JHU), All Rights Reserved.

# --- begin cisst license - do not edit ---

# This software is provided "as is" under an open source license, with
# no warranty.  The complete license can be found in license.txt and
# http://www.cisst.org/cisst/license.txt.

# --- end cisst license ---

# Start a single arm using
# > rosrun dvrk_robot dvrk_console_json -j <console-file> -c crtk_alpha

# To communicate with the arm using ROS topics, see the python based example dvrk_arm_test.py:
# > rosrun crtk_pythoself.n_client crtk_arm_test.py <arm-name>
 

# For the abt move_cp() example, here's the setup:

# > mkdir CWS (a catkin workspace)

# > cd CWS
# > catkin_make   # set this up as an official catkin workspace

# > cd src
# > git pull << the four crtk repos below (one per command) >>

#############  your files should look like #####################
#CWS/--
      #|
      #-- src/ --
              #|
              #-- crtk-python-client   (cloned here)
              #-- crtk-msgs            (cloned here)
              #-- adaptive-b3          (cloned here)
              #-- behavior3py          (abt_dev branch cloned here)
#
# #  Dont forget 
# > cd CWS
# > source devel/setup.bash
# > catkin build
#
# # link all the deps into your adaptive-b3 folder:
# > cd src/adaptive-b3
# > ln -s ../crtk-python-client .
# > ln -s ../crtk-msgs .
# > ln -s ../behaviour3py/b3 .
#
# # Note, python doesn't like '-' in imports so you have to rename two packages:
# > cd adaptive-b3
# > mv crtk-python-client crtk_python_client 
# > mv crtk-msgs crtk_msgs
# 

# fire up ROS
# > cd <<anywhere>>
# > roscore &

#
#   Finally ready to run this simulation!!
#
# > cd CWS
# > rosrun adaptive_b3 crtk_abt_move_cp_example.py

import crtk_python_client.src.crtk as crtk
import crtk_msgs
import math
import sys
#  ROS melodic installation: 
#http://wiki.ros.org/melodic/Installation/Ubuntu#melodic.2FInstallation.2FDebEnvironment.Environment_setup
sys.path.insert(0,'/opt/ros/melodic/lib/python2.7/dist-packages')
import rospy
import numpy
import PyKDL    # couldn't get this to work but not important


#adaptive BT imports and misc.
import sys
import b3                 # behavior trees (abt_dev branch) (see behavior3py above)
import random
import numpy as np
import time
#import uuid
#import matplotlib 
#import matplotlib.pyplot as plt 
#import smart_nodes as sn   # leaf nodes to simulate fire fighting robot scenario
import smart_selectors as ss  # adaptive selector nodes using various algorithms.

#########################################################################################
##  quick and dirty methods to stub the PyKDL dependency
#class F:
    #def __init__(self,p=[0,0,0],M=np.ones([3,3])):
        #self.p = p
        #self.M = M
        
#def PyKDL.Vector( x,y,z):
    #return [x,y,z]

#def PyKDL.Rotation.RPY(r,p,z):
    #return np.ones([3,3])

#########################################################################################
#
#    Define some physical points (sort of corresponding to the figure)
#
Start = PyKDL.Frame()
# generic start pose
Start.p = PyKDL.Vector(0.0,0.0,0.0)
Start.M = PyKDL.Rotation.RPY(0,0,0)

mm10 = 0.010

#A = PyKDL.Frame()
A = PyKDL.Frame()
A.p = PyKDL.Vector(mm10,mm10,mm10)
A.M = PyKDL.Rotation.RPY(0,0,0)

#B1 = PyKDL.Frame()
B1 = PyKDL.Frame()
B1.p = PyKDL.Vector(2*mm10,4*mm10,mm10)
B1.M = PyKDL.Rotation.RPY(0,0,0)

#B2 = PyKDL.Frame()
B2 = PyKDL.Frame()
B2.p = PyKDL.Vector(4*mm10,3*mm10,mm10)
B2.M = PyKDL.Rotation.RPY(0,0,0)

#B3 = PyKDL.Frame()
B3 = PyKDL.Frame()
B3.p = PyKDL.Vector(3*mm10,3*mm10,mm10)
B3.M = PyKDL.Rotation.RPY(0,0,0)


#C = PyKDL.Frame()
C = PyKDL.Frame()
C.p = PyKDL.Vector(2.5*mm10,2*mm10,mm10)
C.M = PyKDL.Rotation.RPY(0,0,0)


valid_points_list = [Start, A, B1, B2, B3, C]
#
#    The basic idea will be to move a physical robot through a set of points
#     controlled by an adaptive BT.  Each point-to-point move will have a (simulated) probability
#     of success.   By adaptive BT execution, the robot will find the most reliable path from 
#     A--> C (via Bi intermediate points). 
#
# 
#   This leaf class will move our robot from one point to another.   To simulate real-world issues,
#     The node will simulate a "failure" result by checking a random number.   If the 0-1.0 random draw
#     is below self.Ps, the move will not happen and the node will return b3.FAILURE.   Otherwise, 
#     commands to crtk will cause a physical move command (move_cp()).
#
class move_to_point(b3.Action):
    # p = prob of success (fixed param)
    # goal_point = where to move
    # parentcl = parent class (which contains the crtk_moveto method instance
    def __init__(self, p, goal_point,parentcl):
        super(move_to_point, self).__init__()
        if (p<0.0) or (p>1.0):
            print 'node initialized with invalid probability of success: ', p
            quit()
        if not goal_point in valid_points_list:
            print 'node set for "illegal" point"', goal_point
            quit() 
        
        self.Ps = p
        self.goal_point = goal_point
        self.move_to_call = parentcl.move_cp  # this is the function which does a move via crtk
    
    def tick(self, tick):
        self.N_ticks += 1 
        tick.blackboard.inc('treeTickCount', 1)  # count the leaf ticks
        if(self.BHdebug == 1):
            print "Move to point node: ", self.Name
            print "     my Ps is: ", self.Ps
            
        a = random.random() 
        if(a < self.Ps):
            if(self.BHdebug == 1):
                print self.Name + " has succeeded "
            self.move_cp_wrap(self.goal_point)
            return b3.SUCCESS
        else:
          if(self.BHdebug == 1):
              print self.Name + " has failed"
          return b3.FAILURE
      
    def move_cp_wrap(self,point):
        self.move_to_call(point)  # invoke the move_cp() method
        #if False:
            #print('Robot is moving now')
            #for i in range(10):
                #print '>',
                #sys.stdout.flush()
                #time.sleep(0.05)
            #print''

# example of application using device.py
class crtk_adaptive_bt_example:
    def __init__(self,v=False):
        self.VERBOSE = v
        
    # configuration
    def configure(self, device_namespace):
        print 'Configuring the example' 
        
        #################
          # ROS initialization
        if not rospy.get_node_uri():
            rospy.init_node('crtk_abt_move_cp_example', anonymous = True, log_level = rospy.WARN)

        print(rospy.get_caller_id() + ' -> configuring crtk_device_test for: ' + device_namespace)
        # populate this class with all the ROS topics we need
        self.crtk_utils = crtk.utils(self, device_namespace)
        self.crtk_utils.add_operating_state()
        self.crtk_utils.add_measured_cp()
        self.crtk_utils.add_move_cp()
        
        
        #################
        # set up the BT (see figure in doc)
        
        self.tree = b3.BehaviorTree()
        # instantiate the leaves
        self.n_st_A = move_to_point(1.0, A, self) # always succeeds
        self.n_A_B1 = move_to_point(0.1, B1,self) # rarely succeeds
        self.n_A_B2 = move_to_point(0.3, B2,self) # sometimes succeeds
        self.n_A_B3 = move_to_point(0.9, B3,self) # usually succeeds
        self.n_Bx_C = move_to_point(1.0, C,self)   # always succeeds
        # give them descriptive names
        self.n_st_A.Name = 'Move Start->A'
        self.n_A_B1.Name = 'Move A->B1'
        self.n_A_B2.Name = 'Move A->B2'
        self.n_A_B3.Name = 'Move A->B3'
        self.n_A_B1.BHdebug = 1
        self.n_A_B2.BHdebug = 1
        self.n_A_B3.BHdebug = 1
        self.n_Bx_C.Name = 'Move Bx->C'
        
        
        nodes = [self.n_st_A, self.n_A_B1, self.n_A_B2, self.n_A_B3, self.n_A_B3, self.n_Bx_C]
        
        OVERALL_DEBUG = 0
        for n in nodes:
            n.BHdebug = OVERALL_DEBUG
            # Select how to compute "Utility" for a node
            #n.Utility_Mode = 'RATIO'      # utility = P(S) / Cost
            n.Utility_Mode = 'NEG_COST'   # utility = -1*P(S)*Cost
            n.Cost = 1  # for now all the same
        
        
        #you can play around with different costs for the nodes:
        self.n_A_B1.Cost = 1
        self.n_A_B2.Cost = 2
        self.n_A_B3.Cost = 10
        self.n_st_A.Cost = 0
        self.n_Bx_C.Cost = 0
        #
        #  different types of smart selector are possible
        #self.SmSel_A_Bx = ss.SmrtSel00([self.n_A_B1, self.n_A_B2,self.n_A_B3])# traditional ("dumb") selector
        self.SmSel_A_Bx = ss.SmrtSel01([self.n_A_B1, self.n_A_B2,self.n_A_B3]) # tick in order of empirical success prob.
   
        # Sel02 is only used with a "state" or "environment" prior
        #self.SmSel_A_Bx = ss.SmrtSel02([self.n_A_B1, self.n_A_B2,self.n_A_B3])
        
            # Use cost to rank the nodes (not interesting for example tree above b/c cost is fixed)
            #self.SmSel_A_Bx = ss.SmrtSel03([self.n_A_B1, self.n_A_B2,self.n_A_B3])
        
        # use utility to rank the nodes (P(s)*(1-Cost))
        #self.SmSel_A_Bx = ss.SmrtSel04([self.n_A_B1, self.n_A_B2,self.n_A_B3])
        
        self.SmSel_A_Bx.BHdebug = 0
        self.SmSel_A_Bx.Name = 'Three point selector'


        self.seqnode = b3.Sequence([self.n_st_A, self.SmSel_A_Bx, self.n_Bx_C]) 
        
        self.tree.root = self.seqnode
        
        #    here 

   
    
    def run_bt_tests(self,Ntests):
        self.n_success = 0
        self.n_fail = 0
        bb = b3.Blackboard()   
        bb.set('treeTickCount', 0)
        bb.set('TotalCost',0)
        print 'Starting some test runouts'
        for iter in range(0,Ntests):
            print "Running Test number: ",iter
            # target is an unused param
            # blackboard is the common data store
            target = {}
            if self.tree.tick(target,bb) == b3.SUCCESS:
                if self.VERBOSE:
                    print ' BT returns SUCCESS\n'
                self.n_success += 1
            else:
                if self.VERBOSE:
                    print ' BT returns FAILURE\n'
                self.n_fail +=1
                
        ratio = self.n_success/float(Ntests)
        print 'Success ratio: {:.1%}'.format(ratio)
        print 'N success, N fail: ', self.n_success, self.n_fail, '{:.1%}'.format(self.n_success/float(Ntests)) 
        self.SmSel_A_Bx.report_stats()
        print 'Total tick count:   ', bb.get('treeTickCount')
        print 'TotalCost:          ', bb.get('TotalCost')
                
# use the class now, i.e. main program
if __name__ == '__main__': 
    Nruns = 1000
    VERBOSE = True
    dev_namespace = 'test'
    print ' Starting up the example'
    example = crtk_adaptive_bt_example(VERBOSE)
    example.configure(dev_namespace)
    example.run_bt_tests(Nruns)
    
