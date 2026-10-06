"""ai origin of purchase orders

Records whether a purchase order was drafted from an AI recommendation or insight, with the
recommendation as it stood, and links an insight to the draft made from it (Phase 7).

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-06 11:37:04.873854
"""
from alembic import op
import sqlalchemy as sa


revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('ai_insights', sa.Column('purchase_order_id', sa.String(length=16), nullable=True))
    op.add_column('purchase_orders', sa.Column('origin', sa.String(length=32), server_default='Manual', nullable=False))
    op.create_check_constraint(
        op.f('ck_purchase_orders_origin'), 'purchase_orders', "origin IN ('Manual', 'AI Assistant', 'AI Insight')"
    )
    op.add_column('purchase_orders', sa.Column('origin_ref', sa.String(length=16), nullable=True))
    op.add_column('purchase_orders', sa.Column('ai_recommendation', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('purchase_orders', 'ai_recommendation')
    op.drop_column('purchase_orders', 'origin_ref')
    op.drop_constraint(op.f('ck_purchase_orders_origin'), 'purchase_orders', type_='check')
    op.drop_column('purchase_orders', 'origin')
    op.drop_column('ai_insights', 'purchase_order_id')
