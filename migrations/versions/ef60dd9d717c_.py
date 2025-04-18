"""empty message

Revision ID: ef60dd9d717c
Revises: 1259f00efb77
Create Date: 2025-04-07 12:54:35.014036

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef60dd9d717c'
down_revision: Union[str, None] = '1259f00efb77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('group_id', sa.UUID(), nullable=False))
    op.create_foreign_key(None, 'tasks', 'groups', ['group_id'], ['group_id'], ondelete='CASCADE')
    op.create_unique_constraint(None, 'users', ['username'])
    op.drop_constraint('users_groups_user_id_fkey', 'users_groups', type_='foreignkey')
    op.drop_constraint('users_groups_group_id_fkey', 'users_groups', type_='foreignkey')
    op.create_foreign_key(None, 'users_groups', 'users', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'users_groups', 'groups', ['group_id'], ['group_id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users_groups', type_='foreignkey')
    op.drop_constraint(None, 'users_groups', type_='foreignkey')
    op.create_foreign_key('users_groups_group_id_fkey', 'users_groups', 'groups', ['group_id'], ['group_id'])
    op.create_foreign_key('users_groups_user_id_fkey', 'users_groups', 'users', ['user_id'], ['user_id'])
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'group_id')
    # ### end Alembic commands ###
