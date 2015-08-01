import numpy as np

from nose.tools import *
from pylogs.LogContainer import LogContainer

TEST_LOG = 'test_log_file.csv'

def test_log_container_pos():
    c = LogContainer(
        r'^(?P<date>.+)\,(?P<fruit>.+?)\,(?P<value>.+?)\,(?P<score>.+?)$',
        dict(date='date', value='integer', score='float'),
        '%b %d %H:%M:%S'
    )
    assert_equal(len(c.fields), 4)
    assert_equal(set(c.fields), set(['date', 'fruit', 'value', 'score']))

    c.parse('tests', TEST_LOG)
    assert_equal(len(c.logs), 7000)
    assert_equal(c.logs[0]['fruit'], 'Pineapple')
    assert_equal(c.logs[-1]['value'], 1496)
    assert_equal(isinstance(c.logs[0]['value'], int), True)
    assert_equal(isinstance(c.logs[-1]['score'], float), True)

    c.order('value', 'score')
    assert_equal(c.logs[0]['fruit'], 'Orange')
    assert_equal(c.logs[-1]['value'], 6683)
    assert_equal(c.logs[-1]['score'], 0.981300247833133)

    summ = c.summarize(val='score', by='fruit', var='Kiwi', funcs=np.std)
    assert_equal(summ, {'Kiwi': {'std': 0.27986574484522858}})

    summ2 = c.summarize(val='score', by='fruit', funcs=[min, np.mean])
    assert_equal(len(summ2), 29)
    assert_equal(summ2['Kiwi']['min'], 0.0160085917450488)
    assert_equal(summ2['Banana']['mean'], 0.52150886139278263)

@raises(ValueError)
def test_log_container_init_neg1():
    c = LogContainer(r'^.*$', dict(some_value='integer'))

@raises(ValueError)
def test_log_container_init_neg2():
    c = LogContainer(
        r'^(?P<date>.+)\,(?P<fruit>.+?)\,(?P<value>.+?)\,(?P<score>.+?)$',
        dict(date='date', val='integer', score='float'),
        '%b %d %H:%M:%S'
    )

@raises(TypeError)
def test_log_container_parse_neg1():
    c = LogContainer(
        r'^(?P<date>.+)\,(?P<fruit>.+?)\,(?P<value>.+?)\,(?P<score>.+?)$',
        dict(date='date', value='integer', score='score'),
        '%b %d %H:%M:%S'
    )
    c.parse('tests', TEST_LOG)

def test_log_container_parse_neg2():
    c = LogContainer(
        r'^(?P<date>.+)\,(?P<fruit>.+?)\,(?P<value>.+?)\,(?P<score>.+?)$',
        dict(date='date', value='integer', score='score'),
        '%b %d %H:%M:%S'
    )
    c.parse('tests', 'random_file_name')
    assert_equal(len(c.logs), 0)

@raises(ValueError)
def test_log_container_order_neg1():
    c = LogContainer(
        r'^(?P<date>.+)\,(?P<fruit>.+?)\,(?P<value>.+?)\,(?P<score>.+?)$',
        dict(date='date', value='integer', score='float'),
        '%b %d %H:%M:%S'
    )
    c.parse('tests', TEST_LOG)
    c.order('val')

@raises(ValueError)
def test_log_container_summarize_neg1():
    c = LogContainer(
        r'^(?P<date>.+)\,(?P<fruit>.+?)\,(?P<value>.+?)\,(?P<score>.+?)$',
        dict(date='date', value='integer', score='float'),
        '%b %d %H:%M:%S'
    )
    c.parse('tests', TEST_LOG)
    c.order('value')
    c.summarize(val='val', by='fruit', var='Kiwi', funcs=np.std)

@raises(TypeError)
def test_log_container_summarize_neg2():
    c = LogContainer(
        r'^(?P<date>.+)\,(?P<fruit>.+?)\,(?P<value>.+?)\,(?P<score>.+?)$',
        dict(date='date', value='integer', score='float'),
        '%b %d %H:%M:%S'
    )
    c.parse('tests', TEST_LOG)
    c.order('value')
    c.summarize(val='score', by='fruit', funcs=123)
