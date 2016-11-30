Morse Trainer
=============

This is an attempt at a "morse trainer" program.  It will allow the user to
practice sending and receiving morse.  Besides this program you need some
method of making audio morse sounds, such as a morse key and code practice
oscillator.

Requirements
------------

* Teach sending and receiving morse
    * SEND listens to morse sounds and displays the decoded morse
    * RECEIVE sounds morse and listener types in the received characters
* Uses Kock and selectable characters approaches
* User can vary char and word speeds independently
* Program keeps learning statistics for feedback
* Caters to more than one user (different stats per user)

Implementation
--------------

* python3
* PyQt
* use sqlite to state statistics/history

Design
------

SEND

The program will show user groups to send, highlighting the current expected
group.  As the user sends morse, the decoded characters appear underneath, with
incorrect characters highlighted.

Operations allowed:

* START
* STOP
* PAUSE
* CLEAR (?)

Parameters that can be changed:

* Characters used

Statistics kept:

* % correct, in current test and globally
* relative error rates by character

RECEIVE

The program will sound morse and accept user keying in the character.  The
display will show the received character and also the sent character, with
highlighting if incorrect.

Operations allowed:

* START
* STOP
* PAUSE
* CLEAR

Parameters that can be changed:

* Characters used (just A-Z, NUMERALS, etc)
* char speed
* word speed
* random or "wrong skew"

The characters used could also follow the Koch method, starting with two
characters at the desired char speed (usually K and M).  When the error
rate falls below a preset level, add one more character.  Continue until
all selected characters are OK.

Statistics kept:

* % correct, in current test and globally
* relative error rates by character

