#



class RunnerBH(b3.Action):  
        
    def tick(self, tick):
        self.N_ticks += 1
        print "I'm running "+self.Name + " iteration " ,self.iter
        self.iter += 1
        if self.iter < 5 :
           return b3.RUNNING
	else:
	   self.iter = 0
	   self.N_success += 1
	   return b3.SUCCESS

      
      
      
class RandomNodeBH(b3.Action):
    def tick(self, tick):
        x = random.random()
        print x
        tick.blackboard.set('random',x)
        if(x < 0.25):
	  print self.Name + " has succeeded"
	  return b3.SUCCESS;
	if (0.25 <= x < 0.90):
	  print "I'm running: " + self.Name
	  return b3.RUNNING;
	if (x >= 0.9):
	  print self.Name + " has failed"
	  return b3.FAILURE;
	