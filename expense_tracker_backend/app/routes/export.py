import csv
import io
from datetime import date
from typing import Optional
from flask_smorest import Blueprint
from flask.views import MethodView
from webargs.flaskparser import use_kwargs
from marshmallow import fields
from flask import Response
from ..db import query

blp = Blueprint(
    "Export",
    "export",
    url_prefix="/export",
    description="Export expenses as CSV",
)


class ExportFilterSchema:
    start_date = fields.Date(required=False, description="Filter from this date (inclusive)")
    end_date = fields.Date(required=False, description="Filter until this date (inclusive)")
    category_id = fields.Int(required=False, description="Filter by category id")


@blp.route("/")
class ExportCSVResource(MethodView):
    @use_kwargs(ExportFilterSchema, location="query")
    def get(self, start_date: Optional[date] = None, end_date: Optional[date] = None, category_id: Optional[int] = None):
        """Export expenses to CSV with optional filters."""
        conditions = []
        params = []
        if start_date:
            conditions.append("e.expense_date >= %s")
            params.append(start_date)
        if end_date:
            conditions.append("e.expense_date <= %s")
            params.append(end_date)
        if category_id:
            conditions.append("e.category_id = %s")
            params.append(category_id)
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        rows = query(
            f"""
            SELECT e.id, e.amount, e.category_id, c.name AS category_name,
                   e.description, e.expense_date, e.created_at
            FROM expenses e
            LEFT JOIN categories c ON c.id = e.category_id
            {where}
            ORDER BY e.expense_date DESC, e.id DESC
            """,
            tuple(params),
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "amount", "category_id", "category_name", "description", "expense_date", "created_at"])
        for r in rows:
            writer.writerow([
                r.get("id"),
                r.get("amount"),
                r.get("category_id"),
                r.get("category_name"),
                r.get("description"),
                r.get("expense_date"),
                r.get("created_at"),
            ])

        csv_bytes = output.getvalue()
        output.close()

        return Response(
            csv_bytes,
            mimetype="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=expenses.csv"
            }
        )
