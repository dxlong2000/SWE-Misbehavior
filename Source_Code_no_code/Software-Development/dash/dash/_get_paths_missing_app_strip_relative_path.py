from ._utils import AttributeDict
from . import exceptions

CONFIG = AttributeDict()


def get_asset_url(path):
    return app_get_asset_url(CONFIG, path)


def app_get_asset_url(config, path):
    if config.assets_external_path:
        prefix = config.assets_external_path
    else:
        prefix = config.requests_pathname_prefix
    return "/".join(
        [
            # Only take the first part of the pathname
            prefix.rstrip("/"),
            config.assets_url_path.lstrip("/"),
            path,
        ]
    )


def get_relative_path(path):
    """
    Return a path with `requests_pathname_prefix` prefixed before it.
    Use this function when specifying local URL paths that will work
    in environments regardless of what `requests_pathname_prefix` is.
    In some deployment environments, like Dash Enterprise,
    `requests_pathname_prefix` is set to the application name,
    e.g. `my-dash-app`.
    When working locally, `requests_pathname_prefix` might be unset and
    so a relative URL like `/page-2` can just be `/page-2`.
    However, when the app is deployed to a URL like `/my-dash-app`, then
    `dash.get_relative_path('/page-2')` will return `/my-dash-app/page-2`.
    This can be used as an alternative to `get_asset_url` as well with
    `dash.get_relative_path('/assets/logo.png')`

    Use this function with `dash.strip_relative_path` in callbacks that
    deal with `dcc.Location` `pathname` routing.
    That is, your usage may look like:
    ```
    app.layout = html.Div([
        dcc.Location(id='url'),
        html.Div(id='content')
    ])
    @dash.callback(Output('content', 'children'), [Input('url', 'pathname')])
    def display_content(path):
        page_name = dash.strip_relative_path(path)
        if not page_name:  # None or ''
            return html.Div([
                dcc.Link(href=dash.get_relative_path('/page-1')),
                dcc.Link(href=dash.get_relative_path('/page-2')),
            ])
        elif page_name == 'page-1':
            return chapters.page_1
        if page_name == "page-2":
            return chapters.page_2
    ```
    """
    return app_get_relative_path(CONFIG.requests_pathname_prefix, path)


def app_get_relative_path(requests_pathname, path):
    if requests_pathname == "/" and path == "":
        return "/"
    if requests_pathname != "/" and path == "":
        return requests_pathname
    if not path.startswith("/"):
        raise exceptions.UnsupportedRelativePath(
            f"""
            Paths that aren't prefixed with a leading / are not supported.
            You supplied: {path}
            """
        )
    return "/".join([requests_pathname.rstrip("/"), path.lstrip("/")])


def strip_relative_path(path):
    """
    Return a path with `requests_pathname_prefix` and leading and trailing
    slashes stripped from it. Also, if None is passed in, None is returned.
    Use this function with `get_relative_path` in callbacks that deal
    with `dcc.Location` `pathname` routing.
    That is, your usage may look like:
    ```
    app.layout = html.Div([
        dcc.Location(id='url'),
        html.Div(id='content')
    ])
    @dash.callback(Output('content', 'children'), [Input('url', 'pathname')])
    def display_content(path):
        page_name = dash.strip_relative_path(path)
        if not page_name:  # None or ''
            return html.Div([
                dcc.Link(href=dash.get_relative_path('/page-1')),
                dcc.Link(href=dash.get_relative_path('/page-2')),
            ])
        elif page_name == 'page-1':
            return chapters.page_1
        if page_name == "page-2":
            return chapters.page_2
    ```
    Note that `chapters.page_1` will be served if the user visits `/page-1`
    _or_ `/page-1/` since `strip_relative_path` removes the trailing slash.

    Also note that `strip_relative_path` is compatible with
    `get_relative_path` in environments where `requests_pathname_prefix` set.
    In some deployment environments, like Dash Enterprise,
    `requests_pathname_prefix` is set to the application name, e.g. `my-dash-app`.
    When working locally, `requests_pathname_prefix` might be unset and
    so a relative URL like `/page-2` can just be `/page-2`.
    However, when the app is deployed to a URL like `/my-dash-app`, then
    `dash.get_relative_path('/page-2')` will return `/my-dash-app/page-2`

    The `pathname` property of `dcc.Location` will return '`/my-dash-app/page-2`'
    to the callback.
    In this case, `dash.strip_relative_path('/my-dash-app/page-2')`
    will return `'page-2'`

    For nested URLs, slashes are still included:
    `dash.strip_relative_path('/page-1/sub-page-1/')` will return
    `page-1/sub-page-1`
    ```
    """
    return app_strip_relative_path(CONFIG.requests_pathname_prefix, path)


def app_strip_relative_path(requests_pathname, path):
    """This function strips the relative path from the given path based on the pathname of requests. It checks if the pathname of requests not equal "/" and the path don't start with the requests_pathname processed by rstrip with "/" before and removes it if it does. It also handles the case where the requests_pathname has a trailing slash and the path does not.
    Input-Output Arguments
    :param requests_pathname: String. The pathname from the request URL.
    :param path: String. The path to be stripped.
    :return: String. The stripped path.
    """