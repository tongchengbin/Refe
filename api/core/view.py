from flask import request, Response
from flask.views import MethodViewType, View


def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""

    # This requires a bit of explanation: the basic idea is to make a
    # dummy metaclass for one level of class instantiation that replaces
    # itself with the actual metaclass.
    class metaclass(type):
        def __new__(metacls, name, this_bases, d):
            return meta(name, bases, d)

    return type.__new__(metaclass, "temporary_class", (), {})


class MethodView(with_metaclass(MethodViewType, View)):
    """A class-based view that dispatches request methods to the corresponding
    class methods. For example, if you implement a ``get`` method, it will be
    used to handle ``GET`` requests. ::

        class CounterAPI(MethodView):
            def get(self):
                return session.get('counter', 0)

            def post(self):
                session['counter'] = session.get('counter', 0) + 1
                return 'OK'

        app.add_url_rule('/counter', view_func=CounterAPI.as_view('counter'))
    """

    def __init__(self, *args, **kwargs) -> None:
        self.request = None
        super().__init__(*args, **kwargs)

    def dispatch_request(self, *args, **kwargs):
        self.request = request
        meth = getattr(self, request.method.lower(), None)

        # If the request method is HEAD and we don't have a handler for it
        # retry with GET.

        if meth is None and request.method == "HEAD":
            meth = getattr(self, "get", None)

        assert meth is not None, "Unimplemented method %r" % request.method
        return meth(*args, **kwargs)

    def response_ok(self):
        return Response({"status": 0, "data": {}})
