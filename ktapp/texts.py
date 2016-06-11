# -*- coding: utf-8 -*-

EMAIL_TEMPLATE_HTML = u'''<html>
<body style="background: rgb(228,222,195); font-family: verdana, sans-serif; font-size: 10pt; padding: 20px; line-height: 1.6">
<p><a href="http://kritikustomeg.org/click/?u={user_id}&t={type}&c={campaign_id}&url=http://kritikustomeg.org/"><img src="http://kritikustomeg.org/email_header.jpg?u={user_id}&t={type}&c={campaign_id}" alt="Kritikus Tömeg" style="width: 100%" /></a></p>
<p>Kedves {username}!</p>
{html_message}
<p><br /></p>
<p>Üdvözlettel,<br />
a KT szerkesztősége<br />
<a href="http://kritikustomeg.org/click/?u={user_id}&t={type}&c={campaign_id}&url=http://kritikustomeg.org/" style="text-decoration: none; color: rgb(146,23,23)">kritikustomeg.org</a><br />
<a href="http://kritikustomeg.org/click/?u={user_id}&t={type}&c={campaign_id}&url=https://www.facebook.com/kritikustomeg/" style="text-decoration: none; color: rgb(146,23,23)">www.facebook.com/kritikustomeg</a></p>
{ps}
</body>
</html>
'''


EMAIL_TEMPLATE_TEXT = u'''Kedves {username}!

{text_message}


Üdvözlettel,
a KT szerkesztősége
http://kritikustomeg.org/
https://www.facebook.com/kritikustomeg/
{ps}
'''


WELCOME_EMAIL_SUBJECT = u'[Kritikus Tömeg] regisztráció'
WELCOME_EMAIL_BODY = u'''<p>Üdvözlünk a Kritikus Tömegen. Ahhoz, hogy hosszú távon is használni tudd az oldalt, szükséged van egy jelszóra, amivel be tudsz lépni. A jelszó megadásához kattints erre a linkre:</p>
<p><a href="{verification_url}" style="text-decoration: none; color: rgb(146,23,23)">{verification_url}</a></p>'''


WELCOME_PM_BODY = u'''Kedves {username}!

Üdvözlünk a Kritikus Tömegen. Ahhoz, hogy hosszú távon is használni tudd az oldalt, szükséged van egy jelszóra, amivel be tudsz lépni. A jelszó megadásához küldtünk egy linket emailben a címedre ({email}). Ha nem találod, nézz be a spam mappába is, hátha oda került véletlenül. Ha sehogy sem találod, [link={reset_password_url}]kérj egy újat[/link].

Mint új regisztráló talán nem tiszta még számodra, mi mindent rejt a KT, ezért itt egy rövid összefoglaló.

Szinte bármilyen információra van szükséged filmekről, színészekről, rendezőkről, itt megtalálod: filmek története, szereplők, képek, díjak, idézetek, érdekességek, folytatások/remake-ek, színészek/rendezők filmográfiája, díjai. Ha pedig még többre vágysz, csak egy kattintás a film jobb felső sarkában az IMDb vagy Wikipedia ikonra, és megkapod.

Egyetlen listában átfuthatod az összes [link=http://kritikustomeg.org/folytatas/17/james-bond-filmek]James Bond-filmet[/link] vagy [link=http://kritikustomeg.org/folytatas/107/stephen-king-feldolgozasok]Stephen King adaptációt[/link]. Az összetett keresőben megtalálhatod [link=http://kritikustomeg.org/osszetett_kereso/?o=-number_of_ratings&director=Steven%20Spielberg&actor=Tom%20Hanks]rendezők és színészek[/link] vagy [link=http://kritikustomeg.org/osszetett_kereso/?o=-number_of_ratings&actor=Harvey%20Keitel,%20Steve%20Buscemi]színészek és színészek[/link] közös filmjeit, vagy akár a [link=http://kritikustomeg.org/osszetett_kereso/?o=-number_of_ratings&avg_rating_min=4&avg_rating_max=&keyword=maffia&year=1970-1979]70-es évek, legalább 4-es átlagú maffiával foglalkozó filmjeit[/link] (ez csak egy példa).

A fentieknél is fontosabb, hogy végre választ kaphatsz a kérdésre: [b]mit nézzek meg ma este?[/b]

Ha mozizni szeretsz, fusd át az [link=http://kritikustomeg.org/bemutatok/]aktuális bemutatókat[/link]. Ha nem akarsz sokat töprengeni, válaszd a [link=http://kritikustomeg.org/napok_filmjei/]nap filmjét[/link]. A hét minden napjára más logika szerint ajánlunk filmet: néha különlegesebbet, néha mainstream-ebbet, de mindenképp kiválót.

Ha viszont pont, hogy szívesen szemezgetsz, böngéssz a toplistákban: nem csak [link=http://kritikustomeg.org/top_filmek/]minden idők legjobb filmjeit[/link] találod itt, hanem [link=http://kritikustomeg.org/top_filmek/?tipus=legjobb&ev=2010]korszak[/link], [link=http://kritikustomeg.org/top_filmek/?tipus=legjobb&orszag=magyar]ország[/link] és [link=http://kritikustomeg.org/top_filmek/?tipus=legjobb&mufaj=akciofilm]műfaj[/link] szerint is szűrhetsz. Ha különlegességre vágysz, ott vannak az [link=http://kritikustomeg.org/top_filmek/?tipus=ismeretlen]ismeretlen gyöngyszemek[/link], ha egy kis önkínzásra, a [link=http://kritikustomeg.org/top_filmek/?tipus=legrosszabb]legrosszabb filmek[/link], ha pedig a "lemaradásodat" akarod behozni, a [link=http://kritikustomeg.org/top_filmek/?tipus=legnezettebb]legnépszerűbb filmek[/link]. És végül ott vannak még a [link=http://kritikustomeg.org/felhasznaloi_toplistak/]felhasználói toplisták[/link], köztük félkövérrel kiemelve, ahol nem csak egy listát találsz, hanem magyarázatot is hozzá.

Ha nemrég láttál valami nagyon jót, vagy van egy kedvenced, és hasonló filmeket keresel, nézd meg a film adatlapján jobbra az Ajánlott filmeket.

És végül, de nem utolsósorban, kezdj el megismerkedni a közösséggel. Hiszen a legjobb filmajánlatokat akkor kaphatod, ha megtalálod azokat, akikkel hasonló az ízlésetek. Ebben nagy segítség, hogy ha elég sok filmet leosztályzol, a [link=http://kritikustomeg.org/hasonlok/]Hasonlók menüben[/link] listában láthatod ezeket az embereket. Addig is érdemes kedvenc filmjeid szavazatait és kommentjeit átfutnod: biztosan fogsz szimpatikus embereket találni.

Ha valaki felkelti az érdeklődésed, kattints a nevére, hogy lásd az adatlapját. Itt nem csak a hasonlóságotok látszódik műfajokra bontva (ha elég filmet leosztályoztál), de az illető bemutatkozása is, beleértve a kedvenc rendezőket, színészeket, műfajokat, országokat, korszakokat. (Ezeket saját magadnál is megadhatod, ha fent a saját nevedre kattintasz, és ott a [link=http://kritikustomeg.org/szerk_profil/]Profil szerkesztésére[/link].) Ha pedig átnézed a filmjeit, kommentjeit, kívánságait (ahol ugyanúgy tudsz szűrni mindenféle szempontok szerint, mint a böngészőben), végképp meggyőződhetsz arról, hogy érdemes-e az illetőt követned.

Aki megtetszett, azt vedd fel a kedvenceid közé. Ez nem csak azért jó, mert a [link=http://kritikustomeg.org/kedvencek/]Kedvenceid menüben[/link] láthatod a legutóbbi szavazatait és kommentjeit, de azért is, mert a filmek adatlapján kiemelve láthatod az osztályzatait, és az összes filmes listában az átlag mellett a kedvenceid átlaga is megjelenik (és rendezheted a listákat eszerint is).

Jó szórakozást a Kritikus Tömeghez, és még inkább a jobbnál jobb filmekhez, amik várnak rád!


a szerk
'''


PASSWORD_RESET_EMAIL_SUBJECT = u'[Kritikus Tömeg] jelszó'
PASSWORD_RESET_EMAIL_BODY = u'''<p>A Kritikus Tömegen jelezted, hogy nem emlékszel a jelszavadra. Erre a linkre kattintva megadhatsz egy új jelszót:</p>
<p><a href="{reset_password_url}" style="text-decoration: none; color: rgb(146,23,23)">{reset_password_url}</a></p>'''


PM_EMAIL_SUBJECT = u'[Kritikus Tömeg] {sent_by} üzenetet írt neked'
PM_EMAIL_BODY = u'''Kedves {username}!

{sent_by} üzenetet írt neked a Kritikus Tömegen:
---
{content}
---


Üdvözlettel,
a KT szerkesztősége
http://kritikustomeg.org/
'''


LONG_YEARS = {
    1910: u"1920 előtt",
    1920: u"'20-as évek",
    1930: u"'30-as évek",
    1940: u"'40-es évek",
    1950: u"'50-es évek",
    1960: u"'60-as évek",
    1970: u"'70-es évek",
    1980: u"'80-as évek",
    1990: u"'90-es évek",
    2000: u"2000-es évek",
    2010: u"2010-es évek",
}


VAPITI_NOMINEE_CATEGORIES = {
    'G': u'Arany Vapiti a legjobb filmnek jelölés',
    'F': u'Ezüst Vapiti a legjobb színésznőnek jelölés',
    'M': u'Ezüst Vapiti a legjobb színésznek jelölés',
}
VAPITI_WINNER_CATEGORIES = {
    'G': u'Arany Vapiti a legjobb filmnek',
    'F': u'Ezüst Vapiti a legjobb színésznőnek',
    'M': u'Ezüst Vapiti a legjobb színésznek',
}


BAN_TYPES = {
    'ban': u'végleges kitiltás',
    'unban': u'kitiltás visszavonása',
    'warning': u'hivatalos figyelmeztetés',
    'temp_ban_1d': u'1 napos kitiltás',
    'temp_ban_3d': u'3 napos kitiltás',
    'temp_ban_7d': u'7 napos kitiltás',
}


WARNING_PM_BODY = u'''Kedves {username}!

Ez egy hivatalos figyelmeztetés a szerkesztőségtől. Ha továbbra sem tartod be a [link=http://kritikustomeg.org/szabalyzat/]szabályzatot[/link], a következő retorzió egy ideiglenes kitiltás lesz. Hadd ne kelljen idáig eljutni.


a szerk
'''
