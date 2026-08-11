"""use uuid for user id

Revision ID: 4f6920408b80
Revises: 767008611fa6
Create Date: 2026-08-11 16:57:05.667778

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "4f6920408b80"
down_revision: Union[str, Sequence[str], None] = "767008611fa6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.drop_column("users", "id")

    op.add_column(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
    )

    op.alter_column(
        "users",
        "id",
        server_default=None,
    )

    op.create_primary_key(
        "users_pkey",
        "users",
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("users_pkey", "users", type_="primary")

    op.drop_column("users", "id")

    op.add_column(
        "users",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
    )

    op.create_primary_key(
        "users_pkey",
        "users",
        ["id"],
    )
