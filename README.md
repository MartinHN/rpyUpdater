# rpyUpdater
simpleTool to run script from boot partition on RPi


this script expects two directories 
/boot/customConfig/once
/boot/customConfig/each


once are for script executed once only and ... each at each boot ...

they expect sh or python3 scripts and alternatively a file named HOSTNAME to change hostName of pi

each directory will populate with :
* logs/ => stdout and stderr of scripts
* done/ => scripts are copied here when successful
* quarantine/ => scripts are copied here when UNsuccessful , see logs/



an example of service to use with systemd, it expects the script to be placed on boot too but you can change it freely


Noteson OSX hostname change is simulated in /tmp



