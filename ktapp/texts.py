# -*- coding: utf-8 -*-

WELCOME_EMAIL_SUBJECT = u'[Kritikus Tömeg] regisztráció'
WELCOME_EMAIL_BODY = u'''Kedves {username}!

Üdvözlünk a Kritikus Tömegen. Ahhoz, hogy hosszú távon is használni tudd az oldalt, szükséged van egy jelszóra, amivel be tudsz lépni. A jelszó megadásához kattints erre a linkre:
{verification_url}


Üdvözlettel,
a KT szerkesztősége
http://kritikustomeg.org/
'''


WELCOME_PM_BODY = u'''Kedves {username}!

Üdvözlünk a Kritikus Tömegen. Ahhoz, hogy hosszú távon is használni tudd az oldalt, szükséged van egy jelszóra, amivel be tudsz lépni. A jelszó megadásához küldtünk egy linket emailben a címedre ({email}). Ha nem találod, nézz be a spam mappába is, hátha oda került véletlenül. Ha sehogy sem találod, [link={reset_password_url}]kérj egy újat[/link].


a szerk
'''


PASSWORD_RESET_EMAIL_SUBJECT = u'[Kritikus Tömeg] jelszó'
PASSWORD_RESET_EMAIL_BODY = u'''Kedves {username}!

A Kritikus Tömegen jelezted, hogy nem emlékszel a jelszavadra. Erre a linkre kattintva megadhatsz egy új jelszót:
{reset_password_url}


Üdvözlettel,
a KT szerkesztősége
http://kritikustomeg.org/
'''


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
