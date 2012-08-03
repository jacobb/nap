================
Tutorial: Part 1
================

In part one of our tutorial, we'll be creating a :class:`~ResourceModel` to internact with a simple Tastypie Django site. `Tastypie`_ is a third party Django app that makes creating to-spec REST APIs. Because of this, it's the perfect match to write our first :class:`~ResourceModel`, as it will require only a little fine tuning.

.. _Tastypie: http://tastypieapi.org/


Step 0: Writing our API
=======================

Our API will closely match the one inferred to in :doc:`quickstart`. Feel free to write your own as you follow along with this tutorial, but if you'd like to just use ours, the source code is available `here <https://github.com/jacobb/example_nap_api/>`_
