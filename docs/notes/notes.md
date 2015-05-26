# Notes


## UX


### UX advice from Juli

- competition analysis:
    - check out features
    - and reasons why people might use them
    - what's my "offer", what do users get from KT vs other alternatives?

- interviews:
    - ask in details about last 2 weeks
    - what did they watch?
    - how and why did they choose them?
    - ask a continuous story, not just yes/no or numeric questions

- stories, use cases, personas:
    - story: bunch of functions, smaller use cases in a flow
    - use cases: not just functionality, but emotions (e.g. I'm so thrilled to find this film from my childhood)
    - persona: kind of a role, e.g. non-KT-user FB friend of a KT-user (sees his KT shares)

- survey:
    - have potential use cases before the survey
    - ask about them specifically, and not just without any preconceptions and frames
    - leave a free text area as well (for getting special cases)

- UX + design is an iteration in an ideal case: a good designer gives feedbacks about the wireframe

- reading:
    - iterate it with work
    - when you work on a topic, read about it; then go on
    - Pepe sent some notes on books

- old users:
    - let them complain about changes, it helps them to bear these
    - give them help when changing things, e.g. tooltips and messages that show them around on the new site


### UX advice from Juli (round 2)

- follow your instincts, not these advice

- info design
    - put the interesting stuff in the face of the user
    - otherwise she'll leave
    - vs too many info that might not by interesting at first (e.g. all the ratings on the main page of films)

- personas:
    - vision/mission is FIRST
        - help everyone find their next film?
    - have a few scales:
        - social/antisocial
        - knowledgeable/not
        - open/geek
    - try to balance personas on all scales
        - 2 heavy users
        - 1 mid
        - 1 light: comes to KT to find her the next film she watches
    - if it's unbalanced, ppl from the other end won't find the site welcoming
    - handle these as an orthogonal dimension (so each persona has all phases):
        - unregistered users
        - users who already signed up but have little activity so far
        - users with lot of ratings and comments
    - concentrate on behaviour

- data:
    - check current user groups:
        - registered 3, 2, 1 years ago, now
        - very active, inactive
        - what features do they use? what content are they interested in?

- interviews and surveys
    - survey: 10 minutes max
    - interview: 45 minutes max
    - do more rounds, if necessary
    - Likert survey: don't use too strong statements
    - what comes out of a question? don't ask if nothing

- vision VS strategy VS MVP:
    - concentrate on the MVP
    - extend later in as small meaningful and testable chunks as possible
        - e.g. tv series extension: just add Game of Thrones in some format and let users rate and comment and observe


### [About Face - Interviews and personas](about-face-interviews-and-personas.md)



## General

### [Postmortem of a Venture-backed Startup](postmortem-of-a-venture-backed-startup.md)



## Technology

### Mobile

http://www.smashingmagazine.com/2013/11/28/lessons-from-an-app-graveyard/
"A recent study (PDF, 2 MB) by Compuware found that smartphone users prefer mobile apps to mobile websites, but other research shows organizational strategy shifting away from native mobile apps towards Web experiences. If your content and functionality can be better served to users through a responsive website or Web app, then you have no real need for a native app. While native apps can easily use a device’s capabilities, a few features, such as GPS, can be used by websites, too."

- how to wrap a mobile web page into an Android app?
- how to wrap a mobile web page into an iPhone app? http://fluidapp.com/
- how to create a mobile web page that is really smooth and native-like?

Mobile first approach:

- it's not about users on the move, only limited screen size
- have all the info that the web version has
- only tap and scroll more to get them
- it helps prioritizing and choosing MVP features
- load fast first, then get the rest via ajax
