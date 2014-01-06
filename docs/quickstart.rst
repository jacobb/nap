==========
Quickstart
==========


Step One: Declare your resource
===============================


..  code-block:: python

    # note/client.py
    from nap.resources import ResourceModel, Field


    class Note(ResourceModel):

        pk = Field(api_name='id', resource_id=True)
        title = Field()
        content = Field()

        class Meta:
            root_url = 'http://127.0.0.1:8000/api/'
            resource_name = 'note'


Step Two: Access your api
==========================

.. code-block:: python

    from note.client import Note

    n = Note(title='Some Title', content="some content")

    # POST http://127.0.0.1:8000/api/note/
    n.save()

    n = Note.objects.get('note/1/')
    # Some Title
    n.title

    # GET http://127.0.0.1:8000/api/note/1/
    n = Note.objects.lookup(pk=1)
    n.title = "New Title"
    n.content = "I sure do love butterflies"

    # PUT http://127.0.0.1:8000/api/note/1/
    n.save()

    n = Note.objects.get('note/1/')
    # "New Title"
    n.title


Step Three: Set up custom lookup_urls
=====================================

.. code-block:: python

    from nap.resources import ResourceModel, Field
    from nap.lookup import nap_url

    class Note(ResourceModel):

        pk = Field(api_name='id', resource_id=True)
        title = Field()
        content = Field()

        class Meta:
            root_url = 'http://127.0.0.1:8000/api/'
            resource_name = 'note'
            additional_urls = (
                nap_url(r'%(resource_name)s/title/%(title)s/'),
            )

    # GET http://127.0.0.1:8000/api/note/title/butterflies/
    n = Note.objects.lookup(title='New Title')
    # "I sure do love butterflies"
    n.content

Step Four: What's next?
=======================

* Learn more about tweaking :class:`~nap.resources.ResourceModel` by looking at :doc:`tutorial/tutorial1`
* :doc:`Learn about LookupURLs<urls>`, the glue between your resource and its API
* Look deeper into the core modules behind nap:
    *  :doc:`resourcemodel`, The Pythonic representation of your resource.
    *  :doc:`engine`, all the HTTP nuts-and-bolts powering nap.
