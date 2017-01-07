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
			if self.skip == True and c != "]":
				self.skip = True
			elif self.skip == True and c == "]":
				self.skip = False
			elif c == "<" and self.pointer - 1 >= 0:
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
				if self.memory[self.pointer] == 0:
					self.skip = True
				else:
					self.stack.append(self.index+1)
			elif c == "]":
				if self.memory[self.pointer] == 0:
					self.stack.pop()
				else:
					self.index = self.stack[-1]-1
		else:
			print("MACHINE: "+c+" is not a valid command")

	#print out the current state of the memory
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
		#load in new data
		self.formattedCode = code
		self.lineMapping = {}
		line = 0
		curr = 0
		for c in list(code):
			if c == "\n":
				line += 1
			elif isBFCommand(c):
				self.lineMapping[curr] = line
				curr += 1
		code = re.sub(r'[^\<\>\+\-\,\.\[\]]',r'',code)
		self.code = list(code)
		self.maxIndex = len(code) - 1
	# Step through one command of code
	def step(self):
		if self.finished == False:
			self.doAction(self.code[self.index])
			self.index += 1
			self.cycles += 1
			if self.index > self.maxIndex:
				self.finished = True
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
		self.stack = []
		self.finished = False
		self.output = []
		self.maxPoint = self.memSize-1
		self.memory = [0]*(self.memSize)
		self.cycles = 0
	# soft reset the machine, just move the index pointer back and stuff
	def reset(self):
		self.index = 0
		self.pointer = 0
		self.skip = False
		self.stack = []
		self.finished = False
		self.output = []
		self.memory = [0]*(self.memSize)
		self.cycles = 0
	# skips current loop
	def skipLoop(self):
		try:
			currLoop = self.stack[-1]
		except:
			return None
		while currLoop in self.stack:
			self.step()

	#converts code to a nice html version
	def codeToHTML(self):
		array = self.formattedCode.split("\n")
		selected = self.getSelectedLine()
		output = []
		output.append("<pre>")
		for n,l in enumerate(array):
			if n == selected:
				count = 0
				for k in self.lineMapping.keys():
					if self.lineMapping[k] < selected:
						count+=1
				relIndex = self.index - count
				newL = ""
				i = 0
				for c in list(l):
					if i == relIndex and isBFCommand(c):
						newL = newL+"<span style=\"color: red;\">"+c+"</span>"
						i += 1
					elif isBFCommand(c):
						i += 1
						newL = newL+c
					else:
						newL = newL+c
				output.append("<b style=\"color: #2196f3;\">" + str(n) + "  " + newL + "</b>")
			else:
				output.append(str(n) + "  " + l)
		output.append("</pre>")
		print(output)
		return "\n".join(output)

	# Creates a html console with the current output
	def consoleToHTML(self):
		rows = int(self.maxPoint/ 8)+1
		rowH = 30 # editable (in two places :/ )
		h = rowH*rows
		output = []
		#This Console style comes fron 
		#http://www.java2s.com/Code/HTMLCSS/Tags/CreateConsolewindowlikestyletodisplaycode.htm
		output.append("<style type=\"text/css\">")
		output.append("    console {")
		output.append("        background: #000;")
		output.append("        border: 3px groove #ccc;")
		output.append("        color: #ccc;")
		output.append("        display: block;")
		output.append("        padding: 5px;")
		output.append("        height: "+str(h)+"px;")
		output.append("     }")
		output.append("    code {")
		output.append("        background: #000000;")
		output.append("        color: #FFFFFF;")
		output.append("    }")
		output.append("</style>")
		output.append("<console>")
		output.append("    <code>")
		for l in self.output:
			if l == "\n":
				output.append("<br></br>")
			else:
				output.append(l)
			
		output.append("    </code>")
		output.append("</console>")
		return "".join(output)
	# Creates a html representation of memory
	def memoryToHTML(self):
		#set up
		rows = int(self.maxPoint/ 8)+1
		rowH = 30 # editable
		colW = 30 # editable
		hexLen = 4 # editable
		h = rowH*rows
		output = []
		output.append("<svg style=\"height:"+str(h)+"px; width: 100%\">")
		output.append("<g>")
		#generate background
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
		#generate memory
		y = rowH - (rowH/4)
		for r in range(0,rows):
			off = 15
			hexData = "{0:#0{1}x}".format(r*8,hexLen+2)
			output.append(text(0,y,hexData,off,"#000000"))
			off = colW + 3*(hexLen+24) 
			for i in range(0,8):
				curr = (r*8)+i
				hexData = "{0:0{1}x}".format(self.memory[curr],hexLen)
				if curr == self.pointer:
					color = "#2196f3"
				else:
					color = "#000000"
				output.append(text(0,y,hexData,off,color))
				off += + colW + 3*hexLen
			y = y + rowH
		#finish up
		output.append("</g>")
		output.append("</svg>")
		return "".join(output)
# Checks if a character is 
def isBFCommand(c):
	m = re.search(r'([\<\>\+\-\,\.\[\]])', c)
	if m:
		if m.group(1):
			return True
	return False

#testing
if __name__ == '__main__':
	machine = Machine(16)
	code = '''
		+++++ +++               Set Cell #0 to 8
		[
		    >++++               Add 4 to Cell #1; this will always set Cell #1 to 4
		    [                   as the cell will be cleared by the loop
		        >++             Add 4*2 to Cell #2
		        >+++            Add 4*3 to Cell #3
		        >+++            Add 4*3 to Cell #4
		        >+              Add 4 to Cell #5
		        <<<<-           Decrement the loop counter in Cell #1
		    ]                   Loop till Cell #1 is zero
		    >+                  Add 1 to Cell #2
		    >+                  Add 1 to Cell #3
		    >-                  Subtract 1 from Cell #4
		    >>+                 Add 1 to Cell #6
		    [<]                 Move back to the first zero cell you find; this will
		                        be Cell #1 which was cleared by the previous loop
		    <-                  Decrement the loop Counter in Cell #0
		]                       Loop till Cell #0 is zero
		
		The result of this is:
		Cell No :   0   1   2   3   4   5   6
		Contents:   0   0  72 104  88  32   8
		Pointer :   ^
		
		>>.                     Cell #2 has value 72 which is 'H'
		>---.                   Subtract 3 from Cell #3 to get 101 which is 'e'
		+++++ ++..+++.          Likewise for 'llo' from Cell #3
		>>.                     Cell #5 is 32 for the space
		<-.                     Subtract 1 from Cell #4 for 87 to give a 'W'
		<.                      Cell #3 was set to 'o' from the end of 'Hello'
		+++.----- -.----- ---.  Cell #3 for 'rl' and 'd'
		>>+.                    Add 1 to Cell #5 gives us an exclamation point
		>++.                    And finally a newline from Cell #6

	'''
	machine.loadCode(code)
	machine.step()
	sys.stdout.write(machine.memoryToHTML())
