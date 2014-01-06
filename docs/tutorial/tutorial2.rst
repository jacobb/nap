================
Tutorial: Part 2
================

Writing clients against Tastypie APIs give a couple advantages. Not only do we usually have direct access to the API itself to make changes that would be better suited on the API side.

Writing a REST client against a third party site can be a more challenging affair. Sites may make slight changes to the REST spec for convenience (or random) reasons. Getting our LookupURL engine to be able to successfully talk to them will require some adjustments.

Github exposes a very open API to most of it's resources. Since it's `gists`_ product is a fairly simple model, let's use that for this example. Docs on the API itself can be found `here`_.

.. _gists: https://gist.github.com/
.. _here: http://developer.github.com/v3/gists/

Let's get started.


Step 1: Basic Setup
===================

Let's start by applying what we learned in :doc:`Part 1<tutorial1>` to a Gist. Let's only include the key fields right now--there's no need to include everything an API returns to us. To create a gist, we usually need three fields -- its description and files, and whether or not it's public or not. Let's also add a html_url field so we can check any new Gists we make easily:

.. code-block:: python

    import nap
    from nap.auth import FoauthAuthorization
    from nap.lookup import nap_url


    class Gist(nap.ResourceModel):
        id = nap.Field(resource_id=True)

        description = nap.Field()
        public = nap.Field()
        files = nap.Field()

        html_url = nap.Field()


        class Meta:
            resource_name = 'gists'
            root_url = 'https://api.github.com/'

Immediately we see one difference from our Tastypie example. While we could have left off the :ref:`resource_name` for our ``Note`` class, the Github API uses a plural forum in their URLs. Becuase of this, seting resource_name to 'gists' is required.

Let's try using this by grabbing a `example gist`_::

    >>> g = Gist.objects.get(id='3256061')
    Traceback (most recent call last):
    # ...
    ValueError: Expected status code in (200,), got 404

.. _example gist: https://gist.github.com/3256061

Well, that's not good! Diving into the gist API docs, we see that Github's API URLs do *not* include a trailing slash, as our default URLs do. This is a fairly common API spec, and we can accommodate this by setting the Meta option :ref:`add_slash` to False.

.. code-block:: python
    :emphasize-lines: 14

    class Gist(nap.ResourceModel):
        id = nap.Field(resource_id=True)

        description = nap.Field()
        public = nap.Field()
        files = nap.Field()

        html_url = nap.Field()

        class Meta:
            resource_name = 'gists'
            root_url = 'https://api.github.com/'
            add_slash = False

Let's give that a try::

    >>> g = Gist.objects.get(id='3256061')
    >>> print g.description  # "Nap Example"

That's better!

Now would be a good time to show off the ``extra_data`` attribute available on ResourceModels. Our ``Gist`` class contains only a few fields that the API returns. By default, anything returned by the API that has no corresponding field gets thrown into the ``extra_data`` dictionary on an object::

    >>> g.extra_data
    # {u'created_at': u'2012-08-04T08:41:32Z', u'updated_at': u'2012-08-04T08:41:32Z' ... }

This is useful if you only need to grab data in a rare case, or want to introspect the data being returned to you by an API.


Step 2: Authentication
======================

Let's see how creating goes. A gist requires only a files dictionary to be created::

    >>> g = Gist(files={'x.txt': {'content': 'hello world'}})
    >>> g.save()
    >>> g.html_url  # A gist url

If we load up that URL, we see that everything seems keen, but the gist we made is made by Anonymous. Not only does this deprive of us of the fame and glory that comes from such a poetic gist, it also forbids us from ever updating it again. Since updating is a key feature of nap, let's add some authentication information. Github has two ways to authenticate -- HTTP basic auth and Oauth. To keep things (much) simpler, let's just use HTTP Auth for now. In the example below, replace the username and password arguments with your own Github username and password.

.. code-block:: python
    :emphasize-lines: 15-20

    class Gist(nap.ResourceModel):
        id = nap.Field(resource_id=True)

        description = nap.Field()
        public = nap.Field()
        files = nap.Field()

        html_url = nap.Field()

        class Meta:
            resource_name = 'gists'
            root_url = 'https://api.github.com/'
            add_slash = False
            auth = (
                nap.auth.HttpAuthorization(
                    username="YOUR USERNAME",
                    password="YOUR PASSWORD"),
            )

the :ref:`auth` Meta option is a tuple of Auth middlewares to apply to nap calls right before the request is made. :class:`HttpAuthorization` applies basic HTTP auth to all requests made by nap. In case you need multiple forms of authentication, you can chain multiple Authorization backends in this setting. For more information on authorization in nap, see :doc:`../auth`

Let's try that same Creation, but using our new auth backend::

    >>> g = Gist(files={'x.txt': {'content': 'hello world'}})
    >>> g.save()
    >>> g.html_url  # a new gist url

(assuming you put your correct credentials in) Success!

Now that we have an authenticating model and a Gist, let's try adding a description to it.::

    >>> g.save()
    ValueError: Invalid Update Response: expected stauts_code in (204,), got 404

Well that's the pits. Reading more into the docs on Editing a gist, there's two notable differences between nap's defaults and the Gist API.

#) The HTTP Method PATCH is used instead of PUT
#) The valid response code is 200, not 204

Both of these cases are handled by Meta options. Let's add them.

.. code-block:: python
    :emphasize-lines: 21-22

    class Gist(nap.ResourceModel):
        id = nap.Field(resource_id=True)

        description = nap.Field()
        public = nap.Field()
        files = nap.Field()

        html_url = nap.Field()

        class Meta:
            resource_name = 'gists'
            root_url = 'https://api.github.com/'
            add_slash = False
            auth = (
                nap.auth.HttpAuthorization(
                    username="YOUR USERNAME",
                    password="YOUR PASSWORD"),
            )
            update_method = 'PATCH'
            valid_update_status = (204, 200)


Now let's fetch our Gist using a get, and try editing it again::

    >>> g = Gist.objects.get(id='USE_YOUR_GIST_ID_HERE')
    >>> g.description = 'new description'
    >>> g.save()

Loading up the gist's html_url, we see our new description is up!


Final Gist Model
================

.. code-block:: python

    import nap
    from nap.auth import FoauthAuthorization
    from nap.lookup import nap_url

    import secret


    class GistFile(nap.ResourceModel):
        content = nap.Field()

        size = nap.Field(readonly=True)
        raw_url = nap.Field(readonly=True)

        class Meta:
            root_url = 'https://api.github.com/gists'


    class Gist(nap.ResourceModel):
        id = nap.Field(resource_id=True)

        description = nap.Field()
        public = nap.Field()
        files = nap.DictField(GistFile)

        url = nap.Field(readonly=True)
        user = nap.Field(readonly=True)
        html_url = nap.Field(readonly=True)

        class Meta:
            resource_name = 'gists'
            root_url = 'https://api.github.com/'
            add_slash = False
            update_method = 'PATCH'
            prepend_urls = (
                # For accessing /gists/starred and /gists/public, eg.
                # Gist.objects.filter(property='starred')
                nap_url('%(resource_name)s/%(property)s', collection=True, lookup=False),
            )
            auth = (
                FoauthAuthorization(secret.foauth_email, secret.foauth_password),
            )
