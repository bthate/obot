# OBOT - 24/7 channel daemon
#
#

"manual"

def help():
    print("OBOT(1)                          User Commands                           OBOT(1)")
    print("")
    print("NAME")
    print("        obot - 24/7 channel daemon")
    print("")
    print("SYNOPSIS")
    print("""        OBOT is a pure python3 IRC chat bot that can run as a background
        daemon for 24/7 a day presence in a IRC channel. It installs itself
        as a service so you can get it restarted on reboot. You can use it
        to display RSS feeds, act as a UDP to IRC gateway, program your own
        commands for it, have it log objects on disk and search them and scan
        emails for correspondence analysis. OBOT uses a JSON in file
        database with a versioned readonly storage. It reconstructs objects
        based on type information in the path and uses a "dump OOP and use 
        OP" programming library where the methods are factored out into
        functions that use the object as the first argument. 
        
        OBOT is placed in the Public Domain and has no COPYRIGHT or LICENSE.
        """)
    print("")
    print("USAGE")
    print("        obot <cmd> [mods=mod1,mod2] [-b] [-d] [-h] [-s] [-v]")
    print("")
    print("OPTIONS")
    print("        -s 		start a shell")
    print("        -v		be verbose")
    print("        -h		print this message")
    print("")
    print("        mods= let's you starts modules on boot, possbile modules to")
    print("        load are: irc,rss,udp")
    print("")
    print("EXAMPLES")
    print("        # show list of commands")
    print("        $ obot cmd")
    print("        cfg,cmd,dpl,edt,fnd,ftc,hlp,icfg,rem,rss,tsk,udp,ver")
    print("")
    print("        # configure the irc client")
    print("        $ obot cfg server=irc.freenode.net channel=\#dunkbots nick=obot")
    print("        channel=#dunkbots nick=obot port=6667 server=irc.freenode.net")
    print("")
    print("        # start the irc client with rss fetcher and udp<->irc gateway running")
    print("        $ obot mods=irc,rss,udp")
    print("")
