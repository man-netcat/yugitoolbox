from unittest import TestCase, main

from src.deck import Deck
from src.enums import *
from src.omegadb import OmegaDB


class TestDB(TestCase):
    db = OmegaDB(update="skip")
    maxDiff = None

    def test_archetype(self):
        a = TestDB.db.get_archetype_by_id(351)
        self.assertEqual(a.name, "War Rock")

    def test_effect_monster(self):
        # War Rock Meteoragon
        c = TestDB.db.get_card_by_id(10497636)
        self.assertEqual(c.id, 10497636)
        self.assertEqual(c.koid, 16278)
        self.assertEqual(c.name, "War Rock Meteoragon")

        self.assertEqual(c.race, Race.Warrior)
        c.race = Race.Psychic
        self.assertEqual(c.race, Race.Psychic)

        self.assertEqual(c.attribute, Attribute.EARTH)
        c.attribute = Attribute.DARK
        self.assertEqual(c.attribute, Attribute.DARK)

        self.assertEqual(c._atkdata, 2600)
        c._atkdata = 2800
        self.assertEqual(c._atkdata, 2800)

        self.assertEqual(c.def_, 2600)
        c.def_ = 2700
        self.assertEqual(c.def_, 2700)

        self.assertEqual(c.level, 7)
        c.level = 8
        self.assertEqual(c.level, 8)

        self.assertTrue(c.has_any_type([Type.Monster, Type.Effect]))
        self.assertTrue(c.has_type(Type.Effect))
        c.type = [Type.Normal]
        self.assertTrue(c.has_type(Type.Normal))
        c.type = Type.Normal
        self.assertTrue(c.has_all_types([Type.Normal]))

        testarch = TestDB.db.get_archetype_by_name("War Rock")
        self.assertEqual(testarch.name, "War Rock")
        testset = TestDB.db.get_set_by_name("Lightning Overdrive")
        self.assertEqual(testset.name, "Lightning Overdrive")
        # self.assertTrue(c.id in testarch.members)
        self.assertTrue(c.id in testset.contents)
        self.assertTrue(testarch.id in c.archetypes)
        # self.assertIsNotNone(c.script)

    def test_pendulum_monster(self):
        # Odd-Eyes Pendulum Dragon
        c = TestDB.db.get_card_by_id(16178681)
        self.assertTrue(c.has_type(Type.Pendulum))

        # Test level and scale
        self.assertEqual(c.level, 7)
        self.assertEqual(c.scale, 4)
        c.level = 8
        self.assertEqual(c.level, 8)
        self.assertEqual(c.scale, 4)
        c.scale = 3
        self.assertEqual(c.level, 8)
        self.assertEqual(c.scale, 3)

    def test_link_monster(self):
        # Decode Talker
        c = TestDB.db.get_card_by_id(1861629)
        self.assertTrue(c.has_type(Type.Link))

        # Test def
        self.assertEqual(c.def_, 0)
        c.def_ = 3
        self.assertEqual(c.def_, 0)

        # Test linkrating
        self.assertEqual(c.level, 3)
        c.level = 4
        self.assertEqual(c.level, 4)

        # Test linkmarkers
        self.assertTrue(
            c.has_all_linkmarkers(
                [
                    LinkMarker.Top,
                    LinkMarker.BottomLeft,
                    LinkMarker.BottomRight,
                ]
            )
        )
        c.append_linkmarker(LinkMarker.Bottom)
        self.assertTrue(
            c.has_all_linkmarkers(
                [
                    LinkMarker.Top,
                    LinkMarker.BottomLeft,
                    LinkMarker.BottomRight,
                    LinkMarker.Bottom,
                ]
            )
        )
        c.linkmarkers = LinkMarker.Top | LinkMarker.Bottom
        self.assertCountEqual(c.linkmarkers, [LinkMarker.Top, LinkMarker.Bottom])
        c.linkmarkers = [LinkMarker.Top, LinkMarker.Bottom]
        self.assertCountEqual(c.linkmarkers, [LinkMarker.Top, LinkMarker.Bottom])

    def test_deck(self):
        omegacode = "M+ffLv2SpUJvAQMMO9oKsYDwLo1vjDB8NmIdy6HbV5hcbn5jgeHPrZdYYXiD8j0GGF4++wujxvadTDAcWZ3MMjFpHysM2y0pZBRbdIsJhFukVFlg+IygBxzf4drLBMNhunysOxo5mSUXdTGaH7Vn8Jq4lAmExeuPsYBwYLYx8wGp/ywgvFsrCY4/HX7HZLExmQWGnffdZYDh/LL3cHz8oi4zDJs8PsQIwyC7AQ=="
        testdeck = Deck.from_omegacode(TestDB.db, omegacode)
        self.assertEqual(omegacode, testdeck.omegacode)
        ydke_code = "ydke://EUKKAwrmpwEK5qcBR5uPAEebjwBHm48AvadvAfx5vAKzoLECTkEDAE5BAwBOQQMAfjUBBUwyuADDhdcAnNXGA/ZJ0ACmm/QBPqRxAT6kcQE+pHEBVhgUAVYYFAFWGBQBZOgnA2ToJwNk6CcDIkiZACJImQAiSJkAdgljAnYJYwJ2CWMCVOZcAVTmXAF9e0AChKFCAYShQgGEoUIBPO4FAzzuBQM=!y7sdAIoTdQOKE3UDwLXNA9EgZgUNUFsFtWJvAqRbfAOkW3wDlk8AAoVAsQKA9rsBlI9dAQdR1QE5ySIF!URCDA1EQgwNREIMDI9adAiPWnQJvdu8Ab3bvANcanwHXGp8B1xqfASaQQgMmkEIDJpBCA0O+3QBDvt0A!"
        testdeck = Deck.from_ydke(TestDB.db, ydke_code)
        self.assertEqual(ydke_code, testdeck.ydke)

    def test_db_search(self):
        # Test if Odd-Eyes Wing Dragon and Odd-Eyes Venom Dragon are in the list of extra deck pendulums.
        wingdragon = TestDB.db.get_card_by_id(58074177)
        venomdragon = TestDB.db.get_card_by_id(45014450)
        extradeckpends = TestDB.db.get_cards_by_value(
            "type", "synchro,pendulum|fusion,pendulum"
        )
        synchropends = TestDB.db.get_cards_by_value(
            "type", [Type.Synchro, Type.Pendulum]
        )
        synchro = TestDB.db.get_cards_by_value("type", Type.Synchro)
        self.assertIn(wingdragon, extradeckpends)
        self.assertIn(wingdragon, synchropends)
        self.assertIn(wingdragon, synchro)
        self.assertIn(venomdragon, extradeckpends)

        # Link pendulums do not (yet) exist.
        linkpends = TestDB.db.get_cards_by_value("type", "link,pendulum")
        self.assertEqual(linkpends, [])

        hexetrude = TestDB.db.get_card_by_id(46294982)
        goldencastle = TestDB.db.get_cards_by_value(
            "mentions", "golden castle of stromberg"
        )
        # Test card mentions
        self.assertIn(hexetrude, goldencastle)

        oddeyes = self.db.get_archetype_by_name("Odd-Eyes")
        self.assertIn(wingdragon.id, oddeyes.members)

        notdragons = self.db.get_cards_by_value("race", "~dragon")
        self.assertNotIn(wingdragon, notdragons)

        embodiment = self.db.get_card_by_id(28649820)
        trapmonsters = self.db.get_cards_by_value("type", "trapmonster")
        self.assertIn(embodiment, trapmonsters)

        meteoragon = TestDB.db.get_card_by_id(10497636)
        atkequdef = self.db.get_cards_by_value("atk", "def")
        self.assertIn(meteoragon, atkequdef)
        


if __name__ == "__main__":
    main()
