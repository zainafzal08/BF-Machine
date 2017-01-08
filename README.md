# BF_Debugger
A web debugging enviornment/interpreter for the BrainFuck Programming Langauge

The code in main.py is simply a flask server that generates a very nice interface to interact with the sudo-virtual machine in BF_Machine.py
The BF_Machine.py can easily be removed and used for other purposes, it also has built in capabilities to work via command line with 
all functions being simple to call and not relient on a GUI. In addition the class includes a method for printing memory to a command line. 

If you want to use the machine on your own website with credit feel free, to help out i've  included built in functions 
into the class that generate the current memory, code and console in html. THe sort of html they generate can be seen in the 
given flask implementation. 
