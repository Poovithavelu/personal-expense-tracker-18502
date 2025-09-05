from flask import Flask
from flask_cors import CORS
from flask_smorest import Api
from .routes.health import blp as health_blp
from .routes.categories import blp as categories_blp
from .routes.expenses import blp as expenses_blp
from .routes.export import blp as export_blp
from .db import init_schema

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app, resources={r"/*": {"origins": "*"}})

# OpenAPI/Swagger configuration
app.config["API_TITLE"] = "Expense Tracker API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

api = Api(app)

# Ensure DB schema exists at app import time
try:
    init_schema()
except Exception:
    # If DB is not reachable at startup, it will raise; we avoid crashing the app
    # to allow health checks; routes will still fail gracefully until DB is up.
    pass

# Register blueprints
api.register_blueprint(health_blp)
api.register_blueprint(categories_blp)
api.register_blueprint(expenses_blp)
api.register_blueprint(export_blp)
