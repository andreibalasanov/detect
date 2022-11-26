import time

from PIL import Image, ImageDraw

def annotate(res,image):
	
	src = Image.fromarray(image)
        
	draw = ImageDraw.Draw(src)
        
	for entry in res:
                
		i,score,cl = entry
                
		#print (i,score,cl)
                
		if score > .7:
                        
			draw.rectangle( (i[0], i[1], i[2], i[3]),outline=(255, 0, 0))
        
	return src

class Counter:
	def __init__(self,name,value,count=1):
		self.count = count-1
		self.total = 0
		self.name = name
		self.add (value)
	def average (self):
		return self.total/self.count
	def add (self,value):
		self.total = self.total + value
		self.count = self.count + 1


class ExecOp:
	def __init__(self,name):
		self.name = name
		self.start = time.time()
	def stop (self):
		return time.time() - self.start
class ExecTimer:
	inst = None
	def __init__(self):
		self.counters = {}
	def instance():
		if ExecTimer.inst is None:
			ExecTimer.inst = ExecTimer ()
		return ExecTimer.inst
	def reportOp (self,op):
		key = op.name
		val  = op.stop()
		self.report (key,val)
	def report (self,key,value):
		if key in self.counters:
			self.counters[key].add (value)
		else:
			self.counters[key] = Counter (key,value,1)

	def summary (self,name):
		val = self.counters[name]
		print (val.name," Total: ",val.total," Count:",val.count," Average:",val.average())

	def allsummary(self):
		for e in self.counters:
			self.summary (e)
		
