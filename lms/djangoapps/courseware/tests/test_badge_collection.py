"""
Tests that BadgeCollection behaves correctly when initializing.
"""

from mock import patch

from django.test import TestCase

import courseware.badges as badges


@patch('courseware.badges._fetch')
class FailedFetchTestCase(TestCase):
    """
    Test that badges.BadgeCollection.__init__ behaves correctly when _fetch throws BadgingServiceError.
    BadgeCollection.__init__ should re-raise the BadgingServiceError.
    """

    def setUp(self):
        """
        Create a fake _fetch method to use in tests.
        """
        def temp_fetch(url):
            """
            Raise BadgingServiceError, imitating a _fetch method that always fails.
            """
            raise badges.BadgingServiceError()
        self.temp_fetch = temp_fetch

    def test_with_course(self, mock_fetch):
        """
        Case in which BadgeCollection receives a course id.
        """
        mock_fetch.side_effect = self.temp_fetch

        try:
            badges.BadgeCollection("", "")
            # If no error is thrown, fail the test.
            self.assertEquals(None, badges.BadgingServiceError)
        except badges.BadgingServiceError:
            # Pass the test.
            pass

    def test_without_course(self, mock_fetch):
        """
        Case in which BadgeCollection does not receive a course id.
        """
        mock_fetch.side_effect = self.temp_fetch

        try:
            badges.BadgeCollection("")
            # If no error is thrown, fail the test.
            self.assertEquals(None, badges.BadgingServiceError)
        except badges.BadgingServiceError:
            # Pass the test.
            pass


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
        Case when BadgeCollection receives a course id.
        """
        mock_fetch.side_effect = self.temp_fetch

        output = badges.BadgeCollection('', '')
        self.assertEquals(output.get_badges(), [])
        self.assertEquals(output.get_earned_badges(), [])
        self.assertEquals(output.get_unlockable_badges(), [])
        self.assertEquals(output.get_badge_urls(), '[]')

    def test_blank_data_without_course(self, mock_fetch):
        """
        Case when BadgeCollection does not receive a course id.
        """
        mock_fetch.side_effect = self.temp_fetch

        output = badges.BadgeCollection('')
        self.assertEquals(output.get_badges(), [])
        self.assertEquals(output.get_earned_badges(), [])
        self.assertEquals(output.get_unlockable_badges(), [])
        self.assertEquals(output.get_badge_urls(), '[]')
