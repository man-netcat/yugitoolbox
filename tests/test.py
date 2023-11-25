from unittest import TestCase, main

from yugitoolbox import Attribute, Race, Type, yugidb


class TestDB(TestCase):
    def test_db(self):
        card = yugidb.get_card_by_id(10497636)
        self.assertEqual(card.name, "War Rock Meteoragon")
        arch = yugidb.get_archetype_by_id(351)
        self.assertEqual(arch.name, "War Rock")
        set = yugidb.get_set_by_id(1377)
        self.assertEqual(set.name, "Lightning Overdrive")
        self.assertTrue(Type.Effect in card.type)
        self.assertEqual(card.race, Race.Warrior)
        self.assertEqual(card.attribute, Attribute.EARTH)
        self.assertEqual(card.atk, 2600)
        self.assertEqual(card.def_, 2600)
        self.assertEqual(card.level, 7)
        self.assertTrue(card.id in arch.cards)
        self.assertTrue(card.id in set.contents)
        self.assertTrue(arch.id in card.archetypes)
        self.assertTrue(set.id in card.sets)


if __name__ == "__main__":
    main()
