Design of morse recognizer
==========================

Various ideas were tried in the programs *test.py* through *test[N].py*.

*test4.py* was the first moderately successful incarnation and forms the
basis of *morse.py*.

Design
======

Raw microphone data is passed through various layers before being turned into
English characters.

Layer 0
-------

The function *get_sample()* reads raw data from the microphone.  It does this
in 32 byte chunks of 16 bit integers.  Each array of integers is averaged and
the average value compared to a threshold value.  If the average value is over
the threshold then we have a sound.

The code in *get_sample()* returns a count value.  This value is negative if
the code heard no sound.  If no sound is heard then *get_sample()* returns a
negative count that is limited at a fixed value.  That is, the function doesn't
loop forever if it hears nothing.  We do this as higher-level code needs to know
how long periods of silence are, so we can distinguish between inter-character
and inter-word silences.

If *get_sample()* **does** hear a sound it starts counting how many contiguous
samples of sound it hears.  There is a 'hang' count used to ignore small breaks
in the sound.  The positive count returned is the count of the length of the
sound.  Any preceding silence count is ignored.

To sum up, *get_sample()* returns:

- a negative count meaning nothing was heard
- a positive count meaning a sound was heard for the *count* number of samples

Layer 1
-------

The code in *read_morse()* repeatedly calls *get_sample()* to get positive or
negative counts.

If the read count is negative we have a silence period.  Silence periods are
always a fixed small number.  The code keeps two counts of consecutive silence
periods.  If the count exceeds the value *CHAR_SPACE* the code decides that a
character has finished and any accumulated morse characters are decoded and
emitted.  If silence continues and the count exceeds the value *WORD_SPACE*
then the code assumes a code word has terminated and a delimiting space is
emitted.

If the read count is positive then layer 0 has heard a sound.  The length of
the sound (the count value) is compared with the threshold value *DOT_DASH*
to decide if we have a dot or dash.  Once the sound is classified into a dot
or dash we add the dot/dash character to a code accumulator string.  We also
look at the *length* of the dot or dash and dynamically average various internal
values to accomodate varying code characteristics.

The dynamic internal values are:

+-------------+--------------------------------------------------------------+
| Variable    | Usage                                                        |
+=============+==============================================================+
| DOT_LENGTH  | The length of a 'dot' sound                                  |
+-------------+--------------------------------------------------------------+
| DASH_LENGTH | The length of a 'dash' sound                                 |
+-------------+--------------------------------------------------------------+
| DOT_DASH    | Threshold value to distinguish between a 'dot' and 'dash'    |
+-------------+--------------------------------------------------------------+

Decoding Morse
--------------

Layer 1 accumulates morse dots and dashes into a string.  When the code decides
it has received a character, this string is decoded in a dictionary that returns
the appropriate English character.

If the morse character is *not* recognized the decode mechanism returns a string
indicating the unrecognized character.  For example, an attempt to recognize
three morse characters with the second character not recognized (7 sounds) would
result in this display:

::

    A¿<....-..>Z

Dynamic Parameter Caching
-------------------------

When *morse.py* starts executing it attempts to read cached values for the
dynamic decoding parameters from a file.  If you don't want this to happen
either delete the save file before executing *morse.py* or use the **-x**
option.

*morse.py* also always saves the dynamic parameters when shutting down.

Further Work
============

*morse.py* isn't perfect. We need to do work on:

- Recognizing faster morse
- Handling noise better
