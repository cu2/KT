# -*- coding: utf-8 -*-

WELCOME_EMAIL_SUBJECT = u'Kritikus Tömeg regisztráció'
WELCOME_EMAIL_BODY = u'''Kedves {username}!

Üdvözlünk a Kritikus Tömegen. Ahhoz, hogy hosszú távon is használni tudd az oldalt, szükséged van egy jelszóra, amivel be tudsz lépni. A jelszó megadásához kattints erre a linkre:
{verification_url}


a szerk
'''

WELCOME_PM_BODY = u'''Kedves {username}!

Üdvözlünk a Kritikus Tömegen. Ahhoz, hogy hosszú távon is használni tudd az oldalt, szükséged van egy jelszóra, amivel be tudsz lépni. A jelszó megadásához küldtünk egy linket emailben a címedre ({email}). Ha nem találod, nézz be a spam mappába is, hátha oda került véletlenül. Ha sehogy sem találod, [link={reset_password_url}]kérj egy újat[/link].


a szerk
'''

PASSWORD_RESET_EMAIL_SUBJECT = u'Kritikus Tömeg jelszó'
PASSWORD_RESET_EMAIL_BODY = u'''Kedves {username}!

A Kritikus Tömegen jelezted, hogy nem emlékszel a jelszavadra. Erre a linkre kattintva megadhatsz egy új jelszót:
{reset_password_url}


a szerk
'''
