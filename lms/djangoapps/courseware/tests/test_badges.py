"""
Contains tests for courseware/badges.py
"""
# Allow accessing protected function _fetch in badges.py:
# pylint: disable=W0212

from mock import MagicMock, patch

from django.test import TestCase

import courseware.badges as badges


@patch('courseware.badges._fetch')
class BlankBadgeDataTestCase(TestCase):
    """
    Test that badges.BadgeCollection.__init__ behaves correctly on empty inputs.
    """
    def setUp(self):
        """
        Mock the _fetch() method to return fake blank data.
        """
        def temp_fetch(url):
            """
            Returns blank fake data depending on the URL passed in.
            """
            if 's/.json' in url:  # list endpoint
                return []
            else:
                return {}

        self.temp_fetch = temp_fetch

    def test_blank_data_with_course(self, mock_fetch):
        """
        In the case when a course is passed to make_badge_data -- test that make_badge_data returns
        what it should.
        """
        mock_fetch.side_effect = self.temp_fetch

        output = badges.BadgeCollection('', '')
        self.assertEquals(output.get_badges(), [])
        self.assertEquals(output.get_earned_badges(), [])
        self.assertEquals(output.get_unlockable_badges(), [])
        self.assertEquals(output.get_badge_urls(), '[]')

    def test_blank_data_without_course(self, mock_fetch):
        """
        In the case when a course is not passed to make_badge_data -- test that make_badge_data returns
        what it should.
        """
        mock_fetch.side_effect = self.temp_fetch

        output = badges.BadgeCollection('')
        self.assertEquals(output.get_badges(), [])
        self.assertEquals(output.get_earned_badges(), [])
        self.assertEquals(output.get_unlockable_badges(), [])
        self.assertEquals(output.get_badge_urls(), '[]')


@patch('courseware.badges._fetch')
class FailingBadgeTestCase(TestCase):
    """
    Test that badges.BadgeCollection.__init__ behaves correctly when _fetch throws BadgingServiceError.
    """
    def setUp(self):
        """
        Mock the _fetch() method to throw a BadgingServiceError, to simulate what happens
        when the requests library is unable to access the badge server.
        """
        def temp_fetch(url):
            """
            Raise BadgingServiceError, imitating a _fetch method that always fails.
            """
            raise badges.BadgingServiceError()

        self.temp_fetch = temp_fetch

    def test_failing_with_course(self, mock_fetch):
        """
        In the case when a course is passed to BadgeCollection.__init__ -- test that it catches the exception
        and returns blank data.
        """
        mock_fetch.side_effect = self.temp_fetch

        output = badges.BadgeCollection("", "")
        self.assertEquals(output.get_badges(), [])
        self.assertEquals(output.get_earned_badges(), [])
        self.assertEquals(output.get_unlockable_badges(), [])
        self.assertEquals(output.get_badge_urls(), '[]')

    def test_failing_without_course(self, mock_fetch):
        """
        In the case when a course is not passed to BadgeCollection.__init__ -- test that it catches the exception
        and returns blank data.
        """
        mock_fetch.side_effect = self.temp_fetch

        output = badges.BadgeCollection("")
        self.assertEquals(output.get_badges(), [])
        self.assertEquals(output.get_earned_badges(), [])
        self.assertEquals(output.get_unlockable_badges(), [])
        self.assertEquals(output.get_badge_urls(), '[]')


@patch('courseware.badges.requests')
class FetchTestCase(TestCase):
    """
    Tests the _fetch helper method of badges.py.

    The tests which test make_badge_data, the only function in badges.py which uses the _fetch helper method,
    do so by creating a mock of _fetch -- so _fetch itself needs this testing.
    """
    def setUp(self):
        """
        Create a mock of the requests library which has a dummy get() method.
        """
        def fake_get(url, timeout=None):
            """
            Return fake data, depending on the URL passed in. Replaces requests.get.
            """

            # _fetch should not be calling get without a timeout. If it is, that's a problem.
            if timeout is None:
                raise ValueError("badges._fetch calls requests.get without specifying a timeout -- which is bad")
            response = MagicMock()

            if 'testlist' in url:
                output = {'results': ['list', 'of', 'things'], 'next': None, 'prev': None}
            elif 'test_list_1' in url:
                output = {'results': ['thing 1', 'thing 2'], 'next': 'test_list_2', 'prev': None}
            elif 'test_list_2' in url:
                output = {'results': ['thing 3'], 'next': None, 'prev': 'test_list_1'}
            elif 'test_instance' in url:
                output = {'dummy JSON object': True}
            else:
                output = None

            response.json = output
            return response

        self.fake_get = fake_get

    def test_fetch_list(self, mock_requests):
        """
        Test that _fetch returns correctly when reading a single list of objects.
        """
        mock_requests.get = MagicMock()
        mock_requests.get.side_effect = self.fake_get

        obtained_output = badges._fetch('testlist')
        ideal_output = ['list', 'of', 'things']
        self.assertItemsEqual(ideal_output, obtained_output)

    def test_fetch_list_paginated(self, mock_requests):
        """
        Test that _fetch returns all pages' lists put together when reading a paginated list of objects.
        """
        mock_requests.get = MagicMock()
        mock_requests.get.side_effect = self.fake_get

        obtained_output = badges._fetch('test_list_1')
        ideal_output = ['thing 1', 'thing 2', 'thing 3']
        self.assertItemsEqual(ideal_output, obtained_output)

    def test_fetch_instance(self, mock_requests):
        """
        Test that _fetch returns correctly when reading a single object.
        """
        mock_requests.get = MagicMock()
        mock_requests.get.side_effect = self.fake_get

        obtained_output = badges._fetch('test_instance')
        ideal_output = {'dummy JSON object': True}
        self.assertEqual(ideal_output, obtained_output)
