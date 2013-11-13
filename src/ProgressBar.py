import sys

class ProgressBar:
	size = 20
	percent = 0

	def __init__(self, size=None, percent=None):
		if size != None:
			self.size = size
		if percent != None:
			self.percent = percent

	def draw(self):
		progress = "\r["
		step = 1./float(self.size)
		percent = self.percent
		for i in range(0,self.size-1):
			diff = percent-step
			if diff >= step:
				progress += "="
			elif diff < 0:
				progress += " "
			percent = diff
		progress += "] " + str(self.percent*100) + "%"
		sys.stdout.write(progress)
		sys.stdout.flush()
		return progress

	def update(self, percent, d=True):
		self.percent = percent
		if d:
			self.draw()