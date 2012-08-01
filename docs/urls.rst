====
URLs
====

.. currentmodule:: nap.lookup

Proper URL patterns are the backbone of a ResourceModel. URLs are defined in a ResourceModel as a tuple of ``nap_urls``--a thin wrapper around a python-formatted string. These are defined and tied to a ResourceModel through the :ref:`urls`, :ref:`prepend_urls`, and :ref:`append_urls`. These are stored in the ResourceModel's ``_meta``

By default, ResourceModels have two nap_urls that allow them to make all common calls to a to-spec REST API::

    (
        nap_url('%(resource_name)s/', create=True, lookup=False, collection=True),
        nap_url('%(resource_name)s/%(resource_id)s/', update=True),
    )


How a URL lookup works
======================

nap_urls contain three parts of information:

#) The kinds of lookups that this url can be used for.
#) The URL String itself
#) The names of variables needed to generate

On calls that are backed by a URL, Nap will iterate through every URL in it's url list looking for a match. A match is considered a URL where

#) The URL is valid for the type of request being attempted
#) The variablres required to generated a valid URL are available.

Let's dive into each part of a URL to understand this process a bit better.


Lookup Types
------------

Lookup types closely match the kind of operations possible with an API. They are
``create``, ``lookup``, ``update``, ``collection``.

* **create**: URLs that can be used to create new resources. Used for the :meth:`~nap.resources.ResourceModel.create` method.
* **lookup**: URLs that can be used to retreive a single resource. Used for the :meth:`~nap.resources.ResourceModel.get` method when using keyword arguments.
* **update**: URLs that can be used to create update an existing resource. Used for the :meth:`~nap.resources.ResourceModel.update` method.
* **collection**: URLs that can be used to retrieve collections of resources. Used for the :meth:`~nap.resources.ResourceModel.filter` and :meth:`~nap.resources.ResourceModel.all` methods.

Valid URL Strings
-----------------

A URL string is simply a python string, optionally containing dictionary-format variables. nap bases it's required variables partially on any format variables contained in the URL string.


URL Variables
-------------



URL API
=======

.. class:: LookupURL

.. method:: LookupURL.__init__(url_string, params=None, create=None, update=None, lookup=None, collection=None)

.. attribute:: LookupURL.url_parts

.. attribute:: LookupURL.required_vars

.. method:: LookupURL.match(**kwargs)
