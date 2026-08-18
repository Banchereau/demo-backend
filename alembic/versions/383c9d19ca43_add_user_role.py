"""add user role

Revision ID: 383c9d19ca43
Revises: 4f6920408b80
Create Date: 2026-08-18 15:01:03.442242

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "383c9d19ca43"
down_revision: Union[str, Sequence[str], None] = "4f6920408b80"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


user_role = sa.Enum(
    "admin",
    "operator",
    "viewer",
    name="user_role",
)


def upgrade() -> None:
    user_role.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "users",
        sa.Column(
            "role",
            user_role,
            nullable=False,
            server_default="viewer",
        ),
    )

    op.alter_column(
        "users",
        "role",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column("users", "role")

    user_role.drop(op.get_bind(), checkfirst=True)
