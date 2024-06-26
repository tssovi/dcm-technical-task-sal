# DCM Technical Task

This is a web application that provides a central place to run Python-based
tests. These tests run in a shared environment.

There are some sample tests (some failing, some not, and some that have delays
for more realism) and the tests for this application can also be run in the
runner. The tests are executed on the machine that hosts the test executor
application.

In order to be able to follow instructions and implement the task you need to
have docker on your computer. The required docker version is >= 20.10.8

## Feature to be implemented:

Users of the test runner have asked to have the ability to upload a new test
into the application and run it.  For example, they would like to be able to
upload a simple test that calls a public API and then validates the response.

### Acceptance Criteria

* The user can select a file from their computer and upload it into one of the
  directories or a new directory for the uploaded tests and then they should be
  able to run that test.

* New feature should be tested with unit tests (backend only)

## Bugfix

When running 2 tests in the same environment, there is the possibility that when
multiple workers are being used, that a race condition could occur where both
the workers think the environment is available and as a result both try to use
it.

Please find a way to fix this issue.

Hint: The issue is in the api/tasks.py file

## After the bug

After the bug is fixed and feature is implemented, make sure that the following works properly:

* Creating a new test run with the following:
  * Username
  * Test environment ID (choose an ID between 1 and 100)
  * Choosing one or more files to test (the available tests are read from file system)

**NOTE:** It should not be possible to run a test in an environment where there
    is already a test running, the next test for that environment should wait until the previous is complete!

* List all previous test runs in a table including their outcome (failed, success,
running)

* List details for one test run
  * Show username, test env ID and what was tested
  * Show the full log that the test created


## How to Run the current project locally

First of all add following entry to your `/etc/hosts`:

```
127.0.0.1  ionos.local
```

Above entry maps `ionos.local` domain to your localhost.


```
cd ionos
cp .env.dist .env
cd ..
docker compose build
docker compose up
docker compose run backend pytest --disable-pytest-warnings  api/tests/
```
Go to http://ionos.local/ to see access the application (the frontend part of it).


## How it works

When creating a new test run request, it triggers a celery task to execute it on
the selected env. If the env is busy, we wait for some time (or give up after
some retries) and when it's done, we change the status of the request and save
the logs. in the frontend, we call the listing api every one second to get a
live updates (also the details api).

In the project we have sample-tests directory to save all the sample tests that
can be run. Also, you can choose the actual test files from api.tests dir. The
test path is a multi-select, you can choose one or more file to test at a time
and these paths are created automatically in a migration file
api/migrations/0002_auto_20200706_1208.py
