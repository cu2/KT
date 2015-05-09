# UX plan


## Personas and use cases

Purpose: to answer these questions:

- who and how uses/could use KT?
- what values KT provides for and what emotions it generates in users?

Method: create personas and use cases

- persona should be a human, not just a set of properties
- use case should be a story/part of a story, not just a set of features

The more preconceptions you have for the interviews and/or survey, the more info you'll get. But the more you'll get, the more and better preconceptions you'll get. So iterate.

- First version of personas and use cases
    - personas: had none
    - [use cases](use_cases_v1.md)
- Interviews (see [here](interviews/))
    - what to ask? see [Questions for exploring personas and use cases](persona_interview_questions.md)
    - Skype? Hangouts? live? email?
        - email: it's easy to do, but hard to interpret (you can't ask back a lot of times) and control (the subject can easily misunderstand what you asked, and you can't correct her on the spot)
        - live: it can be scary and frustrating (if you have social skill issues), but you can get more out of it, especially if you're able to jump between the questions
    - notes? record it?
        - probably it's easier to let the conversation flow, if you don't have to take notes, just record it (never tried)
    - who to ask?
        - KT users
            - lot of comments and votes
            - lot of votes, few comments
            - lot of comments, few votes
            - just listens
            - ex active user
        - new users
            - friends, family, colleagues
            - relevant FB groups
- Second version of personas and use cases
    - [personas](personas_v2.md)
    - [use cases](use_cases_v2.md)
    - [persona matrix](https://docs.google.com/spreadsheets/d/1MQLYhMIrHgpRXV3eS9elp-Ncf2NSJ1lLInfGBwpTNyc/edit?usp=sharing)
- Second round of interviews
    - [questions](persona_interview_questions_v2.md)

Realize we need a vision and a mission!


## Vision and mission

First idea: be the platform for films

But what the hack is a platform?

YouTube is the platform for music videos:

- lot of content ("everything")
- actual content: not just database or meta info, but actual streaming digital content
- "low hanging" recommendation:
    - for passive/unconscious consumers
    - based on popularity
    - optimized ratio of similar and new content to keep the user engaged as long as possible
    - "mind reading" TV, post median viewer TV
- vision: "all boredom amused" ([Arthur Jensen in Network](http://www.imdb.com/title/tt0074958/quotes?item=qt0447849))

Netflix and Amazon Prime are the same for films.

This is very different from what KT *is* and very far from what KT can provide *ever*.

On the film consciousness scale there are different people:

- unconscious (not in general, just in the film domain)
    - for them films are just a means of entertainment
    - they want entertainment, if it's films then be it, if not then not
    - so they need actual digital content and subconscious recommendation (i.e. platforms for digital content)
- film lovers
    - they differentiate films from other means of entertainment
    - and consider films not just a means of entertainment
    - they make more or less conscious choices when it comes to films
    - they try to get help with these choices from friends, reviews and blogs, but it takes too much time and/or it's not enough
- film fans (filmaholics)
    - film is their hobby and/or life
    - they put serious amount of time, effort, sometimes even money into this
    - over time they collect a lot of knowledge
    - they read news, reviews, blogs and forums, sometimes even contribute to them

Currently KT is (or strives to be) the Mecca of film fans (in Hungary), so a possible vision is to become the Mecca of film lovers (in the world).

- Vision
    - optimal desired future state
    - **Be the Mecca of film lovers**

- Mission
    - *What* we do + *Who* we do it for + *How* we do it
    - **Help film lovers decide what to watch**
    - Why?
        - there are two things every film lover does:
            - choose films to watch
            - watch films: download, stream, cinema; we can't help that (cf platforms)
        - everything else (e.g. talk about films, read about films) is optional: some film lovers do it, others don't


## Personas and use cases (cont'd)

- Dimensions
    - Knowledge
        - layman: knows nothing/not much about films
        - expert: knows a lot about films
    - Range of taste
        - wide (omnivorous): likes films in a lot of genres, from a lot of periods, by a lot of directors
        - narrow (picky): only likes films in specific genres, from specific periods, by specific directors
    - Sociability
        - social: interested in people and films
        - antisocial: interested only in films

The first two dimensions are not independent: you cannot really be picky unless you possess enough knowledge. So if we only consider binary distinctions, we get 6 possible personas:

- social layman
- antisocial layman
- social omnivorous expert
- antisocial omnivorous expert
- social picky expert
- antisocial picky expert

Things to consider:

- number of personas
    - too many personas might lead to loss of focus
- balance
    - film lovers are layman(ish), film fans are experts
    - too many expert personas might result in a film fan oriented KT (vs vision)
    - maybe add a persona to the middle of the knowledge spectrum? (serious film lover)
- actual vs possible personas
    - does it make sense to have social and antisocial version of each knowledge/range-of-taste combo?
- user journey (for each persona):
    - unregistered: have no idea what the site is about
    - newly registered: just started rating films (and thus generating real user profile)
    - long-time registered: have lot of experience with KT, ratings, comments, user profile
- concentrate on behaviour

- Data analysis
    - current KT users
    - newly registered vs registered a long time ago
    - active vs inactive
    - what features do they use?
    - what content are they interested in?
    - knowledge based on number of votes
    - range of taste based on votes per genre, period, director
    - sociability based on number of comments

- Survey
    - 10 minutes max
    - only questions that yield answers we can learn from
    - only questions that yield answers that help building a better KT
    - predefined choices where possible: [Likert scale](http://en.wikipedia.org/wiki/Likert_scale)
    - for KT users
        - who to ask?
            - select a sample of users (10-20%)
        - what to ask?
    - for new users
        - who to ask?
            - friends, family, colleagues
            - relevant FB groups
        - what to ask?

- Third version of personas and use cases
    - personas
    - use cases


## Core functions

- what functions should KT provide?
    - MVP:
        - rating
        - comment
        - content:
            - films
            - plots
            - roles, actors
            - keywords: genre, country, mood?, style?, other
            - pictures
            - trailers
        - content editing:
            - by admin
            - by crowdsourcing
    - other:
        - content:
            - awards
            - reviews
            - quotes
            - trivia
            - links
        - cinema program


## Interaction design

- pages and functions
- navigation
- usability tests for current KT and competitors?


## Wireframes


## Usability testing

- typical tasks
    - sign up, login, logout, change password
    - look at home page and tell what the site is about
    - search for your favorite film
    - other: check use cases
- screen+audio recording
- length?
- compensation?
- where?
- 3 participants (users) per round
- observers:
    - more than 1
    - write down top 3 problems for each participant
