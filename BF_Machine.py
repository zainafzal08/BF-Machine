import re
import sys
# Functions borrowed from my gannt chart library

#formats a rectangle html tag
# x and y is the position of the element in pixels
# w and h are width and height in pixels
# f is the fill colour in hex
# o is opacity as a float 0 to 1
# rounded is a boolean specifying if the rectangle should be rounded or not
def rect(x,y,h,f,o):
	return "<rect fill-opacity=\""+str(o)+"\" x=\""+str(x)+"\" y=\""+str(y)+"\" width=\"100%\" height=\""+str(h)+"\" fill=\""+str(f)+"\"></rect>"

# formats text html
# x and y are position
# s is the string to display
# offset is the offset from the x,y given (how much it should be shifted right)
# color is text color in hex
# id is just how you choose to identify each element for interactivity
# 	This is what will be sent to the specified handler when the text is clicked on
#	If Null the text is not interactive (such as label text)
def text(x,y,s,offset,color):
	text = "<text fill='"+color+"' style=style=\"cursor: default; user-select: none; -webkit-font-smoothing: antialiased; font-family: Roboto; font-size: 14px;\" x=\""+str(x)+"\" y=\""+str(y)+"\" dx=\""+str(offset)+"\">"+s+"</text>"
	return text

# The Main Machine Object Class
class Machine():
	#set up machine state
	def __init__(self, size):
		self.memSize = size
		self.hardReset()
	#get the current line
	def getSelectedLine(self):
		return self.lineMapping[self.index]
	#do a BF command
	def doAction(self, c, **params):
		if isBFCommand(c):
			#Movement commands
			if c == "<" and self.pointer - 1 >= 0:
				self.pointer = self.pointer - 1
			elif c == ">" and self.pointer + 1 <= self.maxPoint:
				self.pointer = self.pointer + 1	
			elif c == "+":
				self.memory[self.pointer] = self.memory[self.pointer] + 1
			elif c == "-":
				self.memory[self.pointer] = self.memory[self.pointer] - 1
			elif c == ".":
				self.output.append(chr(self.memory[self.pointer]))
			elif c == ",":
				x = ord(params['input'])
				self.memory[self.pointer] = x
			elif c == "[":
				# we count skipped loops in loop depth
				self.loopDepth+=1
				if self.memory[self.pointer] == 0:
					# jump to the end of this loop. 
					self.skip = True
				else:
					self.stack.append(self.index+1)
			elif c == "]":
				if self.memory[self.pointer] == 0:
					#loop over, pop and move on
					self.loopDepth-=1
					self.stack.pop()
				else:
					#loop is not over, keep going
					self.index = self.stack[-1]-1
		else:
			print("MACHINE: "+c+" is not a valid command")

	#print out the current state of the memory to stdout
	def printMemory(self, lineSize):
		curr = 0
		while curr <= self.maxPoint:
			sys.stdout.write(str(curr).rjust(4) + " |")
			for i in range(0,lineSize):
				try:
					num = self.memory[curr+i]
					if curr+i == self.pointer:
						sys.stdout.write((">"+str(num)).rjust(4))
					else:
						sys.stdout.write("{0:4d}".format(num))
				except:
					break
			sys.stdout.write("\n")
			curr = curr + lineSize
	# Load some code into the machine
	def loadCode(self, code):
		# Reset Machine State
		self.hardReset()
		#load in the code with all formatting for display
		self.formattedCode = code
		#generate a dictionary linking commands to lines for displays
		self.lineMapping = {}
		line = 0
		curr = 0
		for c in list(code):
			if c == "\n":
				line += 1
			elif isBFCommand(c):
				self.lineMapping[curr] = line
				curr += 1
		#generate the pure code with no comments or formatting
		code = re.sub(r'[^\<\>\+\-\,\.\[\]]',r'',code)
		self.code = list(code)
		self.maxIndex = len(code) - 1
		if len(self.code) == 0:
			return False
		return True
	# Step through one command of code
	def step(self, **params):
		if "run" in params:
			run = params["run"]
		else:
			#default value
			run = True
		if self.finished == False:
			if self.cycles > self.maxCycles:
 				self.output.append("Program has passed the maximum number of permitted cycles\n")
 				self.output.append("and has been terminated, this usually occurs due to a infinite loop.\n")
 				self.output.append("If this is not the case, edit the maxCycles value in the machine.")
 				self.finished = True
 				return
			if run == True:
				self.doAction(self.code[self.index])
			self.index += 1
			self.cycles += 1
			if self.index > self.maxIndex:
				self.finished = True
				self.index = self.maxIndex
			if self.skip:
				self.skip = False
				self.nextLoop(False)
	# Run untill no more code
	def run(self):
		while self.finished == False:
			self.step()
	# Run for a specifed number of steps
	def runFor(self, num):
		curr = 0
		while curr < num and self.finished == False:
			self.step()
			curr += 1

	# Hard Reset of the machine
	def hardReset(self):
		self.index = 0
		self.formattedCode = ""
		self.code = ""
		self.maxIndex = 0
		self.pointer = 0
		self.skip = False
		self.maxCycles = 5000
		# Keeps track of the loops
		self.stack = []
		self.finished = False
		self.output = []
		# The maximum memory address
		self.maxPoint = self.memSize-1
		self.memory = [0]*(self.memSize)
		# Total number of times step has been called
		# In this machine every command is 1 cycle long.
		self.cycles = 0
		# Variables to help with debugging navigation
		# Such as skip loop and next loop
		self.loopDepth = 0
	# soft reset the machine, keeps code in place so it can be run again
	def reset(self):
		self.index = 0
		self.pointer = 0
		self.skip = False
		self.stack = []
		self.finished = False
		self.output = []
		self.memory = [0]*(self.memSize)
		self.cycles = 0
		self.loopDepth = 0
	# skips current loop
	def skipLoop(self):
		# see if not in a loop at all
		if len(self.stack) == 0:
			return None
		elif not self.stack[-1]:
			return None
		# else skip the loop
		currLoop = self.stack[-1]
		# run until the loop is pop'ed off the stack
		while currLoop in self.stack:
			self.step()

	# goes to next loop iteration or if loop is done/skipped
	# goes to the end of the loop
	# run defines if this should go to the next loop with or
	# without running the code
	def nextLoop(self, run):
		# Check if not in a loop at all
		if self.loopDepth == 0:
			return None
		depth = self.loopDepth
		while True:
			if self.code[self.index] == ']' and self.loopDepth == depth:
				self.step(run=run)
				break
			self.step(run=run)

	# Converts code to a nice html version
	def codeToHTML(self):
		array = self.formattedCode.split("\n")
		selected = self.getSelectedLine()
		# set up
		output = []
		output.append("<pre>")
		# print out line numbers and the code
		for n,l in enumerate(array):
			if n == selected:
				count = 0
				#quite bad solution to get the 
				#current commands character index in the line
				for k in self.lineMapping.keys():
					if self.lineMapping[k] < selected:
						count+=1
				#relIndex tells us where in the line the
				#current command is so it cna be highlighted
				#in red
				relIndex = self.index - count
				newL = ""
				i = 0
				# This generates a blue coloured line 
				# for the current running line
				for c in list(l):
					if i == relIndex and isBFCommand(c):
						#This highlights the current character red
						newL = newL+"<span style=\"color: red;\">"+c+"</span>"
						i += 1
					elif isBFCommand(c):
						i += 1
						newL = newL+c
					else:
						newL = newL+c
				# This somehow adds a line break after the selected line
				# no idea how but it kinda looks like a feature so
				# i'm gonna pretend like it's not a bug
				output.append("<b style=\"color: #2196f3;\">" + str(n) + "  " + newL + "</b>")
			else:
				output.append(str(n) + "  " + l)
		# ending tags and return
		output.append("</pre>")
		return "\n".join(output)

	# Creates a html console with the current output
	def consoleToHTML(self):
		# get the size of the memory html
		# and match that. 
		rows = int(self.maxPoint/ 8)+1
		rowH = 30 # editable (in two places :/ )
		h = rowH*rows
		# CSS set up
		output = []
		#This Console style comes mostly from with small edits from me
		#http://www.java2s.com/Code/HTMLCSS/Tags/CreateConsolewindowlikestyletodisplaycode.htm
		output.append("<style type=\"text/css\">")
		output.append("    console {")
		output.append("        background: #000;")
		output.append("        border: 3px groove #ccc;")
		output.append("        color: #ccc;")
		output.append("        display: block;")
		output.append("        padding: 5px;")
		output.append("        height: 23vh")
		output.append("     }")
		output.append("    code {")
		output.append("        background: #000000;")
		output.append("        color: #FFFFFF;")
		output.append("    }")
		output.append("</style>")
		output.append("<console>")
		output.append("    <code>")
		# replace new lines with line breaks 
		# so they will be shown in html
		for l in self.output:
			if l == "\n":
				output.append("<br></br>")
			else:
				output.append(l)
		# end and return
		output.append("    </code>")
		output.append("</console>")
		return "".join(output)
	# Creates a html representation of memory
	def memoryToHTML(self):
		# given 8 cells per row
		# the number of rows is total memory
		# rounded up. Thus if memory is 7 big
		# we get 1 row, not 0
		rows = int(self.maxPoint/ 8)+1
		# some pixel values to define how big the
		# rows and spacing should be
		rowH = 30 # editable
		colW = 30 # editable
		# defines the hex printing padding.
		# for this we assume the cell values is 16 bit. 
		hexLen = 4 # editable
		h = rows*rowH
		output = []
		# open tags
		output.append("<svg style=\"height: 43vh; width: 100%\">")
		output.append("<g>")
		#generate background strips
		y = 0
		even = True
		for r in range(0,rows):
			if even:
				output.append(rect(0,y,rowH,"#EBEBEB",1))
				even = False
			else:
				output.append(rect(0,y,rowH,"#CECECE",1))
				even = True
			y = y + rowH
		#generate the memory

		# Y should be offset to center the text in the rows
		# Try setting y to 0 and you will see why this is 
		# needed. 
		y = rowH - (rowH/4)
		for r in range(0,rows):
			# offset for the row address
			off = 15
			# Print out the address of the current row
			#(0x0000 or 0x0008)
			hexData = "{0:#0{1}x}".format(r*8,hexLen+2)
			output.append(text(0,y,hexData,off,"#000000"))
			# Move offset down a bit before printing cell values
			off = colW + 3*(hexLen+24) 
			# print out 8 values in hex
			for i in range(0,8):
				curr = (r*8)+i
				hexData = "{0:0{1}x}".format(self.memory[curr],hexLen)
				# highlight the cell where the pointer is currently
				if curr == self.pointer:
					color = "#2196f3"
				else:
					color = "#000000"
				output.append(text(0,y,hexData,off,color))
				# Move down the row for the next print
				off += + colW + 3*hexLen
			#move down to the next row
			y = y + rowH
		#finish up
		output.append("</g>")
		output.append("</svg>")
		return "".join(output)
# Checks if a character is a valid BF Command
# Can only be <>[]-+.,
def isBFCommand(c):
	m = re.search(r'([\<\>\+\-\,\.\[\]])', c)
	if m:
		if m.group(1):
			return True
	return False

#testing
if __name__ == '__main__':
	machine = Machine(16)
	code = "[>+<-]+"
	machine.loadCode(code)
	machine.step()
	machine.step()
	print("now on " + str(machine.index))
	machine.printMemory(8)
