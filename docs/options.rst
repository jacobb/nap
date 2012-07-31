=======
Options
=======


``resource_name``
=================

*Optional*

The name used to refer to a source in URLs. ``resource_name`` is appended to ``root_url`` to create the default url set.

**Defaults to:** ResourceModel's class name, in all lower case. eg::

    class FooBar(ResourceModel):
        # fields here..
        # resource_name is `foobar`


``root_url``
============

*Optional*

**Defaults to:** ``None``


.. _urls:

``urls``
========

*Optional*

URLs used to lookup API requests. See :doc:`urls` for more information on definging ResourceModel urls.

**Defaults to:** A tuple of urls set to::

    (
        nap_url('%(resource_name)s/',
            create=True,
            lookup=False,
            collection=True
        ),
        nap_url('%(resource_name)s/%(resource_id)s', update=True),
    )


.. _append_urls:

``append_urls``
===============

*Optional*

URLs to be added after ResourceModel's default_urls. See :doc:`urls` for more information on definging ResourceModel urls.

**Defaults to:** () (an empty tuple)


.. _prepend_urls:

``prepend_urls``
================

*Optional*

URLs to be added before ResourceModel's default_urls. See :doc:`urls` for more information on definging ResourceModel urls.

**Defaults to:** () (an empty tuple)



``add_slash``
=============

*Optional*

Determines whehter or not slashes are appended to a url.

* If ``True``, slashes will always be added to the end of URLs.
* If ``False``, slashes will always be removed from the end of URLs
* If ``None``, URLs will follow what is defined in the ``nap_url`` string.

**Defaults to:** ``None``


``update_from_write``
=====================

*Optional*

Determines whether or not nap attempts to change an object's field data based on the HTTP content of create and update requests.

**Defaults to:** ``True``

``update_method``
=================

*Optional*

String representing HTTP method used to update (edit) resource objects.

**Defaults to:** "PUT"

``auth``
=========

Iterable of authorization classes. See :doc:auth for more information on Authorization classes.

**Defaults to:** () (an empty tuple)
