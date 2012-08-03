================
Tutorial: Part 1
================

In part one of our tutorial, we'll be creating a :class:`~ResourceModel` to interact with a simple Tastypie Django site. `Tastypie`_ is a third party Django app that makes creating to-spec REST APIs. Because of this, it's the perfect match to write our first :class:`~ResourceModel`, as it will require only a little fine tuning.

.. _Tastypie: http://tastypieapi.org/


Step 0: Writing our API
=======================

Our API will closely match the one inferred to in :doc:`../quickstart`. Feel free to write your own as you follow along with this tutorial, but if you'd like to just use ours, the source code is available `here <https://github.com/jacobb/example_nap_api/>`_

Step 1: Writing a basic ResourceModel
=====================================

Let's start by writing a very basic ResourceModel and going through it's parts::

    class Note(ResourceModel):

        title = Field(default='new title')
        content = Field()

        pk = Field(api_name='id', resource_id=True)

        class Meta:
            root_url = 'http://127.0.0.1:8000/api/v1/'
            resource_name = 'note'

We have a few things to note here:

* Two normal Fields, ``title`` and ``content``. On any lookup field nap does, these will simple load whatever value the API returns for attributes with the same names. If the fields are not present, the Note object will be loaded with their default value (a blank string by default, or 'new title' in the case of ``title``)
* A field ``pk`` with two special keyword arguments, ``api_name`` and ``resource_id``
    * ``api_name`` allows you to refer to a API variable by a different name on the object than what the API uses. In this case, a attribute on the API data called 'id' will be preferred to by a python attribute `pk`
    * ``resource_id`` designates this field as the primary identifier for the object. This is used in issuing API requests to URLs that require an id (such as the default URL for :meth:`~nap.resources.ResourceModel.update` and :meth:`~nap.resources.ResourceModel.update.get`). It is also used to help represent the object in it's :meth:`~nap.resources.ResourceModel.update.__unicode__` method.
* the Meta class. This is the primary way to tweak and configure your ResourceModel. This one is pretty sparse, and contains the two primary options of a Meta class:
    * ``root_url`` - This is a full base URL of your API. All requests to your API will be prefaced with this setting.
    * ``resource_name`` - The primary name of your resource class. This is used to construct all default URLs. For this class, this option is not necessary -- if left out of the Meta class, resource_name defaults to the name of the class in all lowercase -- but it never hurts to be explicit!

That's quite a lot! Feel free to quick through the in-links above to find out more about each option, but there's no need to dive in too deeply yet.

Step 2: Using your ResourceModel
================================

Our API is empty right now (assuming you haven't added data manually), so let's add a new Note::

    n = Note(title="A New Note!")
    n.content = "Daniel Lindsley rocks da house"
    n.save()

There! We've now created our first object in our API, and can retrieve it by it's id:

    n = Note(pk=1)
    print n.title  # "A New Note!"

Remember, since we used ``api_name`` on the pk Field in our :class:`~nap.resources.ResourceModel` definition, we use ``pk`` to look up a value that the API refers to as `id`

We can also update and save this resource::

    n.title = "Let's use a new title"
    n.save()

And a PUT is issues to our API, updating our record.

Note that we had to re-fetch our Note in order to properly have access to it's ``pk`` attribute. When we issued the create command, we weren't able to update our Note with information calculated by the API itself (such as it's ID, and created/updated timestamps). If we need to make many of these kind of creates and don't mind the cost of an extra request, refreshing the object after a create may be beneficial. Our next step will go into a few ways we can handle that.

Step 3: Finer customization
===========================

By default, Tastypie APIs respond to a POST request with 201 response with a Location header pointing to the new resource's URL. By default, nap will automatically set the value of the Location header as the Note object's full_url, so any further updates should work. However, because Tastypie by default does *not* return a serialized representation of the object, we can't get updated information without issuing a second GET request.

There are several ways we could address this:

* Set the Tastypie Resource Meta setting ``always_return_data`` to True. By default, if the 201 response after a create issues has content, Nap will attempt to update itself based on that content. However, since this is a nap tutorial and not a Tastypie tutorial, let's say we don't have access to change the API at hand.
* Manually Refresh the object. After saving the object, we could call :meth:`~nap.resources.ResourceModel.refresh`, which issues a GET request to update our fields based on what the API has. But this seems a little overly manual, no?
* Subclass and extend the :meth:`~nap.resources.ResourceModel.handle_create_response` method to automatically refresh after create if we have no content.

Not only does this sound like the best method, it also gives us an excuse to
show how easy it is to extend ResourceModel.

.. code-block:: python
    :emphasize-lines: 12-15

    class Note(ResourceModel):

        title = Field(default='new title')
        content = Field()

        pk = Field(api_name='id', resource_id=True)

        class Meta:
            root_url = 'http://127.0.0.1:8000/api/v1/'
            resource_name = 'note'

        def handle_create_response(self, response):
            super(Note, self).handle_create_response(response)
            if not response.content:
                self.refresh()
