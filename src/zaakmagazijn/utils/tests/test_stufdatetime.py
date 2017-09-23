import datetime

from django.test import TestCase

from .. import stuf_datetime


class StUFDateTimeTests(TestCase):
    def setUp(self):
        self.dt = datetime.datetime(2017, 12, 31, 23, 59, 59)

    def indicatie_onvolledige_datum_v(self):
        ind = stuf_datetime.indicatie_onvolledige_datum('20171231')
        self.assertEqual(ind, stuf_datetime.IndicatieOnvolledigeDatum.V)

    def indicatie_onvolledige_datum_d(self):
        ind = stuf_datetime.indicatie_onvolledige_datum('201712  ')
        self.assertEqual(ind, stuf_datetime.IndicatieOnvolledigeDatum.D)

    def indicatie_onvolledige_datum_m(self):
        ind = stuf_datetime.indicatie_onvolledige_datum('2017    ')
        self.assertEqual(ind, stuf_datetime.IndicatieOnvolledigeDatum.M)

    def indicatie_onvolledige_datum_j(self):
        ind = stuf_datetime.indicatie_onvolledige_datum('        ')
        self.assertEqual(ind, stuf_datetime.IndicatieOnvolledigeDatum.J)

    def test_stuf_date_v(self):
        stuf_dt = stuf_datetime.stuf_date(self.dt, stuf_datetime.IndicatieOnvolledigeDatum.V)
        self.assertEqual(stuf_dt, '20171231')

    def test_stuf_date_d(self):
        stuf_dt = stuf_datetime.stuf_date(self.dt, stuf_datetime.IndicatieOnvolledigeDatum.D)
        self.assertEqual(stuf_dt, '201712  ')

    def test_stuf_date_m(self):
        stuf_dt = stuf_datetime.stuf_date(self.dt, stuf_datetime.IndicatieOnvolledigeDatum.M)
        self.assertEqual(stuf_dt, '2017    ')

    def test_stuf_date_j(self):
        stuf_dt = stuf_datetime.stuf_date(self.dt, stuf_datetime.IndicatieOnvolledigeDatum.J)
        self.assertEqual(stuf_dt, '        ')

    def test_stuf_datetime_v(self):
        stuf_dt = stuf_datetime.stuf_datetime(self.dt, stuf_datetime.IndicatieOnvolledigeDatum.V)
        self.assertEqual(stuf_dt, '20171231235959')

    def test_stuf_datetime_d(self):
        stuf_dt = stuf_datetime.stuf_datetime(self.dt, stuf_datetime.IndicatieOnvolledigeDatum.D)
        self.assertEqual(stuf_dt, '201712  235959')

    def test_stuf_datetime_m(self):
        stuf_dt = stuf_datetime.stuf_datetime(self.dt, stuf_datetime.IndicatieOnvolledigeDatum.M)
        self.assertEqual(stuf_dt, '2017    235959')

    def test_stuf_datetime_j(self):
        stuf_dt = stuf_datetime.stuf_datetime(self.dt, stuf_datetime.IndicatieOnvolledigeDatum.J)
        self.assertEqual(stuf_dt, '        235959')
