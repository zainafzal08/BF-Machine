# BF_Debugger
A web debugging enviornment/interpreter for the BrainFuck Programming Langauge

The code in main.py is simply a flask server that generates a very nice interface to interact with the sudo-virtual machine in BF_Machine.py. To use simply run main.py as a python script and navigate to http://127.0.0.1:5000/BFD
The interface is self explanatory, just input in your code into the left, click "debug this code" to load it into the virtual machine and the interface should come up. 

the left displays the code, the current line being run in blue, current command in red. 
The top right will be the current memory, with the current cell being pointed to displayed in blue. 
The middle right will be the console showing output
The bottom right will be 6 navigation buttons to run the code, or to step through it slowly. 
**Note that at the moment on some screens the buttons are cut off, this will be fixed asap**

The BF_Machine.py can easily be removed and used for other purposes, it also has built in capabilities to work via command line with 
all functions being simple to call and not relient on a GUI. In addition the class includes a method for printing memory to a command line. 

If you want to use the machine on your own website with credit feel free, to help out i've  included built in functions 
into the class that generate the current memory, code and console in html. THe sort of html they generate can be seen in the 
given flask implementation. 
