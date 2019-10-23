""" list of commands. """

from ob import k

def cmds(event):
    """ show commands. """
    event.reply("|".join(sorted(k.cmds)))

def nr(event):
    event.reply("EM_T04_OTP-CR-117_19")
    
def aangifte(event):
    event.reply("Aangifte van genocide misdrijven door toediening van gif (impotent maken, martelen, doden): dit nummer is de aangifte dat de koning weet dat het gif is en dus genocide. Aangifte nr. EM_T04_OTP-CR-117_19 - https://genoclaim.readthedocs.io #ggz #gifpil")
