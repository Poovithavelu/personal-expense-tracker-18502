from datetime import date
from typing import Optional
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from webargs.flaskparser import use_kwargs
from marshmallow import fields
from ..db import query, execute
from ..schemas import ExpenseCreateSchema, ExpenseUpdateSchema, ExpenseSchema

blp = Blueprint(
    "Expenses",
    "expenses",
    url_prefix="/expenses",
    description="Manage expenses with CRUD operations and filtering",
)


class ExpenseFilterSchema:
    start_date = fields.Date(required=False, description="Filter expenses from this date (inclusive)")
    end_date = fields.Date(required=False, description="Filter expenses until this date (inclusive)")
    category_id = fields.Int(required=False, description="Filter by category id")


@blp.route("/")
class ExpenseListResource(MethodView):
    @use_kwargs(ExpenseFilterSchema, location="query")
    @blp.response(200, ExpenseSchema(many=True))
    def get(self, start_date: Optional[date] = None, end_date: Optional[date] = None, category_id: Optional[int] = None):
        """List expenses with optional filters."""
        conditions = []
        params = []
        if start_date:
            conditions.append("expense_date >= %s")
            params.append(start_date)
        if end_date:
            conditions.append("expense_date <= %s")
            params.append(end_date)
        if category_id:
            conditions.append("category_id = %s")
            params.append(category_id)
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        rows = query(
            f"""
            SELECT id, amount, category_id, description, expense_date, created_at
            FROM expenses
            {where}
            ORDER BY expense_date DESC, id DESC
            """,
            tuple(params),
        )
        return rows

    @use_kwargs(ExpenseCreateSchema, location="json")
    @blp.response(201, ExpenseSchema)
    def post(self, amount, expense_date, category_id=None, description=None):
        """Create a new expense."""
        try:
            new_id = execute(
                "INSERT INTO expenses (amount, category_id, description, expense_date) VALUES (%s, %s, %s, %s)",
                (amount, category_id, description, expense_date),
            )
        except Exception:
            abort(400, message="Failed to create expense")
        row = query(
            "SELECT id, amount, category_id, description, expense_date, created_at FROM expenses WHERE id=%s",
            (new_id,),
        )
        if not row:
            abort(500, message="Expense creation failed")
        return row[0]


@blp.route("/<int:expense_id>")
class ExpenseResource(MethodView):
    @blp.response(200, ExpenseSchema)
    def get(self, expense_id: int):
        """Get expense by id."""
        rows = query(
            "SELECT id, amount, category_id, description, expense_date, created_at FROM expenses WHERE id=%s",
            (expense_id,),
        )
        if not rows:
            abort(404, message="Expense not found")
        return rows[0]

    @use_kwargs(ExpenseUpdateSchema, location="json")
    @blp.response(200, ExpenseSchema)
    def put(self, expense_id: int, **updates):
        """Update an expense. Only provided fields will be updated."""
        if not updates:
            rows = query(
                "SELECT id, amount, category_id, description, expense_date, created_at FROM expenses WHERE id=%s",
                (expense_id,),
            )
            if not rows:
                abort(404, message="Expense not found")
            return rows[0]

        set_parts = []
        params = []
        for key in ("amount", "category_id", "description", "expense_date"):
            if key in updates and updates[key] is not None:
                set_parts.append(f"{key}=%s")
                params.append(updates[key])
        if not set_parts:
            abort(400, message="No valid fields to update")

        params.append(expense_id)
        affected = execute(f"UPDATE expenses SET {', '.join(set_parts)} WHERE id=%s", tuple(params))
        if affected == 0:
            abort(404, message="Expense not found")

        rows = query(
            "SELECT id, amount, category_id, description, expense_date, created_at FROM expenses WHERE id=%s",
            (expense_id,),
        )
        return rows[0]

    @blp.response(204)
    def delete(self, expense_id: int):
        """Delete an expense."""
        execute("DELETE FROM expenses WHERE id=%s", (expense_id,))
        return ""
