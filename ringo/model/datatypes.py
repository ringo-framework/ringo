import sqlalchemy as sa
import json


class Json(sa.TypeDecorator):
    """Json Datatype is used to implement a field which can store more
    that one value in a single field. This can typically be used to
    store checkboxes or other fields which can have multiple values."""

    impl = sa.String

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
