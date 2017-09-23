from django.test import SimpleTestCase

from ..utils import set_model_value


class SetModelValueTests(SimpleTestCase):

    def test_set_model_value(self):

        class Thing:
            pass

        thing1 = Thing()
        thing1.thing2 = Thing()
        thing1.thing2.thing3 = Thing()

        thing = set_model_value(thing1, 'thing2__thing3__foo', 'bar')
        self.assertEqual(thing, thing1.thing2.thing3)
        self.assertEqual(thing1.thing2.thing3.foo, 'bar')

    def test_set_model_value2(self):
        class Thing:
            bar = None
        foo = Thing()
        foo2 = set_model_value(foo, 'bar', 'baz')
        self.assertEqual(foo, foo2)
        self.assertEqual(foo.bar, 'baz')
