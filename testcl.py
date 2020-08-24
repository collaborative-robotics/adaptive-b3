
class test:
  def __init__(self):
    self.var1 = 0
    self.var2 = 0
  def setV1(self,x):
    self.var1 = x    
    
    
class level2(test):
  def __init__(self):
    self.var2 = 0
    
  def setV2(self,x):
    self.var2 = x
    
    
tester = test()

tester.var1 = 50
tester.var2 = -1
tester.var3 = 2301

print "test : var 1, var2, var3, ", tester.var1, tester.var2, tester.var3

tester.setV1(-99)

print "test : var 1, var2, var3, ", tester.var1, tester.var2, tester.var3

print "----------"


tester = level2()

tester.var1 = 50
tester.var2 = -1
tester.var3 = 2301

print "test : var 1, var2, var3, ", tester.var1, tester.var2, tester.var3

tester.setV2(-99)

print "test : var 1, var2, var3, ", tester.var1, tester.var2, tester.var3