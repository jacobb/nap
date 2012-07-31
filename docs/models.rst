===================
Defining Your Model
===================

Taking full advantage of all of nap's features requires a properly configured model. Luckily, nap makes this easy through it's declarative field syntax, custom API URLs, various :doc:`options` and subclassing ResourceModel's methods.


Fields
======

Main article: :doc:`fields`

Each field is a one-to-one mapping with a attribute returned in your API's response. It handles any validation and coerition (*scrubbing*) necessary to turn the API data into Python (and back to an API data string again). Special fields can be used to group API data into sub-collections of ResourceModels.

Lookup URLs
===========

Main article: :doc:`urls`

Options
=======

Main article: :doc:`options`

ResourceModel
=============

Main article: :doc:`resourcemodel`
