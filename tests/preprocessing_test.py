import unittest

from auxiliary.preprocessing import Preprocessing
import os

class CaseInstance(object):

    def __init__(self, text, title, body_index, formatted_title, speaks_offsets):
        self.text = text
        self.body_index = body_index
        self.title = title
        self.formatted_title = formatted_title
        self.speaks_offsets = speaks_offsets

class PreprocessingTest(unittest.TestCase):

    case_instances = [
        CaseInstance(text='''	JORGE
	JORGE
ANA	Jorge I (Hanover, 28 de maio de 1660 Osnabruque, 11 de junho
de 1727) foi o Rei da GraBretanha e Irlanda de 1 de agosto de 1714 
at sua morte, e tambem governante do Ducado e Eleitorado de II.''',
        body_index=14,
        title='JORGE',
        formatted_title='Jorge',
        speaks_offsets={0:'ANA'}),

        CaseInstance(text='''	THE TAMING OF THE SHREW


    DRAMATIS PERSONAE


    A Lord.		|
            |
CHRISTOPHER SLY	a tinker. (SLY:)		|  Persons in
            |  the Induction.
    Hostess, Page, Players,	|
    Huntsmen, and Servants.	|
    (Hostess:)
    (Page:)
    (A Player:)
    (First Huntsman:)
    (Second Huntsman:)
    (Messenger:)
    (First Servant:)
    (Second Servant:)
    (Third Servant:)


BAPTISTA	a rich gentleman of Padua.

VINCENTIO	an old gentleman of Pisa.

LUCENTIO	son to Vincentio, in love with Bianca.

PETRUCHIO	a gentleman of Verona, a suitor to
    Katharina.


GREMIO	|
    | suitors to Bianca.
HORTENSIO	|


TRANIO	|
    | servants to Lucentio.
BIONDELLO	|


GRUMIO	|
    |
CURTIS	|
    |
NATHANIEL	|
    |
NICHOLAS	|  servants to Petruchio.
    |
JOSEPH	|
    |
PHILIP	|
    |
PETER	|

    A Pedant.


KATHARINA the shrew,	|
        | daughters to Baptista.
BIANCA		|

    Widow.

    Tailor, Haberdasher, and Servants attending
    on Baptista and Petruchio.
    (Tailor:)
    (Haberdasher:)
    (First Servant:)


SCENE	Padua, and Petruchio's country house.




    THE TAMING OF THE SHREW

    INDUCTION



SCENE I	Before an alehouse on a heath.


    [Enter Hostess and SLY]

SLY	I'll pheeze you, in faith.

Hostess	A pair of stocks, you rogue!

SLY	Ye are a baggage: the Slys are no rogues; look in
    the chronicles; we came in with Richard Conqueror.
    Therefore paucas pallabris; let the world slide: sessa!''',
        body_index=1107,
        title='THE TAMING OF THE SHREW',
        formatted_title='The Taming Of The Shrew',
        speaks_offsets={88: 'SLY',120: 'Hostess', 158: 'SLY'}),

        CaseInstance(text='''	HAMLET


    DRAMATIS PERSONAE


CLAUDIUS	king of Denmark. (KING CLAUDIUS:)

HAMLET	son to the late, and nephew to the present king.

POLONIUS	lord chamberlain. (LORD POLONIUS:)

HORATIO	friend to Hamlet.

LAERTES	son to Polonius.

LUCIANUS	nephew to the king.


VOLTIMAND	|
    |
CORNELIUS	|
    |
ROSENCRANTZ	|  courtiers.
    |
GUILDENSTERN	|
    |
OSRIC	|


    A Gentleman, (Gentlemen:)

    A Priest. (First Priest:)


MARCELLUS	|
    |  officers.
BERNARDO	|


FRANCISCO	a soldier.

REYNALDO	servant to Polonius.
    Players.
    (First Player:)
    (Player King:)
    (Player Queen:)

    Two Clowns, grave-diggers.
    (First Clown:)
    (Second Clown:)

HAMLET	Hi, I am Hamlet!
FORTINBRAS	prince of Norway. (PRINCE FORTINBRAS:)

    A Captain.

    English Ambassadors. (First Ambassador:)

GERTRUDE	queen of Denmark, and mother to Hamlet.
    (QUEEN GERTRUDE:)

OPHELIA	daughter to Polonius.

    Lords, Ladies, Officers, Soldiers, Sailors, Messengers,
    and other Attendants. (Lord:)
    (First Sailor:)
    (Messenger:)

    Ghost of Hamlet's Father. (Ghost:)



SCENE	Denmark.




    HAMLET


ACT I



SCENE I	Elsinore. A platform before the castle.


    [FRANCISCO at his post. Enter to him BERNARDO]

BERNARDO	Who's there?

FRANCISCO	Nay, answer me: stand, and unfold yourself.

BERNARDO	Long live the king!

FRANCISCO	Bernardo?

BERNARDO	He.

FRANCISCO	You come most carefully upon your hour.

BERNARDO	'Tis now struck twelve; get thee to bed, Francisco.

FRANCISCO	For this relief much thanks: 'tis bitter cold,
    And I am sick at heart.

BERNARDO	Have you had quiet guard?''', 
        body_index=1108,
        title='HAMLET',
        formatted_title='Hamlet',
        speaks_offsets={113: 'BERNARDO', 136: 'FRANCISCO', 191: 'BERNARDO',
                221: 'FRANCISCO', 242: 'BERNARDO', 256: 'FRANCISCO', 307:
                'BERNARDO', 369: 'FRANCISCO', 455: 'BERNARDO'}),
        
        CaseInstance(text='''	A LOVER'S COMPLAINT



FROM off a hill whose concave womb reworded
A plaintful story from a sistering vale,
My spirits to attend this double voice accorded,
And down I laid to list the sad-tuned tale;
Ere long espied a fickle maid full pale,
Tearing of papers, breaking rings a-twain,
Storming her world with sorrow's wind and rain.''', 
        body_index=21,
        title='A LOVER\'S COMPLAINT',
        formatted_title='A Lover\'s Complaint',
        speaks_offsets={})]

    def test_find_title(self):
        for case_instance in self.case_instances:
            title = Preprocessing.find_title(case_instance.text)
            self.assertEquals(title, case_instance.title)

    def test_titlecase(self):
        for case_instance in self.case_instances:
            formatted_title = Preprocessing.titlecase(case_instance.title)
            self.assertEquals(formatted_title, case_instance.formatted_title)

    def test_get_speaks_offsets(self):
        for case_instance in self.case_instances:
            speaks_offsets = Preprocessing.get_speaks_offsets(case_instance.
                text[case_instance.body_index:])
            self.assertEquals(speaks_offsets, case_instance.speaks_offsets)

if __name__ == '__main__':
    unittest.main()



