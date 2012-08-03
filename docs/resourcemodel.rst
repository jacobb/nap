=================
ResourceModel API
=================

.. module:: nap.resources

The ResourceModel is the main component to interaction with nap. While not intereacted with directly, subclasses of nap provide the functionality needed to working with APIs. Because of this, ResourceModel is designed to have as many hooks as possible to tweak the functionality of it's primary method calls.

Fields
======

Main article: :doc:`fields`

Each field is a one-to-one mapping with a attribute returned in your API's response. It handles any validation and coerition (*scrubbing*) necessary to turn the API data into Python (and back to an API data string again). Special fields can be used to group API data into sub-collections of ResourceModels.

Lookup URLs
===========

Main article: :doc:`urls`

LookupURLs power the main engine of nap. By defining dynamic URLs, API get/create/update operations can be issued without specifying a raw URL, and instead the necessary data to complete the operation.

How LookupURLs work and


Options
=======

Main article: :doc:`options`


API
===

.. autoclass:: ResourceModel
    :members: get, refresh, create, update, filter, all, handle_create_response, handle_update_response, serialize, deserialize, to_python, full_url, resource_id