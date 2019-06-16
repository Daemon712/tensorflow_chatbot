"""empty message

Revision ID: 90d07d8c385d
Revises: 
Create Date: 2019-06-15 22:03:53.018125

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90d07d8c385d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chat',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_timestamp'), 'chat', ['timestamp'], unique=False)
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('author', sa.Integer(), nullable=True),
    sa.Column('text', sa.String(length=512), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('chat_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['chat_id'], ['chat.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message')
    op.drop_index(op.f('ix_chat_timestamp'), table_name='chat')
    op.drop_table('chat')
    # ### end Alembic commands ###