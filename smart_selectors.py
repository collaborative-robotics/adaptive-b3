
import sys
import b3 

import numpy as np
import random
import itertools

#########################################################################
#
#      Selector 0:  Choose children in order they are listed
#
#########################################################################       

class SmrtSel00(b3.Composite):
    def __init__(self, children=None):
        super(SmrtSel00, self).__init__(children)

    def tick(self, tick):        
        if(self.BHdebug == 1):
            print "Sel 0: Node ticked: ", self.Name
        children = []
        # go through the children and get estimated P(s) for each 
        for node in self.children:
            #print "Selecting from "+node.Name
            # prob independent of state / experience
            #p = tick.blackboard.get('thresh', tick.tree.id, node.id)
            # prob depends on experience only 
            node.P_selector = node.prob()
            #print "Returned probability: ",p
            children.append(node)
            # sort the probabilities (lowest first)
        #rank = sorted(children, key=lambda node: node.P_selector)  # sort by P(s|F)
        rank = children
        if(self.BHdebug == 1):
            print "dumb selector (sel0): fixed order" 		 
        N = len(rank)
        tmpCost = 0
        for j in range(0,N):
            # Try them in fixed order
            if(self.BHdebug  == 1):
                print "Sel00:",self.Name," ticking "+rank[N-1-j].Name
                print 'SmrSel00: cost: ',self.Cost
            status = rank[j]._execute(tick)
            tmpCost += rank[j].Cost
            self.Cost = tmpCost  # my cost equals total leaf costs
            if status != b3.FAILURE:
                if(self.BHdebug == 1):
                     print "Sel00: ",self.Name, "->", rank[j].name, " Succeeded"
                return status
            if(self.BHdebug == 1):
                 print "Sel00: ",self.Name, "->", rank[j].name, " Failed" 
        return b3.FAILURE
        
        
	

#########################################################################
#
#      Selector 1:  Choose children in order of estimated probability(success)
#
#########################################################################       

class SmrtSel01(b3.Composite):
	def __init__(self, children=None):
		super(SmrtSel01, self).__init__(children)

	def tick(self, tick):        
		if(self.BHdebug == 1):
			print "Sel01: Node ticked: ", self.Name
		children = []
		# go through the children and get estimated P(s) for each 
		for node in self.children:
			#print "Selecting from "+node.Name
			# prob independent of state / experience
			#p = tick.blackboard.get('thresh', tick.tree.id, node.id)
			# prob depends on experience only 
			node.P_selector = node.prob()
			#print "Returned probability: ",p
			children.append(node)
			# sort the probabilities (lowest first)
		rank = sorted(children, key=lambda node: node.P_selector)  # sort by P(s|F)
		if(self.BHdebug == 1):
			tmpstr = "smart selector 01: P(s) Rank: | " 
			for n in rank:
				tmpstr  +=  n.Name + " " +str(n.P_selector) + " |" 
			print tmpstr
		N = len(rank)
		tmpCost = 0
		tmpUtil = 0.0
		for j in range(0,N):
			# Try them in descending order of probability
			if(self.BHdebug  == 1):
				print "Sel01:",self.Name," ticking "+rank[N-1-j].Name
			status = rank[N-1-j]._execute(tick)
			tmpCost += rank[N-1-j].Cost
			if status != b3.FAILURE:
                                if(self.BHdebug == 1):
                                    print "Sel01: ",self.Name, "->", rank[N-1-j].name, " Succeeded"
				self.Cost = tmpCost  # my cost equals total leaf costs
				return status
                       
                        if(self.BHdebug == 1):
                                print "Sel01: ",self.Name, "->", rank[N-1-j].name, " Failed"    
			self.Cost = tmpCost  # my cost equals total leaf costs
		return b3.FAILURE
		
		
	
#########################################################################
#
#      Selector 2:  Choose children in order of Ps(Node,state) = P_i(S|F)
#
#########################################################################       

class SmrtSel02(b3.Composite):
	def __init__(self, children=None):
		super(SmrtSel02, self).__init__(children)
		self.Greedy=False

	def tick(self, tick):        
		if(self.BHdebug == 1):
			print "Sel 02: Node ticked: ", self.Name, "  Greedy: ", self.Greedy
		children = [] 
		j = 0 
		for node in self.children:
			plist = node.prob_state() # get P(s) for this node and all states
			node.get_state(tick.blackboard)     # update sensing state (node.state) for this node
			node.P_selector = plist[node.state] # this specific state
			children.append(node)
		rank = sorted(children, key=lambda node: node.P_selector)  # sort by P(s|F)
		if(self.BHdebug == 1):
			tmpstr = "smart selector 02: State = " + str(rank[0].state) +" P(s|F) Rank: | " 
			for n in rank:
				tmpstr  +=  n.Name +": "+ str(n.P_selector)+ " |" 
			print tmpstr
		N = len(rank)
		if(self.BHdebug==1):
                        print "smart sel 02: ticking leaf: ", rank[N-1].Name
		tmpCost = 0
		if(self.Greedy):  #  only execute the hightest ranked leaf
                    tmpCost = rank[N-1].Cost
                    status = rank[N-1]._execute(tick) 
                    if(self.BHdebug==1):
                        print "Greedy 02: state: ",node.state, "  status: ", status, "   cost: ", tmpCost
                    self.Cost = tmpCost
                    return status
                else:
		    for j in range(0,N):  # execute the children in order of probability
			if(self.BHdebug == 1):
				print "Sel02: I'm ticking ", rank[N-1-j].Name
			tmpCost += rank[N-1-j].Cost
			status = rank[N-1-j]._execute(tick)
                        if status != b3.FAILURE:
                                if(self.BHdebug == 1):
                                        print self.Name,": State: ", rank[N-1-j].state , " SUCCESS "
                                self.Cost = tmpCost  # my cost equals total leaf costs
                                return status
                    self.Cost = tmpCost  # my cost equals total leaf costs
		    return b3.FAILURE
	

#########################################################################
#
#      Selector 3:  Choose children in order of Cost(Node)
#
#########################################################################       

class SmrtSel03(b3.Composite):
	def __init__(self, children=None):
		super(SmrtSel03, self).__init__(children)

	def tick(self, tick):  
		if(self.BHdebug == 1):
			print "Sel 03: Node ticked: ", self.Name
		children = []
		#if (self.Name == "Extinguish"):
		#print "Extinguish: "
		j = 0
		for node in self.children:
			#print "I'm looking at leaf: "+node.Name
			u = node.Cost    # get cost for this Leaf
			if(self.BHdebug == 1):
				print "Sel 03: Leaf Cost: ", u
			children.append(node)
		rank = sorted(children, key=lambda node: node.Cost)  # sort by Cost
		if(self.BHdebug == 1):
			tmpstr = "smart selector 03: Cost Rank: | " 
			for n in rank:
				tmpstr  +=  n.Name + " " + str(n.Cost) + " |" 
			print tmpstr
		N = len(rank)
		tmpCost = 0
		for j in range(0,N):  # execute the children in ASCENDING order of Cost
			if(self.BHdebug == 1):
				print "Sel03: I'm ticking ", rank[j].Name
			tmpCost += rank[j].Cost
			status = rank[j]._execute(tick)
			if status != b3.FAILURE:
				if(self.BHdebug == 1):
					print self.Name,  " SUCCESS "
				self.Cost = tmpCost  # my cost equals total leaf costs
				return status
                self.Cost = tmpCost  # my cost equals total leaf costs
		return b3.FAILURE
			


#########################################################################
#
#      Selector 4:  Choose children in order of Utility(Node)
#
#########################################################################       

class SmrtSel04(b3.Composite):
	def __init__(self, children=None):
		super(SmrtSel04, self).__init__(children)

	def tick(self, tick):  
		if(self.BHdebug == 1):
			print "Sel 04: Node ticked: ", self.Name
		state = tick.blackboard.get('State') 
		children = []
		#if (self.Name == "Extinguish"):
		#print "Extinguish: "
		j = 0
		for node in self.children:
			#print "I'm looking at leaf: "+node.Name
			u = node.get_Utility() # get Utility for this Leaf
			if(self.BHdebug == 1):
				print "Sel 04: ", node.Name, " Leaf Util: ", u
			children.append(node)
		rank = sorted(children, key=lambda node: node.Utility)  # sort by Utility
		if(self.BHdebug == 1):
			tmpstr = "smart selector 04: Utility Rank: | " 
			for n in rank:
				tmpstr  +=  n.Name + " " + str(n.Utility) + " |" 
			print tmpstr
		N = len(rank)
		tmpCost = 0
		for j in range(0,N):  # execute the children in descending order of Utility 
			if(self.BHdebug == 1):
				print "Sel04: I'm ticking ", rank[N-1-j].Name
			tmpCost += rank[N-1-j].Cost
			status = rank[N-1-j]._execute(tick)
			if status != b3.FAILURE:
				if(self.BHdebug == 1):
					print self.Name,": State: ", state , " SUCCESS "
				self.Cost = tmpCost  # my cost equals total leaf costs
				return status
                self.Cost = tmpCost  # my cost equals total leaf costs
		return b3.FAILURE
		
		

#########################################################################
#
#      Selector 5:  Choose children in order of Utility(Node, State)
#
#     USE THIS ONLY ON LEAFS (because only they have states)
#
#########################################################################       

class SmrtSel05(b3.Composite): 
	def __init__(self, children=None):
		super(SmrtSel05, self).__init__(children)

	def tick(self, tick):  
		if(self.BHdebug == 1):
			print "Sel 05: Node ticked: ", self.Name
		state = tick.blackboard.get('State') 
		children = []
		#if (self.Name == "Extinguish"):
		#print "Extinguish: "
		j = 0
		for node in self.children:
			#print "I'm looking at leaf: "+node.Name
			node.get_state(tick.blackboard)  # update node's sensing
			u = node.get_Utility2() # get Utility for this Leaf conditioned on state
			p = node.prob_state()[node.state]
			if(self.BHdebug == 1):
				print "Sel 05: ", node.Name, "State: ", node.state, "Leaf Prob:", p ," Leaf Util: ", u
			children.append(node)
		rank = sorted(children, key=lambda node: node.Utility)  # sort by Utility
		if(self.BHdebug == 1):
			tmpstr = "smart selector 05: Utility Rank: | " 
			for n in rank:
				tmpstr  +=  n.Name + " " + str(n.Utility) + " |" 
			print tmpstr
		N = len(rank)
		tmpCost = 0
		for j in range(0,N):  # execute the children in descending order of Utility 
			if(self.BHdebug == 1):
				print "Sel05: I'm ticking ", rank[N-1-j].Name
			tmpCost += rank[N-1-j].Cost
			status = rank[N-1-j]._execute(tick)
			if status != b3.FAILURE:
				if(self.BHdebug == 1):
					print self.Name,": State: ", state , " SUCCESS "
				self.Cost = tmpCost  # my cost equals total leaf costs
				return status
                self.Cost = tmpCost  # my cost equals total leaf costs
		return b3.FAILURE
		
		 
		