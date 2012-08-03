.. nap documentation master file, created by
   sphinx-quickstart on Sat Jul  7 01:11:38 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to nap's documentation!
===============================

===
nap
===
Accessing APIs open-endily is an easy affair. pip install requests, pass in your data get data back. But the slight differences and demands of different API creating code that’s structured, re-usable and simple proves difficult.

nap hopes to help.

nap aims to be:

* Support Read (GET) and Write (POST/PUT/PATCH)
* Little to no configuration needed for to-spec REST APIs
* Easy to configure to fit any REST-like API
* Customize to fit even edgier use cases

Contents:

.. toctree::
   :maxdepth: 2

   quickstart

* Tutorial.
   * :doc:`Part 1: a Tastypie API <tutorial/tutorial1>`
   * :doc:`Part 2: Github Gist API <tutorial/tutorial2>`

.. toctree::
   :maxdepth: 2

   resourcemodel
   fields
   urls
   options
   etc
