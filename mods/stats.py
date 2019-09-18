""" show statistics on suicide. """

__version__ = 1

import ob
import random
import time

from ob import Object, k
from ob.clk import Repeater
from ob.hdl import Event
from ob.tms import elapsed, today, to_day

from obot.rss import Fetcher, to_time

run = Object()

## init

def init():
    for name in ob.keys(wanted):
        obj = ob.get(wanted, name, None)
        if obj:
            e = Event()
            e.txt = ""
            for key in ob.keys(obj):
                if k.cfg.options and key not in k.cfg.options:
                    continue
                val = ob.get(obj, key, None)
                if val:
                    sec = seconds(val)
                    repeater = Repeater(sec, stat, e, name="stats.%s" % key)
                    repeater.start()

## defines

startdate = "2018-10-05 00:00:00"
starttime = to_day(startdate)
source = "https://bitbucket.org/bthate/obot"

## exceptions

class ENOSTATS(Exception):

    pass

## functions

def seconds(nr, period="jaar"):
    if not nr:
        return nr
    return ob.get(nrsec, period) / float(nr)

def nr(name):
    for key in ob.keys(wanted):
        obj = ob.get(wanted, key, None)
        for n in ob.keys(obj):
            if n == name:
                return ob.get(obj, n)
    raise ENOSTATS(name)

## COMMANDS

def stats(event, **kwargs):
    args = event.args
    txt = "Sinds %s\n" % time.ctime(starttime)
    delta = time.time() - starttime
    for name, obj in ob.items(wanted):
        for key, val in ob.items(obj):
            needed = seconds(nr(key))
            if not needed:
                continue
            nrtimes = int(delta/needed)
            txt += "\n%s #%s %s %s in %s" % (key.upper(), nrtimes, ob.get(tags, key, ""), ob.get(zorg, random.choice(list(ob.keys(zorg))), ""), random.choice(gemeenten))
    event.reply(txt.strip())

def stat(event, **kwargs):
    e = Event()
    ob.update(e, kwargs)
    name = event.rest or e.name or "suicide" 
    if "." in name:
        name = name.split(".")[-1]
    name = name.lower()
    delta = time.time() - starttime
    awake = time.time() - today()
    try:
        needed = seconds(nr(name))
    except ENOSTATS:
        return
    if needed:
        nrtimes = int(delta/needed)
        txt = "%s #%s" % (name.upper(), nrtimes)
        if name in omschrijving:
            txt += " (%s)" % ob.get(omschrijving, name)
        txt += " elke %s" % elapsed(seconds(nr(name)))
        if name in soort:
            txt += " door een %s" % ob.get(soort, name)
        else:
            txt += " door een %s" % random.choice(list(soort.values()))
        txt += " bijv. in %s" % random.choice(gemeenten)
        if name in tags:
            txt += " %s" % ob.get(tags, name)
        else:
            txt += " %s" % random.choice(list(tags.values()))
        if name in urls:
            txt += " - %s" % ob.get(urls, name)
        k.fleet.announce(txt)

## DATA

nrsec = Object()
nrsec.dag = 24 * 60 * 60.0
nrsec.jaar = 365 * nrsec.dag
nrsec.weekend = 2 / 7 * (24 * 60 * 60.0 * 365) / 52
nrsec.avond = 16 / 24 * (24 * 60 * 60.0)

times = Object()
times.weekend = 2 / 7 * (24 * 60 * 60.0 * 365) / 52
times.avond = 16 / 24 * (24 * 60 * 60.0)
times.dag = 24 * 60 * 60.0
times.jaar = 365 * 24 * 60 * 60.0

rechter = Object()
rechter.ibs = 8171
rechter.rm = 16171
rechter.vwm = 6516
rechter.mvv = 4034
rechter.vm = 5566
rechter.mev = 45
#rechter.om = 0
rechter.zm= 6

drugs = Object()
drugs.speed = 20000
drugs.cocaine = 50000
drugs.alcohol = 400000
drugs.wiet = 500000

e33 = Object()
e33.melding = 61000

recepten = Object()
recepten.antipsychotica = 150000
recepten.antidepresiva = 600000
recepten.slaapmiddel = 1000000

demografie = Object()
demografie.ambulant = 792000
demografie.verslaving = 13000
demografie.schizofrenie = 9800
demografie.depressie = 9600
demografie.verslaafden = 2074278
demografie.arbeidshandicap = 103000
demografie.huisartsen = 11345
demografie.zorgmijder = 24000

cijfers = Object()
cijfers.melding = 61000
cijfers.opnames = 24338
cijfers.crisis = 150000
cijfers.oordeel = 150000
cijfers.pogingen = 94000
cijfers.incidenten = 66000
cijfers.poh = 1300000
cijfers.vergiftigingen = 25262
cijfers.overlast = 18000
cijfers.insluiting = 240000
cijfers.aangiftes = 134000
cijfers.suicide = 1871
cijfers.burenoverlast = 12000
cijfers.uitzetting = 5900
cijfers.volwassendoop = 500
cijfers.tumor = 12000
cijfers.detox = 65654
cijfers.acuut = 8000
cijfers.spoedeisendpoging = 14000
cijfers.weguitkliniek = 2539
cijfers.bewindvoering = 295000
cijfers.suicidegedachtes = 410000

medicijnen = Object()
medicijnen.amitriptyline = 189137
medicijnen.paroxetine = 186028
medicijnen.citalopram = 154620
medicijnen.oxazepam = 133608
medicijnen.venlafaxine = 112000
medicijnen.mirtazapine = 110742
medicijnen.quetiapine = 84414
medicijnen.diazepam = 72000
medicijnen.sertraline = 68000
medicijnen.haloperidol = 59825

oordeel = Object()
oordeel.verwijs = cijfers.crisis * 0.85 
oordeel.uitstroom = cijfers.crisis * 0.05
oordeel.opname = cijfers.crisis * 0.10

alarm = Object()
alarm.politie = 0.30 * cijfers.crisis
alarm.hap = 0.40 * cijfers.crisis
alarm.keten = 0.30 * cijfers.crisis

dbc = Object()
dbc.middelgebondenstoornissen = 33060
dbc.somatoformestoornissen = 21841
dbc.cognitievestoornissen = 25717
dbc.angststoornissen = 54458
dbc.aanpassingsstoornissen = 43079
dbc.depressievestoornissen = 102361
dbc.eetstoornissen = 8688
dbc.restgroepdiagnose = 16996
dbc.ontbrekendeprimairediagnose = 3030
dbc.andereproblemenredenvoorzorg = 49286
dbc.schizofrenieenanderepsychotischestoornissen = 6798
dbc.bipolairestoornissen = 3569
dbc.posttraumatischestressstoornis = 24716
dbc.persoonlijkheidsstoornissen = 36574
dbc.adhd = 25951
dbc.gedrag = 1176
dbc.kindertijdoverig = 1035
dbc.autismespectrum = 9436

halfwaarde = Object()
halfwaarde.zyprexa = 30
halfwaarde.abilify = 75
halfwaarde.haldol = 30
halfwaarde.alprazolam = 11
halfwaarde.orap = 55
halfwaarde.paracetamol = 2.5
halfwaarde.lorazepam = 12
halfwaarde.paroxetine = 21 
halfwaarde.citalopram = 35
halfwaarde.oxazepam = 8.2
halfwaarde.quetiapine = 6
halfwaarde.diazepam = 100
halfwaarde.wiet = 7

perdag = Object()
perdag.medicijnen = medicijnen
perdag.drugs = drugs

suicidejaar = Object()
suicidejaar.y2008 = 1435
suicidejaar.y2009 = 1525
suicidejaar.y2010 = 1600
suicidejaar.y2011 = 1647
suicidejaar.y2012 = 1753
suicidejaar.y2013 = 1857
suicidejaar.y2014 = 1839
suicidejaar.y2015 = 1871 
suicidejaar.y2016 = 1894
suicidejaar.y2017 = 1917

ziekenhuis = Object()
ziekenhuis.y2010 = 7800
ziekenhuis.y2011 = 9600
ziekenhuis.y2012 = 9200
ziekenhuis.y2013 = 8300
ziekenhuis.y2014 = 8500

seh = Object()
seh.y2010 = 13700
seh.y2011 = 16000
seh.y2012 = 15800
seh.y2013 = 13300
seh.y2014 = 14000

suicide = Object()
suicide.suicide = suicidejaar.y2017

pogingen = Object()
pogingen.pogingen = cijfers.pogingen

poging = Object()
poging.ziekenhuis = ziekenhuis.y2014
poging.seh = seh.y2014

show = Object()
show.opnames = 24338
show.crisis = 150000
show.oordeel = 150000
show.pogingen = 94000
show.incidenten = 66000
show.vergiftigingen = 25262
show.overlast = 18000
show.insluiting = 24000
show.aangiftes = 134000
show.suicide = 1871
show.burenoverlast = 12000
show.uitzetting = 5900
show.volwassendoop = 500
show.detox = 65654
show.acuut = 8000
show.spoedeisendpoging = 14000
show.weguitkliniek = 2539
show.bewindvoering = 295000
show.pogingen = cijfers.pogingen

wanted = Object()
wanted.suicide = suicide
wanted.pogingen = pogingen
wanted.rechter = rechter
wanted.oordeel = oordeel
wanted.alarm = alarm
wanted.e33 = e33

omdat = Object()
omdat.blokkeren = "met antipsychotica de werking van receptoren BLOKKEREN en dat dat benadeling van de gezondheid is."
omdat.wetboek = "het Wetboek van Strafrecht zegt dat mishandeling wordt gelijkgesteld aan opzettelijke benadeling van de gezondheid."
omdat.benadeling = "men op de hoogte is van de benadeling is er van opzet altijd sprake."
omdat.vergiftigt = "men vergiftigt kan worden door deze medicijnen."
omdat.zolang = ", zolang een arts de bloedspiegel van een medicijn niet meet, de toestand van vergiftiging niet opgeheven word."
omdat.toestand = "men met deze toestand de kans op overlijden geeft."
omdat.dood = "men eraan dood gaat."

zorg = Object()
zorg.interventie = "een interventie, bestaande uit een vorm van verzorging, bejegening, behandeling, begeleiding of bescherming"
zorg.toediening = "toediening van medicatie, vocht en voeding, regelmatige medische controle of andere medische handelingen"
zorg.maatregel = "pedagogische of therapeutische maatregelen"
zorg.opname = "opname in een accommodatie"
zorg.beperking = "beperking van de bewegingsvrijheid"
zorg.seperatie = "afzondering of separatie in een daartoe geschikte verblijfsruimte"
zorg.beperking = "beperking van het recht op het ontvangen van bezoek of het gebruik van communicatiemiddelen"
zorg.toezicht = "toezicht op betrokkene"
zorg.onderzoek = "onderzoek aan kleding of lichaam"
zorg.controle = "controle op de aanwezigheid van gedrag beïnvloedende middelen"
zorg.beperkingen = "beperkingen in de vrijheid het eigen leven in te richten, die tot gevolg hebben dat betrokkene iets moet doen of nalaten."

tags = Object()
tags.keten = "#burgemeester"
tags.politie = "#broodjepindakaas"
tags.hap = "#triagetrien"
tags.verwijs = "#maandagweer"
tags.uitstroom = "#zorgwekkend"
tags.opname = "#meermedicijn"  
tags.crisis = "#triade"
tags.suicide = "#wetverplichteggz"
tags.pogingen = "#prettigweekend" 
tags.incidenten = "#jammerdan"    
tags.acuut = "#geenbedvoorjou"    
tags.zorgmijder = "#helaas"       
tags.inwoners = "#gebodenvrucht"  
tags.crisis = "#medicijnen"
tags.alarm = "#telaat"
tags.oordeel = "#geencrisis"
tags.vergiftigingen = "#overduur"
tags.neurotoxisch = "#overdosis" 
tags.schizofrenie = "#gifmedicijn"
tags.angst = "#gifmedicijn"
tags.depressie = "#gifmedicijn"
tags.meds = "#gifmedicijn"
tags.ibs = "#overlast"
tags.rm = "#benadeling"
tags.vwm = "#maatregel"
tags.vm = "#nogeven"
tags.mvv = "#direct!!"
tags.mev = "#kieserzelfvoor"
tags.om = "#ffkijken#"
tags.zm = "????"

omschrijving = Object()
omschrijving.ibs = "inbewaringstelling"
omschrijving.rm = "rechterlijke machtiging"
omschrijving.vm = "voorlopige rechterlijke machtiging"
omschrijving.mvv = "machtiging voortgezet verblijf"
omschrijving.vwm = "voorwaardelijke rechterlijke machtiging"
omschrijving.mev = "machtiging eigen verzoek"
omschrijving.zm = "zelfbinding machtiging"
omschrijving.om = "observatie machtiging"
omschrijving.keten = "ggz besluit tot crisisbeoordeling"
omschrijving.politie = "politie vraagt om crisisbeoordeling"
omschrijving.hap = 'huisartsenpost vraagt om crisisbeoordeeling'
omschrijving.verwijs = "crisisdienst maakt vervolg afspraak"
omschrijving.uitstroom = "crisisdienst maakt geen vervolgafspraak"
omschrijving.opname = 'niet meten, maar off-label tot "therapeutische" werking'
omschrijving.suicide = "behandelplan is niet op te vragen"
omschrijving.pogingen = "suicide poging is mislukt"
omschrijving.weekend = "niet bereikbaar tot maandag"
omschrijving.avond = "wachten tot de volgende ochtend"
omschrijving.incidenten = "code 33 gemeld bij politie - overlast veroorzaakt door gestoord/overspannen persoon"
omschrijving.acuut = "spoedeisende psychiatrische hulp ingeschakeld"
omschrijving.zorgmijder = "patient durft geen zorg meer te ontvangen"
omschrijving.inwoners = "5% van de nederlanders heeft GGZ problemen"
omschrijving.crisis = "situatie is dusdanig dat men vraagt om een crisisbeoordeling"
omschrijving.alarm = "opschaling van zorg NA de crisis"
omschrijving.oordeel = "brengt patient aan voor beoordeling"
omschrijving.vergiftigingen = "opgestapelde werking van giftige medicijnen"
omschrijving.neurotoxisch = "2 maanden zyprexa is genoeg"
omschrijving.speed = "speed gebruikt"
omschrijving.cocaine = "cocaine gebruikt"
omschrijving.alcohol = "alcohol gedronken"
omschrijving.wiet = "wietje gerookt"
omschrijving.antipsychotica = "antipsychotica ingenomen"
omschrijving.antidepresiva = "antidepressiva ingenomen"
omschrijving.slaapmiddel = "slaapmiddel ingenomen"
omschrijving.ambulant = "patient/behandelaar contact"
omschrijving.verslaving = "diagnose verslaving"
omschrijving.schizofrenie = "diagnose schizofrenie"
omschrijving.depressie = "depressieve patient"
omschrijving.amitriptyline = "depressie"
omschrijving.paroxetine = "antipsychotica"
omschrijving.citalopram = "sedatie"
omschrijving.oxazepam = "sedatie"
omschrijving.venlafaxine = "depressie"
omschrijving.mirtazapine = "depressie"
omschrijving.quetiapine = "antipschotica"
omschrijving.diazepam = "sedatie"
omschrijving.sertraline = "depressie"
omschrijving.haloperidol = "antipsyochotica"
omschrijving.verslaafden = "diagnose verslaving"
omschrijving.inwoners = "koningrijk der nederlanden"
omschrijving.arbeidshandicap = "volledig afgekeurd"
omschrijving.huisartsen = "praktijkhouder in nederland"
omschrijving.opnames = "opgenomen in ziekenhuis"
omschrijving.zorgmijder = "zorgontwijker"
omschrijving.middelgebondenstoornissen = "drugverslaving"
omschrijving.somatoformestoornissen = "lichamelijke klachten heeft waarvoor geen somatische oorzaak (lichamelijke ziekte) gevonden is"
omschrijving.cognitievestoornissen = "waarnemingsvermogen is verstoord"
omschrijving.angststoornissen = "fobien en sociaal niet meer kunnen functioneren"
omschrijving.aanpassingsstoornissen = "karakterstoornis, men is al te gevormd"
omschrijving.depressievestoornissen = "somberheid troef"
omschrijving.eetstoornissen = "vreetkicks, bolimia, anorexia"
omschrijving.restgroepdiagnose = "niet anders vernoemd, valt niet in een standaard diagnose"
omschrijving.ontbrekendeprimairediagnose = "geen duidelijke diagnose te stellen"
omschrijving.andereproblemenredenvoorzorg = "niet in standaard zorg te plaatsen"
omschrijving.schizofrenieenanderepsychotischestoornissen = "stemmen horen, waan denkbeelden"
omschrijving.bipolairestoornissen = "stemmingswisselingen"
omschrijving.posttraumatischestressstoornis = "stress na trauma"
omschrijving.persoonlijkheidsstoornissen = "aanpassings problemen"
omschrijving.adhd = "te druk, te veel energie"
omschrijving.gedrag = "moelijk opvoedbaar"
omschrijving.kindertijdoverig = "vroegtijdig trauma"
omschrijving.autismespectrum = "valt in een autisme categorie"
omschrijving.seh = "spoedeisende hulp"

periode = Object()
periode.ibs = "voor 6 weken"
periode.rm = "voor 6 maanden"
periode.vlm = "max 18 uur"
periode.mvv = "voor 6 maanden"
periode.vwm = "voor jaren"
periode.mev = "voor jaren"
periode.zb = "voor jaren"
periode.ob = "voor 6 dagen"
periode.keten = "door de week"
periode.politie = "elke dag"
periode.hap = 'buiten kantooruren'
periode.verwijs = "buiten kantooruren en in het weekend"
periode.avond = "'s avonds"
periode.uitstroom = "voor jaren"
periode.opname = 'voor 6 maanden'
periode.suicide = "heel erg lang"
periode.pogingen = "elke dag"
periode.weekend = "in het weekend"
periode.incidenten = "elke dag"
periode.acuut = "elke dag"
periode.zorgmijder = "elke dag"
periode.inwoners = ""
periode.crisis = "elke dag"
periode.alarm = "elke dag"
periode.oordeel = "buiten kantoor uren en in het weekend"
periode.vergiftigingen = "elke dag"
periode.neurotoxisch = "elke dag"

urls = Object()
urls.IBS = "http://www.tijdschriftvoorpsychiatrie.nl/assets/articles/57-2015-4-artikel-broer.pdf"
urls.RM = "http://www.tijdschriftvoorpsychiatrie.nl/assets/articles/57-2015-4-artikel-broer.pdf"
urls.VM = "http://www.tijdschriftvoorpsychiatrie.nl/assets/articles/57-2015-4-artikel-broer.pdf"
urls.MVV = "http://www.tijdschriftvoorpsychiatrie.nl/assets/articles/57-2015-4-artikel-broer.pdf"
urls.VW = "http://www.tijdschriftvoorpsychiatrie.nl/assets/articles/57-2015-4-artikel-broer.pdf"
urls.MEV = "http://www.tijdschriftvoorpsychiatrie.nl/assets/articles/57-2015-4-artikel-broer.pdf"
urls.ZB = "http://www.tijdschriftvoorpsychiatrie.nl/assets/articles/57-2015-4-artikel-broer.pdf"
urls.OB = "http://www.tijdschriftvoorpsychiatrie.nl/assets/articles/57-2015-4-artikel-broer.pdf"
urls.opname = "http://www.tijdschriftvoorpsychiatrie.nl/issues/434/articles/8318"
urls.crisis = "http://www.rijksoverheid.nl/documenten-en-publicaties/rapporten/2015/02/11/acute-geestelijke-gezondheidszorg-knelpunten-en-verbetervoorstellen-in-de-keten.html"
urls.tuchtrecht = "http://tuchtrecht.overheid.nl/zoeken/resultaat/uitspraak/2014/ECLI_NL_TGZRAMS_2014_94?zaaknummer=2013%2F221&Pagina=1&ItemIndex=1"
urls.suicide = "http://www.cbs.nl/nl-NL/menu/themas/bevolking/publicaties/artikelen/archief/2014/2014-4204-wm.htm"
urls.incident = "https://www.wodc.nl/onderzoeksdatabase/2337-de-effectiviteit-van-de-politiele-taakuitvoering-en-de-taken-en-verantwoordelijkheden-van-andere-partijen.aspx"
urls.zorgmijder = "http://www.gezondheidsraad.nl/sites/default/files/samenvatting_noodgedwongen_0.pdf"
urls.acuut = "http://www.gezondheidsraad.nl/sites/default/files/samenvatting_noodgedwongen_0.pdf"
urls.wvggz = "https://www.dwangindezorg.nl/de-toekomst/wetsvoorstellen/wet-verplichte-geestelijke-gezondheidszorg"
urls.politie = "http://www.rijksoverheid.nl/documenten-en-publicaties/rapporten/2015/02/11/acute-geestelijke-gezondheidszorg-knelpunten-en-verbetervoorstellen-in-de-keten.html"
urls.hap = "http://www.rijksoverheid.nl/documenten-en-publicaties/rapporten/2015/02/11/acute-geestelijke-gezondheidszorg-knelpunten-en-verbetervoorstellen-in-de-keten.html"
urls.keten = "http://www.rijksoverheid.nl/documenten-en-publicaties/rapporten/2015/02/11/acute-geestelijke-gezondheidszorg-knelpunten-en-verbetervoorstellen-in-de-keten.html"
urls.verwijs = "http://www.rijksoverheid.nl/documenten-en-publicaties/rapporten/2015/02/11/acute-geestelijke-gezondheidszorg-knelpunten-en-verbetervoorstellen-in-de-keten.html"
urls.uitstroom = "http://www.rijksoverheid.nl/documenten-en-publicaties/rapporten/2015/02/11/acute-geestelijke-gezondheidszorg-knelpunten-en-verbetervoorstellen-in-de-keten.html" 
urls.opnames = "http://www.rijksoverheid.nl/documenten-en-publicaties/rapporten/2015/02/11/acute-geestelijke-gezondheidszorg-knelpunten-en-verbetervoorstellen-in-de-keten.html"
urls.vergifitigingen = "http://www.umcutrecht.nl/getmedia/f9f152e2-8638-4ffc-a05f-fce72f5f416a/NVIC-Jaaroverzicht-2014.pdf.aspx?ext=.pdf"
urls.neurotoxisch = "http://www.umcutrecht.nl/getmedia/f9f152e2-8638-4ffc-a05f-fce72f5f416a/NVIC-Jaaroverzicht-2014.pdf.aspx?ext=.pdf"
urls.incidenten = "http://www.dsp-groep.nl/userfiles/file/Politie%20en%20verwarde%20personen%20_DSP-groep.pdf"
urls.ambulant = "https://www.zorgprismapubliek.nl/informatie-over/geestelijke-gezondheidszorg/"
urls.verslaving = "https://www.zorgprismapubliek.nl/informatie-over/geestelijke-gezondheidszorg/"
urls.poh = "https://www.zorgprismapubliek.nl/informatie-over/geestelijke-gezondheidszorg/"
urls.meds = "https://www.zorgprismapubliek.nl/informatie-over/geestelijke-gezondheidszorg/"
urls.depressie = "https://www.zorgprismapubliek.nl/informatie-over/geestelijke-gezondheidszorg/"
urls.angst = "https://www.zorgprismapubliek.nl/informatie-over/geestelijke-gezondheidszorg/"
urls.schizofrenie = "https://www.zorgprismapubliek.nl/informatie-over/geestelijke-gezondheidszorg/"
urls.detox = "https://www.jellinek.nl/vraag-antwoord/hoeveel-mensen-zijn-verslaafd-en-hoeveel-zijn-er-in-behandeling/"
urls.verslaafden = "https://www.jellinek.nl/vraag-antwoord/hoeveel-mensen-zijn-verslaafd-en-hoeveel-zijn-er-in-behandeling/"
urls.volwassendoop = ""
urls.arbeidshandicap = "http://www.nationalezorggids.nl/gehandicaptenzorg/nieuws/27841-ruim-100-000-mensen-op-sociale-werkplaats.html"
urls.overlast = "http://nos.nl/artikel/2075227-verwarde-huurders-veroorzaken-steeds-meer-overlast.html"
urls.insluiting = "http://www.tweedekamer.nl/downloads/document?id=78ee0f32-7487-4bcc-ba01-e01ace2bc4b4&title=Arrestantenzorg%20Nederland%20Landelijke%20rapportage.pdf"
urls.zyprexa = "http://www.ema.europa.eu/docs/nl_NL/document_library/EPAR_-_Product_Information/human/000287/WC500055611.pdf"
urls.factor = "http://nos.nl/artikel/2090676-aantal-incidenten-met-verwarde-mensen-flink-onderschat.html"
urls.dbc = "https://www.nza.nl/1048076/1048181/Marktscan_ggz_2014_deel_B_en_beleidsbrief.pdf"
urls.dbs2015 = "https://www.rijksoverheid.nl/documenten/rapporten/2016/05/25/marktscan-ggz"
urls.medicijnen="https://www.zorgprismapubliek.nl/informatie-over/geestelijke-gezondheidszorg/geestelijke-gezondheidszorg/row-5/welke-geneesmiddelen-worden-het-meest-voorgeschreven-in-de-ggz/"
urls.pogingen="http://www.nfzp.nl/wp/wp-content/uploads/2010/09/Einddocument-AF0943-Kwaliteitsdcoument-Ketenzorg-bij-Suicidaliteit.pdf"
urls.suicidegedachte="http://www.nfzp.nl/wp/wp-content/uploads/2010/09/Einddocument-AF0943-Kwaliteitsdcoument-Ketenzorg-bij-Suicidaliteit.pdf"
urls.ziekenhuisopnames = "https://www.tweedekamer.nl/kamerstukken/detail?id=2016D13371&did=2016D13371"
urls.seh = "https://www.tweedekamer.nl/kamerstukken/detail?id=2016D13371&did=2016D13371"
urls.epa = "https://www.zorgprismapubliek.nl/informatie-over/geestelijke-gezondheidszorg/ernstige-psychiatrische-aandoeningen/"

soort = Object()
soort.alarm = "patient"
soort.oordeel = "arts"
soort.neurotoxisch = "patient"
soort.angst = "patient"
soort.depressie = "patient"
soort.schizofrenie = "patient"
soort.ibs = "burgemeester"
soort.rm = "civiele rechter"
soort.vm = "civiele rechter"
soort.mvv = "civiele rechter"
soort.vwm = "civiele rechter"
soort.ev = "civiele rechter"
soort.om ="civiele rechter"
soort.zm = "civiele rechter"
soort.politie = "agent"
soort.hap = "huisarts"
soort.keten  = "spv/psychiater"
soort.verwijs = "crisisdienst"
soort.uitstroom = "eigen behandelaar"
soort.suicide = "slachtoffer"
soort.crisis = "burger"
soort.pogingen = "wanhopige patient"
soort.incidenten = "hulproepende patient"
soort.acuut = "vergiftigde patient"
soort.meds = "toegediende patient"
soort.amitriptyline = "patient"
soort.paroxetine = "patient"
soort.citalopram = "patient"
soort.oxazepam = "patient"
soort.venlafaxine = "patient"
soort.mirtazapine = "patient"
soort.quetiapine = "patient"
soort.diazepam = "patient"
soort.sertrali = "patient"
soort.haloperidol = "patient"
soort.insluiting = "politie"
soort.ambulant = "casemanager"
soort.verslaafden = "gebruiker"
soort.slaapmiddel = "insomnia patient"

gemeenten = """Amsterdam
Aa en Hunze
Aalburg
Aalsmeer
Aalten
Achtkarspelen
Alblasserdam
Albrandswaard
Alkmaar
Almelo
Almere
Alphen aan den Rijn
Alphen-Chaam
Ameland
Amersfoort
Amstelveen
Amsterdam
Apeldoorn
Appingedam
Arnhem
Assen
Asten
Baarle-Nassau
Baarn
Barendrecht
Barneveld
Bedum
Beek
Beemster
Beesel
Bellingwedde
Bergeijk
Bergen (Limburg)
Bergen (Noord-Holland)
Bergen op Zoom
Berkelland
Bernheze
Best
Beuningen
Beverwijk
Binnenmaas
Bladel
Blaricum
Bloemendaal
Bodegraven-Reeuwijk
Boekel
Bonaire
Borger-Odoorn
Borne
Borsele
Boxmeer
Boxtel
Breda
Brielle
Bronckhorst
Brummen
Brunssum
Bunnik
Bunschoten
Buren
Bussum
Capelle aan den IJssel
Castricum
Coevorden
Cranendonck
Cromstrijen
Cuijk
Culemborg
Dalfsen
Dantumadeel
De Bilt
De Friese Meren
De Marne
De Ronde Venen
De Wolden
Delft
Delfzijl
Den Haag s-Gravenhage
Den Helder
Deurne
Deventer
Diemen
Dinkelland
Doesburg
Doetinchem
Dongen
Dongeradeel
Dordrecht
Drechterland
Drimmelen
Dronten
Druten
Duiven
Echt-Susteren
Edam-Volendam
Ede
Eemnes
Eemsmond
Eersel
Eijsden-Margraten
Eindhoven
Elburg
Emmen
Enkhuizen
Enschede
Epe
Ermelo
Etten-Leur
Ferwerderadeel
Geertruidenberg
Geldermalsen
Geldrop-Mierlo
Gemert-Bakel
Gennep
Giessenlanden
Gilze en Rijen
Goeree-Overflakkee
Goes
Goirle
Gorinchem (Gorcum of Gorkum)
Gouda
Grave
Groesbeek
Groningen
Grootegast
Gulpen-Wittem
Haaksbergen
Haaren
Haarlem
Haarlemmermeer
Halderberge
Hardenberg
Harderwijk
Hardinxveld-Giessendam
Haren
Harlingen
Hattem
Heemskerk
Heemstede
Heerde
Heerenveen
Heerhugowaard
Heerlen
Heeze-Leende
Heiloo
Hellendoorn
Hellevoetsluis
Helmond
Hendrik-Ido-Ambacht
Hengelo (Overijssel)
s-Hertogenbosch (Den Bosch)
Het Bildt
Heumen
Heusden
Hillegom
Hilvarenbeek
Hilversum
Hof van Twente
Hollands Kroon
Hoogeveen
Hoogezand-Sappemeer
Hoorn
Horst aan de Maas
Houten
Huizen
Hulst
IJsselstein
Kaag en Braassem
Kampen
Kapelle
Katwijk
Kerkrade
Koggenland
Kollumerland en Nieuwkruisland
Korendijk
Krimpen aan den IJssel
Krimpenerwaard
Laarbeek
Landerd
Landgraaf
Landsmeer
Langedijk
Lansingerland
Laren
Leek
Leerdam
Leeuwarden
Leeuwarderadeel
Leiden
Leiderdorp
Leidschendam-Voorburg
Lelystad
Leudal
Leusden
Lingewaal
Lingewaard
Lisse
Littenseradeel
Lochem
Loon op Zand
Lopik
Loppersum
Losser
Maasdriel
Maasgouw
Maassluis
Maastricht
Marum
Medemblik
Meerssen
Menaldumadeel
Menterwolde
Meppel
Middelburg
Midden-Delfland
Midden-Drenthe
Mill en Sint Hubert
Moerdijk
Molenwaard
Montferland
Montfoort
Mook en Middelaar
Muiden
Naarden
Neder-Betuwe
Nederweert
Neerijnen
Nieuwegein
Nieuwkoop
Nijkerk
Nijmegen
Nissewaard
Noord-Beveland
Noordenveld
Noordoostpolder
Noordwijk
Noordwijkerhout
Nuenen, Gerwen en Nedercoreten
Nunspeet
Nuth
Oegstgeest
Oirschot
Oisterwijk
Oldambt
Oldebroek
Oldenzaal
Olst-Wijhe
Ommen
Onderbanken
Oost Gelre
Oosterhout
Ooststellingwerf
Oostzaan
Opmeer
Opsterland
Oss
Oud-Beijerland
Oude IJsselstreek
Ouder-Amstel
Oudewater
Overbetuwe
Papendrecht
Peel en Maas
Pekela
Pijnacker-Nootdorp
Purmerend
Putten
Raalte
Reimerswaal
Renkum
Renswoude
Reusel-De Mierden
Rheden
Rhenen
Ridderkerk
Rijnwaarden
Rijssen-Holten
Rijswijk
Roerdalen
Roermond
Roosendaal
Rotterdam
Rozendaal
Rucphen
Saba
Schagen
Scherpenzeel
Schiedam
Schiermonnikoog
Schijndel
Schinnen
Schouwen-Duiveland
Simpelveld
Sint Anthonis
Sint Eustatius
Sint-Michielsgestel
Sint-Oedenrode
Sittard-Geleen
Sliedrecht
Slochteren
Sluis
Smallingerland
Soest
Someren
Son en Breugel
Stadskanaal
Staphorst
Stede Broec
Steenbergen
Steenwijkerland
Stein
Stichtse Vecht
Strijen
Ten Boer
Terneuzen
Terschelling
Texel
Teylingen
Tholen
Tiel
Tietjerksteradeel
Tilburg
Tubbergen
Twenterand
Tynaarlo
Uden
Uitgeest
Uithoorn
Urk
Utrecht
Utrechtse Heuvelrug
Vaals
Valkenburg aan de Geul
Valkenswaard
Veendam
Veenendaal
Veere
Veghel
Veldhoven
Velsen
Venlo
Venray
Vianen
Vlaardingen
Vlagtwedde
Vlieland
Vlissingen
Voerendaal
Voorschoten
Voorst
Vught
Waalre
Waalwijk
Waddinxveen
Wageningen
Wassenaar
Waterland
Weert
Weesp
Werkendam
West Maas en Waal
Westerveld
Westervoort
Westland
Weststellingwerf
Westvoorne
Wierden
Wijchen
Wijdemeren
Wijk bij Duurstede
Winsum
Winterswijk
Woensdrecht
Woerden
Wormerland
Woudenberg
Woudrichem
Zaanstad
Zaltbommel
Zandvoort
Zederik
Zeevang
Zeewolde
Zeist
Zevenaar
Zoetermeer
Zoeterwoude
Zuidhorn
Zuidplas
Zundert
Zutphen
Zwartewaterland
Zwijndrecht
Zwolle""".split("\n")