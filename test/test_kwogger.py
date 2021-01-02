import kwogger
import unittest
import os
import time
from collections import Counter


class KwoggerTests(unittest.TestCase):

    LOG_PATH = './unittest.log'

    def tearDown(self):
        try:
            os.remove(self.LOG_PATH)
        except FileNotFoundError:
            pass

    def test_base_logging_methods(self):

        #
        # write log entries
        #

        log = kwogger.configure('unittest.test_base_logging_methods', self.LOG_PATH, is_unit_test=True)
        test_id = log.generate_id('test_id')

        log.info('TEST_TYPES', null=None, bool_t=True, bool_f=False, integer=1, float=1.5, string='hello', other=os)

        log.debug('TEST_LEVELS')
        log.info('TEST_LEVELS')
        log.warning('TEST_LEVELS')
        log.error('TEST_LEVELS')
        log.critical('TEST_LEVELS')

        try:
            1 + '1'
        except TypeError:
            log.debug_exc('TEST_EXCEPTION')
            log.info_exc('TEST_EXCEPTION')
            log.warning_exc('TEST_EXCEPTION')
            log.error_exc('TEST_EXCEPTION')
            log.critical_exc('TEST_EXCEPTION')

        log.logger.handlers[0].close()

        #
        # parse log entries
        #

        with kwogger.KwogFile(self.LOG_PATH) as parser:
            levels = Counter()
            for line in parser:
                self.assertIsInstance(line, kwogger.KwogEntry)

                # check context values
                self.assertTrue(line.context['is_unit_test'], msg='missing context value: is_unit_test')
                self.assertEqual(line.context['test_id'], test_id, msg='missing context value: test_id')

                # check parsed data types
                if line.entry['msg'] == 'TEST_TYPES':
                    self.assertIsNone(line.entry['null'], msg='type error: entry.null')
                    self.assertTrue(line.entry['bool_t'], msg='type error: entry.bool_t')
                    self.assertFalse(line.entry['bool_f'], msg='type error: entry.bool_f')
                    self.assertIsInstance(line.entry['integer'], int, msg='type error: entry.integer')
                    self.assertIsInstance(line.entry['float'], float, msg='type error: entry.float')
                    self.assertIsInstance(line.entry['string'], str, msg='type error: entry.string')
                    self.assertIsInstance(line.entry['other'], str, msg='type error: entry.other')
                else:
                    levels[line.level_name] += 1

        # check parsed log levels
        self.assertEqual(levels['DEBUG'], 2, msg='did not get 2 debug calls')
        self.assertEqual(levels['INFO'], 2, msg='did not get 2 info calls')
        self.assertEqual(levels['WARNING'], 2, msg='did not get 2 warning calls')
        self.assertEqual(levels['ERROR'], 2, msg='did not get 2 error calls')
        self.assertEqual(levels['CRITICAL'], 2, msg='did not get 2 critical calls')

        #
        # test kwog file level filter
        #

        with kwogger.KwogFile(self.LOG_PATH, kwogger.WARNING) as parser:
            for line in parser:
                self.assertGreaterEqual(line.level, kwogger.WARNING)

    def test_timer(self):
        log = kwogger.configure('unittest.test_timer', self.LOG_PATH)
        log.timer_start('TIMER_A')
        time.sleep(.3)

        log.timer_start('TIMER_B')
        log.timer_checkpoint('TIMER_A')
        time.sleep(.3)

        log.timer_stop('TIMER_A')
        log.timer_stop('TIMER_B')

        log.logger.handlers[0].close()


if __name__ == '__main__':
    unittest.main()
