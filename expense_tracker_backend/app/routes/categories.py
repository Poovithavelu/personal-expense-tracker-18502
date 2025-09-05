from flask_smorest import Blueprint, abort
from flask.views import MethodView
from webargs.flaskparser import use_kwargs
from ..db import query, execute
from ..schemas import CategoryCreateSchema, CategoryUpdateSchema, CategorySchema

blp = Blueprint(
    "Categories",
    "categories",
    url_prefix="/categories",
    description="Manage categories for expenses",
)


@blp.route("/")
class CategoryListResource(MethodView):
    @blp.response(200, CategorySchema(many=True))
    def get(self):
        """List all categories."""
        rows = query("SELECT id, name, created_at FROM categories ORDER BY name ASC")
        return rows

    @use_kwargs(CategoryCreateSchema, location="json")
    @blp.response(201, CategorySchema)
    def post(self, name: str):
        """Create a new category."""
        try:
            new_id = execute("INSERT INTO categories (name) VALUES (%s)", (name,))
        except Exception:
            abort(400, message="Failed to create category. It may already exist.")
        row = query("SELECT id, name, created_at FROM categories WHERE id=%s", (new_id,))
        if not row:
            abort(500, message="Category creation failed")
        return row[0]


@blp.route("/<int:category_id>")
class CategoryResource(MethodView):
    @blp.response(200, CategorySchema)
    def get(self, category_id: int):
        """Get a single category by ID."""
        rows = query(
            "SELECT id, name, created_at FROM categories WHERE id=%s", (category_id,)
        )
        if not rows:
            abort(404, message="Category not found")
        return rows[0]

    @use_kwargs(CategoryUpdateSchema, location="json")
    @blp.response(200, CategorySchema)
    def put(self, category_id: int, name: str):
        """Update category name."""
        affected = execute("UPDATE categories SET name=%s WHERE id=%s", (name, category_id))
        if affected == 0:
            abort(404, message="Category not found")
        rows = query(
            "SELECT id, name, created_at FROM categories WHERE id=%s", (category_id,)
        )
        return rows[0]

    @blp.response(204)
    def delete(self, category_id: int):
        """Delete a category."""
        execute("DELETE FROM categories WHERE id=%s", (category_id,))
        return ""
