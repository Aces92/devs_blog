"""add post search vector

Revision ID: ce86e04d5837
Revises: 5ac645afc73e
Create Date: 2026-08-17 11:27:39.325150

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ce86e04d5837'
down_revision: Union[str, Sequence[str], None] = '5ac645afc73e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "posts",
        sa.Column(
            "search_vector",
            postgresql.TSVECTOR(),
            sa.Computed(
                "to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''))",
                persisted=True,
            ),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_posts_search_vector",
        "posts",
        ["search_vector"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("ix_posts_search_vector", table_name="posts")
    op.drop_column("posts", "search_vector")