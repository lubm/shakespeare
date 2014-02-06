import unittest

from auxiliary.preprocessing import Preprocessing
import os

class CaseInstance(object):

    def __init__(self, test_input, expected_output):
        self.test_input = test_input
        self.expected_output = expected_output

class PreprocessingTest(unittest.TestCase):

    case_instances = [CaseInstance('''	JORGE
        	JORGE
        ANA Jorge I (Hanover, 28 de maio de 1660 Osnabruque, 11 de junho
        de 1727) foi o Rei da GraBretanha e Irlanda de 1 de agosto de 1714 
        at sua morte, e tambem governante do Ducado e Eleitorado de II.''',
        'JORGE'),
        CaseInstance('''	THE TAMING OF THE SHREW


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
        'THE TAMING OF THE SHREW'),
        CaseInstance('''	HAMLET


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

        BERNARDO	Have you had quiet guard?''', 'HAMLET'),
        CaseInstance('''  	A LOVER'S COMPLAINT



        FROM off a hill whose concave womb reworded
        A plaintful story from a sistering vale,
        My spirits to attend this double voice accorded,
        And down I laid to list the sad-tuned tale;
        Ere long espied a fickle maid full pale,
        Tearing of papers, breaking rings a-twain,
        Storming her world with sorrow's wind and rain.''', 
        '''A LOVER'S COMPLAINT''')]

    def test_find_title(self):
        for case_instance in self.case_instances:
            title = Preprocessing.find_title(case_instance.test_input)
            self.assertEqual(title, case_instance.expected_output)


if __name__ == '__main__':
    unittest.main()



