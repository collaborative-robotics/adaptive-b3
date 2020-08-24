'''
Dianmu Zhang Jun 2015
Navigation by behavior tree (simulation). 
Tree structure:
root - repeat until success - sequence ([plan, navigate])

Plan a path from (0,0) to any (x, y) in two segments, each segment is a vector
contains the direction and steps information 

first segment: "45 degree" move, possible direction includes "NE", "NW", "SE", "SW"
second segment: possible direction "E", "W", "N", "S"

when the agent navigates through the grid world, it sticks to the plan, it takes
the number of steps stated in the plan (blackboard, steps), in the indicated
directions (blackboard, direction). The noise comes from the stochastic world setting,
which when the agent excute each step, it has 0.97 chance ends up in the indented spot,
0.01 chance stays in the same spot, 0.02 chance 45 degree right or left than the indented
loaction.  

result represent in figure: 
blue dots - actual path with each step the agent took
red line - planned ideal path

acceptable range: 0.03 (which is also the accuracy of each step)
'''

import random
import b3
import Queue
import numpy as np
import matplotlib.pyplot as plt

#pathPlan plans a path with two segments, 
#a) diagonal movement and, b) x or y movement         
class pathPlan(b3.Action):
    def tick(self, tick):
        start = tick.blackboard.get("currPos")
        target = tick.blackboard.get("targetPos")
        deltaX = target[0] - start[0]
        deltaY = target[1] - start[1]
        distance = np.fabs(deltaX) + np.fabs(deltaY)
        tick.blackboard.set("reachTarget", False)
        tick.blackboard.set("distance", distance) #distance info will be used to choose speed
        midPoint = start
        tick.blackboard.set("reachMidpoint", True)
        
        direction = Queue.Queue()
        steps = Queue.Queue()
        print "get here"
        while direction.qsize() > 0:
            direction.get()
        
        while steps.qsize() > 0 :
            steps.get()
        #print "resized ", direction.qsize(), steps.qsize()    
        if deltaX != 0 and deltaY != 0:
            tick.blackboard.set("reachMidpoint", False)
            if deltaX > 0 and deltaY > 0:
                if deltaX < deltaY:
                    midPoint = (deltaX, deltaX)
                    steps.put(deltaX)
                else:
                    midPoint = (deltaY, deltaY)
                    steps.put(deltaY)
                direction.put("NE")
            
            if deltaX < 0 and deltaY < 0:
                if np.fabs(deltaX) < np.fabs(deltaY):
                    midPoint = (deltaX, deltaX)
                    steps.put(-deltaX)
                else:
                    midPoint = (deltaY, deltaY)
                    steps.put(-deltaY)
                direction.put("SW")
                
            if deltaX < 0 and deltaY >0:
                if -deltaX < deltaY:
                    midPoint = (deltaX, -deltaX)
                    steps.put(-deltaX)
                else:
                    midPoint = (-deltaY, deltaY)
                    steps.put(deltaY)
                direction.put("NW")
            
            if deltaX > 0 and deltaY <0:
                if deltaX < -deltaY:
                    midPoint = (deltaX, -deltaX)
                    steps.put(deltaX)
                else:
                    midPoint = (-deltaY, deltaY)
                    steps.put(-deltaY)
                direction.put("SE")
        else:
            tick.blackboard.set("reachTarget", True)
                
        print "plan - start: ", start
        print "plan - mid point: ", midPoint
        tick.blackboard.set("midPoint", midPoint)
        deltaX = target[0] - midPoint[0]
        deltaY = target[1] - midPoint[1]
        
        if deltaX != 0:
            if deltaX > 0:
                steps.put(deltaX)
                direction.put("E")
            elif deltaX < 0:
                steps.put(-deltaX)
                direction.put("W")
        if deltaY != 0:
            if deltaY >0:
                steps.put(deltaY)
                direction.put("N")
            elif deltaY < 0:
                steps.put(-deltaY)
                direction.put("S")
        
        
        tick.blackboard.set("direction", direction)
        tick.blackboard.set("steps", steps)
        #print direction.qsize(), steps.qsize()
        if direction.qsize() > 2 or steps.qsize() > 2:
            raise Exception("direction or steps size is not right!")
        
        
        return b3.SUCCESS

class navigation(b3.Action):
    def tick(self, tick):
        reachTarget = tick.blackboard.get("reachTarget")
        reachMidpoint = tick.blackboard.get("reachMidpoint")
        path = tick.blackboard.get("path")
        if not reachTarget:    
            start = tick.blackboard.get("currPos")
            midPoint = tick.blackboard.get("midPoint")
            target = tick.blackboard.get("targetPos")
            print "start at: ", start
            print "mid point goal: ", midPoint
            print "final target: ", target
            direction = tick.blackboard.get("direction")
            steps = tick.blackboard.get("steps")
            
            epsilon = 0.03 #error range
            distance = tick.blackboard.get("distance")
           
            allowed = int (epsilon*distance)
            #navigate to the midpoint
            if not reachMidpoint:
                action = direction.get()
                deltaX, deltaY = 0,0
             
                if action == "NE":
                    deltaX, deltaY = 1, 1
                if action == "NW":
                    deltaX, deltaY = -1, 1
                if action == "SE":
                    deltaX, deltaY = 1, -1
                if action == "SW":
                    deltaX, deltaY = -1, -1
                
                possibleDelta = [(deltaX, deltaY), (0, deltaY), (deltaX, 0), (0,0)]
                weight = [0.97, 0.01, 0.01, 0.01]
                
                stepNum = steps.get()
                print "steps: ", stepNum
                curr = start
                
                for i in range(stepNum):
                    
                    random_index = np.random.choice(len(possibleDelta),1, p= [0.97, 0.01, 0.01, 0.01])
                    delta = possibleDelta[random_index]
                    prev = path[-1]
                    cx = prev[0] + delta[0]
                    cy = prev[1] + delta[1]
                    path.append((cx,cy))
                
                curr = path[-1]
                print "currently at: ", curr
                #set current location in blackboard
                tick.blackboard.set("currPos", curr)
                
                #allowed range
                #allowed = int(stepNum*epsilon)
                print "allowed range: ", allowed
                
                if (curr[0] > midPoint[0] + allowed) or \
                (curr[0] < midPoint[0] - allowed) or \
                (curr[1] > midPoint[1] + allowed) or \
                (curr[1] < midPoint[1] - allowed):
                    return b3.FAILURE
                
                tick.blackboard.set("reachMidpoint", True)
                print "reach mid point ", curr
            #if it successfully reach the mid point continue to the final destination
            action = direction.get()    
            #curr = tick.blackboard.get("currPos")
            curr = path[-1]
            stepNum = steps.get()
            print "steps: ", stepNum
            if action == "E":
                deltaX, deltaY = 1,0
                possibleDelta = [(1,0), (1,1), (1,-1), (0,0)]
            if action == "W":
                deltaX, deltaY = -1, 0
                possibleDelta = [(-1,0), (-1,-1), (-1,1), (0,0)]
            if action == "N":
                deltaX, deltaY = 0, 1
                possibleDelta = [(0,1), (1,1), (-1,1), (0,0)]
            if action == "S":
                deltaX, deltaY = 0, -1
                possibleDelta = [(0,-1), (1,-1), (-1,-1), (0,0)]
            
            for i in range(stepNum):
                
                random_index = np.random.choice(len(possibleDelta),1, p= [0.97, 0.01, 0.01, 0.01])
                delta = possibleDelta[random_index]
                prev = path[-1]
                cx = prev[0] + delta[0]
                cy = prev[1] + delta[1]
                path.append((cx,cy))
            
            #set current location in blackboard
            tick.blackboard.set("currPos", path[-1])
            
            curr = path[-1]
            print "currently at: ", curr
            #allowed range
            #allowed = int(stepNum*epsilon)
            print "error allowed: ", allowed
            if (curr[0] > target[0] + allowed) or \
            (curr[0] < target[0] - allowed) or \
            (curr[1] > target[1] + allowed) or \
            (curr[1] < target[1] - allowed):
                return b3.FAILURE
            
            tick.blackboard.set("reachTarget", True)
            print "reach final target!"
                 
        return b3.SUCCESS
                
'''
tree set-up
'''

tree = b3.BehaviorTree()
bb = b3.Blackboard()
bb.set("currPos", (0,0)) #always star at (0,0)
bb.set("targetPos", (-100, 125)) #set different targetPos here"
xt = int(-150 +  random.random()*300)
yt = int(-150 +  random.random()*300)
bb.set("targetPos", (xt,yt)) #set different targetPos here"
print "\n\n  Target: ", xt, yt
bb.set("path", [(0,0)])
bb.set("TotalCost", 0)  #  BH: I added this line to be compatible with my modified base node class

plan = pathPlan()
nav = navigation()
planNav = b3.Sequence([plan,nav])
tree.root = b3.RepeatUntilSuccess(planNav,3) #allow 3 trials

goal = "navigation"

#status = tree.tick(goal, bb) 
tree.tick(goal,bb)
path = bb.get("path")

ideal = [(0,0), bb.get("midPoint"), bb.get("targetPos")]

xs = [i[0] for i in path]
ys = [i[1] for i in path]

x_plan = [i[0] for i in ideal]
y_plan = [i[1] for i in ideal]

fig = plt.figure()
ax1 = fig.add_subplot(111)

ax1.set_ylim([-200,200])
ax1.set_xlim([-200,200])
ax1.plot(xs, ys,  color='g', linestyle='-', marker=',',label = "actual path")
ax1.plot(x_plan, y_plan, 'r--',label = "plan")
plt.legend(loc='upper left')
plt.show()


