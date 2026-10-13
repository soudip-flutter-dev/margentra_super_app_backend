"""add refresh token rotation fields

Revision ID: 0001_refresh_rotation
Revises: 
Create Date: 2026-10-12
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_refresh_rotation"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("refresh_tokens", schema=None) as batch_op:
        batch_op.add_column(sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("replaced_by_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_refresh_tokens_replaced_by_id",
            "refresh_tokens",
            ["replaced_by_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("refresh_tokens", schema=None) as batch_op:
        batch_op.drop_constraint("fk_refresh_tokens_replaced_by_id", type_="foreignkey")
        batch_op.drop_column("replaced_by_id")
        batch_op.drop_column("revoked_at")
