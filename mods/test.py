from ob.kernel import k

outtxt = u"Đíť ìš éèñ ëņċøďıńğŧęŝţ· .. にほんごがはなせません .. ₀0⁰₁1¹₂2²₃3³₄4⁴₅5⁵₆6⁶₇7⁷₈8⁸₉9⁹ .. ▁▂▃▄▅▆▇▉▇▆▅▄▃▂▁ .. .. uǝʌoqǝʇsɹǝpuo pɐdı ǝɾ ʇpnoɥ ǝɾ"

def unicode(event):
    event.reply(outtxt)

def reconnect(event):
    bot = k.fleet.get_bot(event.orig)
    bot.announce("reconnect")
    bot._sock.shutdown(2)
    bot._sock.close()
    