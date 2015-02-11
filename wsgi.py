def app(env, start_response):
    import os
    from werkzeug.wsgi import peek_path_info
    from app.app import App
    from app import config
    _app = App()
    if peek_path_info(env) == "healthcheck":
        _app.config['SERVER_NAME'] = None
    else:
        _app.config['SERVER_NAME'] = config.SERVER_NAME

    return _app(env, start_response)
