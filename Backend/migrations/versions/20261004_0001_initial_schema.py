"""initial schema

Status/role columns are VARCHARs guarded by CHECK constraints (not native enums),
so adding a value later is a simple constraint change.

Revision ID: 0001
Revises: 
Create Date: 2026-10-04 22:53:27.875998
"""
from alembic import op
import sqlalchemy as sa


revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

# Back Repository.next_id(); listed literally so this migration never changes with the code.
ID_SEQUENCES = (
    "user_id_seq",
    "supplier_id_seq",
    "product_id_seq",
    "inventory_id_seq",
    "sales_order_id_seq",
    "purchase_order_id_seq",
    "approval_id_seq",
    "audit_log_id_seq",
)


def upgrade() -> None:
    op.create_table('audit_logs',
    sa.Column('id', sa.String(length=16), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.String(length=16), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('action', sa.String(length=64), nullable=False),
    sa.Column('entity', sa.String(length=64), nullable=False),
    sa.Column('entity_id', sa.String(length=32), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.CheckConstraint("status IN ('SUCCESS', 'FAILED')", name=op.f('ck_audit_logs_status')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_audit_logs'))
    )
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_timestamp'), 'audit_logs', ['timestamp'], unique=False)
    op.create_table('suppliers',
    sa.Column('id', sa.String(length=16), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('contact_name', sa.String(length=120), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('phone', sa.String(length=40), nullable=False),
    sa.Column('country', sa.String(length=80), nullable=False),
    sa.Column('avg_delivery_days', sa.Float(), nullable=False),
    sa.Column('delivery_reliability', sa.Float(), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.CheckConstraint("status IN ('Active', 'Inactive')", name=op.f('ck_suppliers_status')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_suppliers'))
    )
    op.create_table('users',
    sa.Column('id', sa.String(length=16), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('full_name', sa.String(length=120), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('role', sa.String(length=32), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.CheckConstraint("role IN ('ADMIN', 'INVENTORY_MANAGER', 'PROCUREMENT_MANAGER', 'EMPLOYEE')", name=op.f('ck_users_role')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('username', name=op.f('uq_users_username'))
    )
    op.create_table('products',
    sa.Column('id', sa.String(length=16), nullable=False),
    sa.Column('sku', sa.String(length=40), nullable=False),
    sa.Column('name', sa.String(length=160), nullable=False),
    sa.Column('category', sa.String(length=80), nullable=False),
    sa.Column('supplier_id', sa.String(length=16), nullable=False),
    sa.Column('price', sa.Numeric(precision=12, scale=2, asdecimal=False), nullable=False),
    sa.Column('unit_cost', sa.Numeric(precision=12, scale=2, asdecimal=False), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.CheckConstraint("status IN ('Active', 'Discontinued')", name=op.f('ck_products_status')),
    sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], name=op.f('fk_products_supplier_id_suppliers')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_products')),
    sa.UniqueConstraint('sku', name=op.f('uq_products_sku'))
    )
    op.create_index(op.f('ix_products_category'), 'products', ['category'], unique=False)
    op.create_index(op.f('ix_products_supplier_id'), 'products', ['supplier_id'], unique=False)
    op.create_table('inventory',
    sa.Column('id', sa.String(length=16), nullable=False),
    sa.Column('product_id', sa.String(length=16), nullable=False),
    sa.Column('warehouse', sa.String(length=80), nullable=False),
    sa.Column('current_stock', sa.Integer(), nullable=False),
    sa.Column('safety_stock', sa.Integer(), nullable=False),
    sa.Column('reorder_level', sa.Integer(), nullable=False),
    sa.Column('last_updated', sa.Date(), nullable=False),
    sa.CheckConstraint('current_stock >= 0', name=op.f('ck_inventory_current_stock_non_negative')),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], name=op.f('fk_inventory_product_id_products')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_inventory'))
    )
    op.create_index(op.f('ix_inventory_product_id'), 'inventory', ['product_id'], unique=False)
    op.create_table('purchase_orders',
    sa.Column('id', sa.String(length=16), nullable=False),
    sa.Column('supplier_id', sa.String(length=16), nullable=False),
    sa.Column('product_id', sa.String(length=16), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('unit_price', sa.Numeric(precision=12, scale=2, asdecimal=False), nullable=False),
    sa.Column('order_date', sa.Date(), nullable=False),
    sa.Column('expected_delivery', sa.Date(), nullable=False),
    sa.Column('actual_delivery', sa.Date(), nullable=True),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('reason', sa.String(length=500), nullable=False),
    sa.Column('created_by', sa.String(length=64), nullable=False),
    sa.CheckConstraint("status IN ('Draft', 'Pending Approval', 'Approved', 'Rejected', 'Ordered', 'Delivered', 'Cancelled')", name=op.f('ck_purchase_orders_status')),
    sa.CheckConstraint('quantity > 0', name=op.f('ck_purchase_orders_quantity_positive')),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], name=op.f('fk_purchase_orders_product_id_products')),
    sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], name=op.f('fk_purchase_orders_supplier_id_suppliers')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_purchase_orders'))
    )
    op.create_index(op.f('ix_purchase_orders_product_id'), 'purchase_orders', ['product_id'], unique=False)
    op.create_index(op.f('ix_purchase_orders_status'), 'purchase_orders', ['status'], unique=False)
    op.create_index(op.f('ix_purchase_orders_supplier_id'), 'purchase_orders', ['supplier_id'], unique=False)
    op.create_table('sales_orders',
    sa.Column('id', sa.String(length=16), nullable=False),
    sa.Column('customer', sa.String(length=160), nullable=False),
    sa.Column('product_id', sa.String(length=16), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('unit_price', sa.Numeric(precision=12, scale=2, asdecimal=False), nullable=False),
    sa.Column('order_date', sa.Date(), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.CheckConstraint("status IN ('Pending', 'Processing', 'Completed', 'Cancelled')", name=op.f('ck_sales_orders_status')),
    sa.CheckConstraint('quantity > 0', name=op.f('ck_sales_orders_quantity_positive')),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], name=op.f('fk_sales_orders_product_id_products')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_sales_orders'))
    )
    op.create_index(op.f('ix_sales_orders_order_date'), 'sales_orders', ['order_date'], unique=False)
    op.create_index(op.f('ix_sales_orders_product_id'), 'sales_orders', ['product_id'], unique=False)
    op.create_table('supplier_products',
    sa.Column('supplier_id', sa.String(length=16), nullable=False),
    sa.Column('product_id', sa.String(length=16), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], name=op.f('fk_supplier_products_product_id_products'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], name=op.f('fk_supplier_products_supplier_id_suppliers'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('supplier_id', 'product_id', name=op.f('pk_supplier_products'))
    )
    op.create_table('approvals',
    sa.Column('id', sa.String(length=16), nullable=False),
    sa.Column('purchase_order_id', sa.String(length=16), nullable=False),
    sa.Column('requested_by', sa.String(length=64), nullable=False),
    sa.Column('requested_at', sa.DateTime(), nullable=False),
    sa.Column('reason', sa.String(length=500), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('decided_by', sa.String(length=64), nullable=True),
    sa.Column('decided_at', sa.DateTime(), nullable=True),
    sa.Column('comment', sa.String(length=500), nullable=True),
    sa.CheckConstraint("status IN ('Pending', 'Approved', 'Rejected')", name=op.f('ck_approvals_status')),
    sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id'], name=op.f('fk_approvals_purchase_order_id_purchase_orders')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_approvals'))
    )
    op.create_index(op.f('ix_approvals_purchase_order_id'), 'approvals', ['purchase_order_id'], unique=False)
    op.create_index(op.f('ix_approvals_status'), 'approvals', ['status'], unique=False)
    for sequence in ID_SEQUENCES:
        op.execute(sa.schema.CreateSequence(sa.Sequence(sequence)))


def downgrade() -> None:
    for sequence in ID_SEQUENCES:
        op.execute(sa.schema.DropSequence(sa.Sequence(sequence)))
    op.drop_index(op.f('ix_approvals_status'), table_name='approvals')
    op.drop_index(op.f('ix_approvals_purchase_order_id'), table_name='approvals')
    op.drop_table('approvals')
    op.drop_table('supplier_products')
    op.drop_index(op.f('ix_sales_orders_product_id'), table_name='sales_orders')
    op.drop_index(op.f('ix_sales_orders_order_date'), table_name='sales_orders')
    op.drop_table('sales_orders')
    op.drop_index(op.f('ix_purchase_orders_supplier_id'), table_name='purchase_orders')
    op.drop_index(op.f('ix_purchase_orders_status'), table_name='purchase_orders')
    op.drop_index(op.f('ix_purchase_orders_product_id'), table_name='purchase_orders')
    op.drop_table('purchase_orders')
    op.drop_index(op.f('ix_inventory_product_id'), table_name='inventory')
    op.drop_table('inventory')
    op.drop_index(op.f('ix_products_supplier_id'), table_name='products')
    op.drop_index(op.f('ix_products_category'), table_name='products')
    op.drop_table('products')
    op.drop_table('users')
    op.drop_table('suppliers')
    op.drop_index(op.f('ix_audit_logs_timestamp'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_table('audit_logs')
