====
URLs
====

Proper URL patterns are the backbone of a ResourceModel. URLs are defined in a ResourceModel as a tuple of ``nap_urls``--a thin wrapper around a python-formatted string. These are defined and tied to a ResourceModel through the :ref:`urls`, :ref:`prepend_urls`, and :ref:`append_urls`.

By default, ResourceModels have two nap_urls that allow them to make all common calls to a to-spec REST API::

    nap_url('%(resource_name)s/', create=True, lookup=False, collection=True),
    nap_url('%(resource_name)s/%(resource_id)s', update=True),


How a URL Lookup works
======================



URL API
=======