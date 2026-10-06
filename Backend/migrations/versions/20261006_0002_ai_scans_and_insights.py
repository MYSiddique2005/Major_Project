"""ai scans and insights

Proactive scans by the AI assistant and the insights they record (Phase 6).

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-06 11:10:19.645781
"""
from alembic import op
import sqlalchemy as sa


revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

# Back Repository.next_id(); listed literally so this migration never changes with the code.
ID_SEQUENCES = ("ai_scan_id_seq", "ai_insight_id_seq")


def upgrade() -> None:
    for sequence in ID_SEQUENCES:
        op.execute(sa.schema.CreateSequence(sa.Sequence(sequence)))
    op.create_table('ai_scans',
    sa.Column('id', sa.String(length=16), nullable=False),
    sa.Column('started_at', sa.DateTime(), nullable=False),
    sa.Column('finished_at', sa.DateTime(), nullable=True),
    sa.Column('trigger', sa.String(length=64), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('findings', sa.Integer(), nullable=False),
    sa.Column('insights', sa.Integer(), nullable=False),
    sa.Column('message', sa.String(length=500), nullable=False),
    sa.Column('provider', sa.String(length=32), nullable=True),
    sa.Column('model', sa.String(length=64), nullable=True),
    sa.CheckConstraint("status IN ('Running', 'Completed', 'Failed')", name=op.f('ck_ai_scans_status')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ai_scans'))
    )
    op.create_index(op.f('ix_ai_scans_started_at'), 'ai_scans', ['started_at'], unique=False)
    op.create_table('ai_insights',
    sa.Column('id', sa.String(length=16), nullable=False),
    sa.Column('scan_id', sa.String(length=16), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('subject_type', sa.String(length=16), nullable=False),
    sa.Column('subject_id', sa.String(length=16), nullable=False),
    sa.Column('subject_name', sa.String(length=160), nullable=False),
    sa.Column('severity', sa.String(length=32), nullable=False),
    sa.Column('headline', sa.String(length=200), nullable=False),
    sa.Column('explanation', sa.Text(), nullable=False),
    sa.Column('action', sa.String(length=32), nullable=False),
    sa.Column('product_id', sa.String(length=16), nullable=True),
    sa.Column('product_name', sa.String(length=160), nullable=True),
    sa.Column('supplier_id', sa.String(length=16), nullable=True),
    sa.Column('supplier_name', sa.String(length=160), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('system_quantity', sa.Integer(), nullable=True),
    sa.Column('evidence', sa.JSON(), nullable=False),
    sa.Column('checks', sa.JSON(), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('reviewed_by', sa.String(length=64), nullable=True),
    sa.Column('reviewed_at', sa.DateTime(), nullable=True),
    sa.CheckConstraint("severity IN ('Low', 'Medium', 'High', 'Critical')", name=op.f('ck_ai_insights_severity')),
    sa.CheckConstraint("status IN ('New', 'Acknowledged', 'Dismissed', 'Superseded')", name=op.f('ck_ai_insights_status')),
    sa.ForeignKeyConstraint(['scan_id'], ['ai_scans.id'], name=op.f('fk_ai_insights_scan_id_ai_scans'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ai_insights'))
    )
    op.create_index(op.f('ix_ai_insights_created_at'), 'ai_insights', ['created_at'], unique=False)
    op.create_index(op.f('ix_ai_insights_scan_id'), 'ai_insights', ['scan_id'], unique=False)
    op.create_index(op.f('ix_ai_insights_status'), 'ai_insights', ['status'], unique=False)
    op.create_index(op.f('ix_ai_insights_subject_id'), 'ai_insights', ['subject_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_ai_insights_subject_id'), table_name='ai_insights')
    op.drop_index(op.f('ix_ai_insights_status'), table_name='ai_insights')
    op.drop_index(op.f('ix_ai_insights_scan_id'), table_name='ai_insights')
    op.drop_index(op.f('ix_ai_insights_created_at'), table_name='ai_insights')
    op.drop_table('ai_insights')
    op.drop_index(op.f('ix_ai_scans_started_at'), table_name='ai_scans')
    op.drop_table('ai_scans')
    for sequence in ID_SEQUENCES:
        op.execute(sa.schema.DropSequence(sa.Sequence(sequence)))
