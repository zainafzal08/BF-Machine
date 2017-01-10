# BF-Machine
A web debugging enviornment/Virtual Machine for running the BrainFuck Programming Langauge

# Running
The code in main.py is simply a flask server that generates a very nice interface to interact with the sudo-virtual machine in BF_Machine.py. To use simply run main.py as a python script and navigate to http://127.0.0.1:5000/BFD
The interface is self explanatory, just input in your code into the left, click "debug this code" to load it into the virtual machine and the interface should come up. 

# Web Interface
The left displays the code, the current line being run in blue, current command in red. 
The top right will be the current memory, with the current cell being pointed to displayed in blue. 
The middle right will be the console showing output.
The bottom right will be 6 navigation buttons to run the code, or to step through it slowly. 

# The VM
The small virtual machine is within BF_Machine.py and can easily be removed and used for other purposes.
It has built in capabilities to work via command line with all functions being simple to call and not relient on a GUI. 
In addition the class includes a method for printing memory to the command line and allows for easy testing via the runFor commands that allow the vm to be pushed foward a certain number of cycles. 

If you want to use the machine for your own uses for fun or to use on a project feel free! If you are planning to use it for something public a link to this github would be appreciated.

# Generating your own interface
The VM class includes functions that generate the current memory, code and console in html. The sort of html they generate can be seen in the given flask implementation. The code is tailored to work with the given templete and design but can be edited to suit your needs.

# Issues
If you find any issues or have any tips feel free to bring it up or email me at zain.afz@gmail.com
