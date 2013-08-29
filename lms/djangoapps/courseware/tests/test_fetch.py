"""
Tests the _fetch helper method of badges.py.
"""
# Allow accessing protected function _fetch in badges.py:
# pylint: disable=W0212

from mock import MagicMock, patch
import requests

from django.test import TestCase

import courseware.badges as badges


class ListTestCase(TestCase):
    """
    Test that _fetch returns correctly when reading a simple list of objects.
    """

    @patch('courseware.badges.requests')
    def test(self, mock_requests):
        """
        """
        output = ['list', 'of', 'things']

        def fake_get(url, timeout=None):
            """
            Returns dummy information. Replaces requests.get.
            """
            # _fetch should not be calling get without a timeout. If it is, that's a problem.
            if timeout is None:
                raise ValueError("badges._fetch calls requests.get without specifying a timeout -- which is bad")
            response = MagicMock()
            response.json = {'results': output, 'next': None, 'prev': None}
            return response

        mock_requests.get = fake_get
        mock_requests.exceptions.RequestException = requests.exceptions.RequestException

        result = badges._fetch('dummy_url')
        self.assertItemsEqual(result, output)


class PaginatedListTestCase(TestCase):
    """
    Test that _fetch returns all pages' lists put together when reading a paginated list of objects.
    """

    @patch('courseware.badges.requests')
    def test(self, mock_requests):
        """
        """
        output_1 = ('1', '2', '42', '33')
        output_2 = ('3', '100')

        def fake_get(url, timeout=None):
            """
            Returns dummy information, depending on the url passed in. Replaces requests.get.
            """
            if timeout is None:
                raise ValueError("badges._fetch calls requests.get without specifying a timeout -- which is bad")
            if 'dummy_url/1' in url:
                json = {'results': list(output_1), 'next': 'dummy_url/2', 'prev': None}
            elif 'dummy_url/2' in url:
                json = {'results': list(output_2), 'next': None, 'prev': 'dummy_url/1'}
            else:
                raise ValueError(url)
            response = MagicMock()
            response.json = json
            return response

        mock_requests.get = fake_get
        mock_requests.exceptions.RequestException = requests.exceptions.RequestException

        result = badges._fetch('dummy_url/1')
        self.assertItemsEqual(result, output_1 + output_2)


class InstanceTestCase(TestCase):
    """
    Test that _fetch returns correctly when reading a single object.
    """

    @patch('courseware.badges.requests')
    def test(self, mock_requests):
        """
        """
        output = {'dummy JSON object': True}

        def fake_get(url, timeout=None):
            """
            Returns dummy information. Replaces requests.get.
            """
            if timeout is None:
                raise ValueError("badges._fetch calls requests.get without specifying a timeout -- which is bad")
            response = MagicMock()
            response.json = output
            return response

        mock_requests.get = fake_get
        mock_requests.exceptions.RequestException = requests.exceptions.RequestException

        result = badges._fetch('dummy_url')
        self.assertItemsEqual(result, output)


class RequestExceptionTestCase(TestCase):
    """
    Test that _fetch correctly catches RequestExceptions and re-raises them as BadgingServiceErrors.
    """

    @patch('courseware.badges.requests')
    def test(self, mock_requests):
        """
        """
        def fake_get(url, timeout=None):
            """
            Always throws RequestException. Replaces requests.get.
            """
            raise requests.exceptions.RequestException()

        mock_requests.get = fake_get
        mock_requests.exceptions.RequestException = requests.exceptions.RequestException

        try:
            badges._fetch('dummy_url')
            # If no error is thrown, fail the test.
            self.assertEquals(None, badges.BadgingServiceError)
        except badges.BadgingServiceError:
            # Pass the test.
            pass
        # except requests.exceptions.RequestException:
            # Fail the test.
            # self.assertEqual(requests.exceptions.RequestException, badges.BadgingServiceError)

