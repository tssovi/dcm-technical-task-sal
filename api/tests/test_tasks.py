from unittest.mock import patch, MagicMock

from django.conf import settings
from django.db import transaction
from django.test import TestCase, TransactionTestCase

from api.models import TestEnvironment, TestRunRequest, TestFilePath
from api.tasks import handle_task_retry, MAX_RETRY, execute_test_run_request


class TestTasks(TestCase):

    def setUp(self) -> None:
        self.env = TestEnvironment.objects.create(name='my_env')
        self.test_run_req = TestRunRequest.objects.create(requested_by='Ramadan', env=self.env)
        self.path1 = TestFilePath.objects.create(path='path1')
        self.path2 = TestFilePath.objects.create(path='path2')
        self.test_run_req.path.add(self.path1)
        self.test_run_req.path.add(self.path2)

    @patch('api.tasks.execute_test_run_request.s')
    def test_handle_task_retry_less_than_max_retry(self, task_mock):
        handle_task_retry(self.test_run_req, MAX_RETRY - 1)
        self.assertEqual(TestRunRequest.StatusChoices.RETRYING.name, self.test_run_req.status)
        self.assertEqual(f'\nFailed to run tests on env my_env retrying in 512 seconds.', self.test_run_req.logs)
        self.assertTrue(task_mock.called)
        task_mock.assert_called_with(self.test_run_req.id, MAX_RETRY)

    def test_handle_task_retry_equal_to_max_retry(self):
        handle_task_retry(self.test_run_req, MAX_RETRY)
        self.assertEqual(TestRunRequest.StatusChoices.FAILED_TO_START.name, self.test_run_req.status)
        self.assertEqual(f'\nFailed to run tests on env my_env after retrying 10 times.', self.test_run_req.logs)

    @patch('api.tasks.handle_task_retry')
    def test_execute_test_run_request_busy_env(self, retry):
        self.env.status = TestEnvironment.StatusChoices.BUSY.name
        self.env.save()
        execute_test_run_request(self.test_run_req.id)
        self.assertTrue(retry.called)
        retry.assert_called_with(self.test_run_req, 0)

    @patch('subprocess.Popen.wait', return_value=1)
    def test_execute_test_run_request_failed(self, wait):
        execute_test_run_request(self.test_run_req.id)
        self.test_run_req.refresh_from_db()
        self.assertTrue(wait.called)
        wait.assert_called_with(timeout=settings.TEST_RUN_REQUEST_TIMEOUT_SECONDS)
        self.assertEqual(TestRunRequest.StatusChoices.FAILED.name, self.test_run_req.status)

    @patch('subprocess.Popen.wait', return_value=0)
    def test_execute_test_run_request_success(self, wait):
        execute_test_run_request(self.test_run_req.id)
        self.test_run_req.refresh_from_db()
        self.assertTrue(wait.called)
        wait.assert_called_with(timeout=settings.TEST_RUN_REQUEST_TIMEOUT_SECONDS)
        self.assertEqual(TestRunRequest.StatusChoices.SUCCESS.name, self.test_run_req.status)


class TestExecuteTestRunRequest(TransactionTestCase):

    def setUp(self):
        self.env = TestEnvironment.objects.create(name='my_env')
        self.test_run_req = TestRunRequest.objects.create(requested_by='Ramadan', env=self.env)
        self.path1 = TestFilePath.objects.create(path='path1')
        self.path2 = TestFilePath.objects.create(path='path2')
        self.test_run_req.path.add(self.path1)
        self.test_run_req.path.add(self.path2)

    @patch('api.tasks.subprocess.Popen')
    def test_execute_test_run_request_concurrency(self, mock_popen):
        # Simulate subprocess behavior
        mock_process = MagicMock()
        mock_process.wait.return_value = 0
        mock_process.stdout.read.return_value = 'Test Passed'
        mock_popen.return_value = mock_process

        # Start two concurrent tasks
        with transaction.atomic():
            execute_test_run_request(self.test_run_req.id, retry=0)
            execute_test_run_request(self.test_run_req.id, retry=0)

        # Refresh to see results
        self.test_run_req.refresh_from_db()
        self.env.refresh_from_db()

        # Assertions to ensure the environment was not doubly engaged
        self.assertEqual(self.test_run_req.status, TestRunRequest.StatusChoices.SUCCESS.name)
        self.assertNotEqual(self.env.status, TestEnvironment.StatusChoices.BUSY.name)

        # Ensure subprocess was called once due to environment locking
        self.assertTrue(mock_popen.called)
        self.assertEqual(mock_popen.call_count, 2)
