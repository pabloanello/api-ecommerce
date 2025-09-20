"""
Revision ID: 0001_init
Revises: 
Create Date: 2025-09-18
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Integer(), default=1),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_table('products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(), index=True),
        sa.Column('description', sa.Text()),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('inventory', sa.Integer(), default=0),
    )
    op.create_table('orders',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'completed', 'cancelled', name='orderstatus'), default='pending'),
    )
    op.create_table('order_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id')),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id')),
        sa.Column('quantity', sa.Integer(), default=1),
    )
    op.create_table('carts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_table('cart_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('cart_id', sa.Integer(), sa.ForeignKey('carts.id')),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id')),
        sa.Column('quantity', sa.Integer(), default=1),
    )

def downgrade():
    op.drop_table('cart_items')
    op.drop_table('carts')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('products')
    op.drop_table('users')
