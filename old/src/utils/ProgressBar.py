import sys
import os

class ProgressBar:
	"""Create a simple progress bar in ASCII"""

	size = 20	# lenght of the progress bar
	percent = 0	# filled percentage of the progress bar
	output = sys.stdout

	def __init__(self, size=None, percent=None, output=None):
		if size != None:
			self.size = size
		if percent != None:
			self.percent = percent
		if output != None:
			self.output = output

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
		percent = self.percent*100
		progress += "] " + str("%.2f" % percent) + "%"
		if self.output != os.devnull:
			self.output.write(progress)
			self.output.flush()
		return progress

	def update(self, percent, d=True):
		self.percent = percent
		if d:
			self.draw()