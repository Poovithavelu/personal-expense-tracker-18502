from marshmallow import Schema, fields, validate


class CategoryCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))


class CategoryUpdateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))


class CategorySchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True)
    created_at = fields.DateTime(required=True)


class ExpenseCreateSchema(Schema):
    amount = fields.Decimal(as_string=True, required=True)
    category_id = fields.Int(allow_none=True)
    description = fields.Str(allow_none=True, validate=validate.Length(max=255))
    expense_date = fields.Date(required=True)


class ExpenseUpdateSchema(Schema):
    amount = fields.Decimal(as_string=True)
    category_id = fields.Int(allow_none=True)
    description = fields.Str(allow_none=True, validate=validate.Length(max=255))
    expense_date = fields.Date()


class ExpenseSchema(Schema):
    id = fields.Int(required=True)
    amount = fields.Decimal(as_string=True, required=True)
    category_id = fields.Int(allow_none=True)
    description = fields.Str(allow_none=True)
    expense_date = fields.Date(required=True)
    created_at = fields.DateTime(required=True)
