===
nap
===

api access modeling and tools

Step One: Declare your resource
===============================


..  code-block:: python

    # note/client.py
    from nap.resources import RemoteModel, Field


    class Note(RemoteModel):

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

    n = Note.get('note/1/')
    # Some Title
    n.title

    # GET http://127.0.0.1:8000/api/note/1/
    n = Note.lookup(pk=1)
    n.title = "butterflies"
    n.content = "I sure do love butterflies"
    # PUT http://127.0.0.1:8000/api/note/1/
    n.save()

    n = Note.get('note/1/')
    n.title
    # "New Title"

Step Three: Set up custom lookup_urls
=====================================

.. code-block:: python
    :emphasize-lines: 2, 13-15

    from nap.resources import RemoteModel, Field
    from nap.lookup import nap_url

    class Note(RemoteModel):

        pk = Field(api_name='id', resource_id=True)
        title = Field()
        content = Field()

        class Meta:
            root_url = 'http://127.0.0.1:8000/api/'
            resource_name = 'note'
            additional_urls = (
                nap_url(r'%(resource_name)s/title/(?P<title>[^/]+)/'),
            )

    # GET http://127.0.0.1:8000/api/note/title/butterflies/
    n = Note.lookup(title='butterflies')
    # "I sure do love butterflies"
    n.content

Step Four
=========

Coming soon...