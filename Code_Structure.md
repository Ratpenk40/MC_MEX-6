# Main.py
1) Creating class eloG for the log files

Then in the main function:
2) setting all parameters to zero for initialization
3) Creating the log files instances
4) Setting k_fast etc. with Erik Griffin's values
````
#Python3
k_fast_slow = 0.1
k_slow_fast_low = 0.02
k_slow_fast_high = 0.11
````
5) Reading the parameters and options from the terminal command
     * I should do a standard + better help output
6) Reading the setting file
7) Logging parameters in the "summary_parameters" file = log 
````
log.writeLine("Starting simulation ")
log.writeLine("N. particles " + st(particles))
````

8) ThreeD
 * !! 2D is deprecated I can remove

# Particle_manager.cpp

# Particle_manager.h
is it normal that there is the same name in ifndef?
I modified the ifndef in the PLK-1 header

# setting files and main

# to do:
add phophorate for MEX_6 and MEX-5