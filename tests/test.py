from unittest import TestCase, main

from yugitoolbox import Attribute, Deck, Race, Type, yugidb


class TestDB(TestCase):
    def test_db(self):
        self.maxDiff = None
        testcard = yugidb.get_card_by_id(10497636)
        self.assertEqual(testcard.id, 10497636)
        self.assertEqual(testcard.koid, 16278)
        self.assertEqual(testcard.name, "War Rock Meteoragon")
        testarch = yugidb.get_archetype_by_id(351)
        self.assertEqual(testarch.name, "War Rock")
        testset = yugidb.get_set_by_id(1377)
        self.assertEqual(testset.name, "Lightning Overdrive")
        self.assertTrue(Type.Effect in testcard.type)
        self.assertEqual(testcard.race, Race.Warrior)
        self.assertEqual(testcard.attribute, Attribute.EARTH)
        self.assertEqual(testcard.atk, 2600)
        self.assertEqual(testcard.def_, 2600)
        self.assertEqual(testcard.level, 7)
        self.assertTrue(testcard.id in testarch.cards)
        self.assertTrue(testcard.id in testset.contents)
        self.assertTrue(testarch.id in testcard.archetypes)
        self.assertTrue(testset.id in testcard.sets)
        self.assertIsNotNone(testcard.get_script())
        omegacode1 = "M+ffLv2SpUJvAQMMO9oKsYDwLo1vjDB8NmIdy6HbV5hcbn5jgeHPrZdYYXiD8j0GGF4++wujxvadTDAcWZ3MMjFpHysM2y0pZBRbdIsJhFukVFlg+IygBxzf4drLBMNhunysOxo5mSUXdTGaH7Vn8Jq4lAmExeuPsYBwYLYx8wGp/ywgvFsrCY4/HX7HFH+/gEUsTYX1ReMM1ll717Pur73Cesb8MeuqM09Y/mjkszAs12T5bVnHnGd8jlkt6hqz4LabzJfr3jEbRPqzgMIFAA=="
        testdeck = Deck.from_omegacode(omegacode1)
        omegacode2 = testdeck.to_omegacode()
        self.assertEqual(omegacode1, omegacode2)
        ydke_code1 = "ydke://EUKKAwrmpwEK5qcBR5uPAEebjwBHm48AvadvAfx5vAKzoLECTkEDAE5BAwBOQQMAfjUBBUwyuADDhdcAnNXGA/ZJ0ACmm/QBPqRxAT6kcQE+pHEBVhgUAVYYFAFWGBQBZOgnA2ToJwNk6CcDIkiZACJImQAiSJkAdgljAnYJYwJ2CWMCVOZcAVTmXAF9e0AChKFCAYShQgGEoUIBPO4FAzzuBQM=!y7sdAIoTdQOKE3UDwLXNA9EgZgUNUFsFtWJvAqRbfAOkW3wDlk8AAoVAsQKA9rsBlI9dAQdR1QE5ySIF!URCDA1EQgwNREIMDI9adAiPWnQJvdu8Ab3bvANcanwHXGp8B1xqfASaQQgMmkEIDJpBCA0O+3QBDvt0A!"
        testdeck = Deck.from_ydke(ydke_code1)
        ydke_code2 = testdeck.to_ydke()
        self.assertEqual(ydke_code1, ydke_code2)
        # print(testcard.get_rulings())


if __name__ == "__main__":
    main()
