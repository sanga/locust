import unittest
from locust import TaskSet, Locust

class MyTaskSet(TaskSet):
    def _sleep(self, seconds):
        """ Bypass actual sleeping
        """
        pass

class DummyLocust(Locust):
    host = 'dummy'
        

class MovingAverageTest(unittest.TestCase):
    """ This is not a unit test per se because it may fail ocassionally, which is perfectly ok since it deals with randomness.
        It is more for testing the expected behavior if using self.avg_wait in a Locust class and for feedback on the algorithm used.
    """

    def _setupLocust(self, min_wait, avg_wait, max_wait):
        ts = MyTaskSet(DummyLocust())
        ts.min_wait = min_wait
        ts.avg_wait = avg_wait
        ts.max_wait = max_wait
        return ts

    def _wait(self, ts, count):
        for x in xrange(count):
            ts.wait()

    def _get_deviation(self, ts):
        return abs(ts._avg_wait - ts.avg_wait)

    def _get_max_deviation(self, ts, percent):
        return ts.avg_wait * (percent / 100.0)

    def _deviation(self, ts, percentage):
        deviation = self._get_deviation(ts)
        max_deviation = self._get_max_deviation(ts, percentage)
        print "Deviation: %.3f ms (%1.3f%%), max: %s ms (%s%%)" % (deviation, deviation / ts.avg_wait * 100.0, max_deviation, percentage)
        return deviation, max_deviation, percentage

    def _dump_stats(self, ts):
        print "Num waits: %d Wanted Average: %s Actual Average: %s" % (ts._avg_wait_ctr, ts.avg_wait, ts._avg_wait)

    def _assertion(self, ts, deviation, max_deviation, percentage):
        self._dump_stats(ts)
        self.assertTrue(deviation < max_deviation, msg="Deviation not within %s%% of wanted average" % percentage)

    def test_moving_average_100000(self):
        ts = self._setupLocust(3000, 140000, 20 * 60 * 1000) # 3 seconds, 140 seconds, 20 minutes
        print "Large"
        self._wait(ts, 100000)
        (deviation, max_deviation, percentage) = self._deviation(ts, 1.0)
        self._assertion(ts, deviation, max_deviation, percentage)

    def test_moving_average_100(self):
        # This test is actually expected to fail sometimes
        ts = self._setupLocust(3000, 140000, 20 * 60 * 1000) # 3 seconds, 140 seconds, 20 minutes
        print "Small"
        self._wait(ts, 100)
        (deviation, max_deviation, percentage) = self._deviation(ts, 5.0)
        self._assertion(ts, deviation, max_deviation, percentage)

    def test_omit_average(self):
        ts = self._setupLocust(3000, None, 20 * 60 * 1000) # 3 seconds, None, 20 minutes
        print "Omitted"
        self.assertEquals(None, ts.avg_wait)
        self.assertEquals(0, ts._avg_wait)
        self.assertEquals(0, ts._avg_wait_ctr)
        self._wait(ts, 100000)
        self.assertEquals(None, ts.avg_wait)
        self.assertEquals(0, ts._avg_wait)
        self.assertEquals(0, ts._avg_wait_ctr)


if __name__ == '__main__':
    unittest.main()