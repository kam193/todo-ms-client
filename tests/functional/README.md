# Functional tests

## Scope and goal

Those tests are meant to test the behavior of the library as a whole, including
interaction with a real server. They should cover basic use cases and be used
to ensure that the library is working as expected with the current version of
the Microsoft ToDo API.

## Running the tests

Those tests are disabled by default. To run them, you need to set the environmental
variables for loging into the API and the flag to enable the tests. The authentication is
done manually.

Required environmental variables:

* ``APP_ID``, ``APP_SECRET`` - the ID and sectet to use for OAuth2 authentication flow
* ``TEST_USER_EMAIL`` - the email of the user to use for testing. Do not use your own
  account, as the tests will modify the data.
* ``RUN_FUNCTIONAL_TESTS`` - set to ``1`` to enable the tests
