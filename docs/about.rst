=====
About
=====

Design Philosophy
=================

Accessing APIs open-endily is an easy affair. ``pip install requests``, pass in your data
get data back. But the slight differences and demands of different API creating code that's structured, re-usable and simple proves difficult.

nap hopes to help.

nap aims to be

* Support Read (GET) and Write (POST/PUT/PATCH)
* Little to no configuration needed for to-spec REST APIs
* Easy to configure to fit any REST-like API
* Customize to fit even edgier use cases

Warnings about API Design.
==========================

REST, similarly so many wonderful technological buzzronyms before it, was something specific that has come to mean something vaguely "not SOAP." Because of this, nap triesto pick safe, undestructive defaults. The tradeoff with this decision is there is a little bit more customization required to make things work than a more traditional modeling backend (such as a relational database). To facilitate this, nap has an extensive list of :doc:`options <options>` to make setting these configuration easy as possible.

Your nap models will only go as far as your API allows. For instance, if your API's collections only return partial data about your object, you won't have access to the left out fields (and risk saving over them without proper configuration!). The more you expose in your API the easier using nap will be.

Thanks
======

nap is the spiritual descendant of `remote objects`_, and owes the core idea to it's leg work -- and both owe a great deal to the declarative syntax of `Django models`_ and `SQLAlchemy`_

.. _remote objects: https://github.com/saymedia/remoteobjects
.. _Django models: http://www.sqlalchemy.org/
.. _SQLAlchemy: https://docs.djangoproject.com/en/dev/topics/db/models/
