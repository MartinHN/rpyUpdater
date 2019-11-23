# rpyUpdater
Tool to run scripts located on boot partition on RPi SDCards

usefull when using for minor modifications based on same RPI image 

# Install
git clone where ever you want ant add to systemctl,
you can use the template file (modifying it with the path of your install)
then  copy rpyUpdater.service to `/lib/systemd/system/`

```
sudo systemctl daemon-reload
sudo systemctl enable rpyUpdater
```


# Folder structure
this script expects two directories 
```
/boot/customConfig/
                  once/
                  each/
```
once are for script executed once only and ... each at each boot ...

each directory will populate with :
* logs/ => stdout and stderr of scripts
* done/ => scripts are copied here when successful
* quarantine/ => scripts are copied here when UNsuccessful , see logs/


# Scripts
they expect sh or python3 scripts and alternatively a file (case independent)

 named HOSTNAME to change hostName of pi
 named UPDATEME to try to pull last version of this tool using git


# Custom behaviours
Ech script can start with custom comments to modify its behavior
a valid comment is a line formatted as following :  
`#rpy.<param>:<valueAsInteger> `

example:
   `#rpy.timeout:10 `

valid config parameters are (case-sensitive)

* timeout `(default:120)` : the time in seconds before scripts is considered hung 
* internetTimeout `(default:0)` : if positive, will start to ping google before to start the script until connected or specified Time out has been spent
* scriptGroup `(default:0)` : scripts will be sorted by their groups, for "once" scripts, each new group will trigger a reboot


# BE CAREFULL NOTES
with great power comes great puberty

* from now, one reboot with a faulty sudo script will suffice to burn your sd image up...

* if a "once" script manually triggers reboot, it'll be executed each time as the system can't now if it succeeded

* if scripts waits for user input it'll hang for ever until timeout and put in quarantine



# Notes
* an example of service to use with systemd

* on OSX hostname change is simulated in /tmp




