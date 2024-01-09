from unittest import TestCase, main

from yugitoolbox import *


class TestDB(TestCase):
    sqlite_connection_string = f"sqlite:///db/omega/omega.db"
    db = YugiDB(sqlite_connection_string)
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

        self.assertEqual(c.atk, 2600)
        c.atk = 2800
        self.assertEqual(c.atk, 2800)

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
        self.assertTrue(c.id in testarch.members)
        self.assertTrue(c.id in testset.contents)
        self.assertTrue(testarch.id in c.archetypes)
        self.assertIsNotNone(c.script)

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

    # def test_deck(self):
    #     omegacode = "M+ffLv2SpUJvAQMMO9oKsYDwLo1vjDB8NmIdy6HbV5hcbn5jgeHPrZdYYXiD8j0GGF4++wujxvadTDAcWZ3MMjFpHysM2y0pZBRbdIsJhFukVFlg+IygBxzf4drLBMNhunysOxo5mSUXdTGaH7Vn8Jq4lAmExeuPsYBwYLYx8wGp/ywgvFsrCY4/HX7HZLExmQWGnffdZYDh/LL3cHz8oi4zDJs8PsQIwyC7AQ=="
    #     testdeck = Deck.from_omegacode(TestDB.db, omegacode)
    #     self.assertEqual(omegacode, testdeck.omegacode)
    #     ydke_code = "ydke://EUKKAwrmpwEK5qcBR5uPAEebjwBHm48AvadvAfx5vAKzoLECTkEDAE5BAwBOQQMAfjUBBUwyuADDhdcAnNXGA/ZJ0ACmm/QBPqRxAT6kcQE+pHEBVhgUAVYYFAFWGBQBZOgnA2ToJwNk6CcDIkiZACJImQAiSJkAdgljAnYJYwJ2CWMCVOZcAVTmXAF9e0AChKFCAYShQgGEoUIBPO4FAzzuBQM=!y7sdAIoTdQOKE3UDwLXNA9EgZgUNUFsFtWJvAqRbfAOkW3wDlk8AAoVAsQKA9rsBlI9dAQdR1QE5ySIF!URCDA1EQgwNREIMDI9adAiPWnQJvdu8Ab3bvANcanwHXGp8B1xqfASaQQgMmkEIDJpBCA0O+3QBDvt0A!"
    #     testdeck = Deck.from_ydke(TestDB.db, ydke_code)
    #     self.assertEqual(ydke_code, testdeck.ydke)


if __name__ == "__main__":
    main()
