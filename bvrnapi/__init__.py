import os
import tempfile

from flask import Flask, jsonify
from multiexit import install, register

from bvrnapi.api_spec import spec
from bvrnapi.cache import cache
from bvrnapi.endpoints.associations import associations_bp
from bvrnapi.endpoints.swagger import SWAGGER_URL, swagger_ui_blueprint


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    install()
    cache_dir = tempfile.TemporaryDirectory()
    register(cache_dir.cleanup)
    print("Cache Directory: {}".format(cache_dir.name))

    app.config.from_mapping(
        SECRET_KEY="dev",
        CACHE_TYPE="filesystem",
        CACHE_DIR=cache_dir.name,
    )
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    cache.init_app(app)

    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

    # TODO: url_prefix should NOT contain /api/v1, but otherwise routing is not working
    app.register_blueprint(associations_bp, url_prefix="/api/v1/associations")

    # register all swagger documented functions here
    with app.test_request_context():
        for fn_name in app.view_functions:
            if fn_name == "static":
                continue
            print(f"Loading swagger docs for function: {fn_name}")
            view_fn = app.view_functions[fn_name]
            spec.path(view=view_fn)

    @app.route("/api/swagger.json")
    def create_swagger_spec():
        """
        Swagger API definition.
        """
        return jsonify(spec.to_dict())

    return app
