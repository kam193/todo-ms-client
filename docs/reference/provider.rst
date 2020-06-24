Provider
========

Package `todoms.provider` contains abstract class for providers and one simple provider.

Provider is responsible for authorize user, storing auth data and execute API calls.
For now there is only one simple example allows login by opening browser. Probably you
should build your own provider, shaped for your use case.

------------------
Provider interface
------------------

.. autoclass:: todoms.provider.base.AbstractProvider

-------------------
WebBrowser provider
-------------------

.. module:: todoms.provider.browser_provider

.. autoclass:: WebBrowserProvider

++++++++++
Exceptions
++++++++++

.. autoclass:: RequestBeforeAuthenticatedError
    :no-inherited-members:
