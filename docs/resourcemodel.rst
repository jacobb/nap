=================
ResourceModel API
=================

.. module:: nap.resources

The ResourceModel is the main component to interaction with nap. While not intereacted with directly, subclasses of nap provide the functionality needed to working with APIs. Because of this, ResourceModel is designed to have as many hooks as possible to tweak the functionality of it's primary method calls.


.. autoclass:: ResourceModel
    :members: get, create, update, filter, all, handle_create_response, handle_update_response, serialize, deserialize, to_python, full_url, resource_id