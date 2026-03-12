"""대시보드 테이블 추가 (pdf_download_events + 인덱스)

Revision ID: 004_add_dashboard_tables
Revises: 003_csv_seed_data
Create Date: 2026-03-12

pdf_download_events 테이블 생성 및 recommendation_history 인덱스 추가.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '004_add_dashboard_tables'
down_revision = '003_csv_seed_data'
branch_labels = None
depends_on = None


def upgrade():
    # pdf_download_events 테이블 생성
    op.create_table(
        'pdf_download_events',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_name', sa.String(100), nullable=True),
        sa.Column('target_year', sa.Integer, nullable=True),
        sa.Column('target_month', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # pdf_download_events 인덱스
    op.create_index('idx_pde_user_id', 'pdf_download_events', ['user_id'])
    op.create_index('idx_pde_created_at', 'pdf_download_events', ['created_at'])

    # recommendation_history 인덱스 추가 (집계 쿼리 성능 최적화)
    op.create_index(
        'idx_rh_created_at',
        'recommendation_history',
        ['created_at'],
        if_not_exists=True,
    )


def downgrade():
    op.drop_index('idx_rh_created_at', table_name='recommendation_history')
    op.drop_index('idx_pde_created_at', table_name='pdf_download_events')
    op.drop_index('idx_pde_user_id', table_name='pdf_download_events')
    op.drop_table('pdf_download_events')
