"""Add query optimization indexes

Revision ID: 00000003
Revises: 00000002
Create Date: 2023-05-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '00000003'
down_revision = '00000002'
branch_labels = None
depends_on = None


def upgrade():
    # Add indexes to articles table
    op.create_index('ix_articles_source_id', 'articles', ['source_id'], unique=False)
    op.create_index('ix_articles_status', 'articles', ['status'], unique=False)
    op.create_index('ix_articles_published_at', 'articles', ['published_at'], unique=False)
    op.create_index('ix_articles_discovered_at', 'articles', ['discovered_at'], unique=False)
    op.create_index('ix_articles_political_bias', 'articles', ['political_bias'], unique=False)
    op.create_index('ix_articles_emotional_language', 'articles', ['emotional_language'], unique=False)
    op.create_index('ix_articles_fact_opinion_ratio', 'articles', ['fact_opinion_ratio'], unique=False)
    
    # Compound indexes for common query patterns
    op.create_index('ix_articles_source_status', 'articles', ['source_id', 'status'], unique=False)
    op.create_index('ix_articles_status_published', 'articles', ['status', 'published_at'], unique=False)
    
    # Add indexes to sources table
    op.create_index('ix_sources_name', 'sources', ['name'], unique=True)
    op.create_index('ix_sources_category', 'sources', ['category'], unique=False)
    op.create_index('ix_sources_reliability_score', 'sources', ['reliability_score'], unique=False)
    op.create_index('ix_sources_bias_score', 'sources', ['bias_score'], unique=False)
    op.create_index('ix_sources_last_crawled_at', 'sources', ['last_crawled_at'], unique=False)
    
    # Add indexes to users table for auth-related queries
    op.create_index('ix_users_role', 'users', ['role'], unique=False)
    op.create_index('ix_users_is_active', 'users', ['is_active'], unique=False)
    op.create_index('ix_users_is_verified', 'users', ['is_verified'], unique=False)
    
    # Add indexes to user_sessions table
    op.create_index('ix_user_sessions_user_id', 'user_sessions', ['user_id'], unique=False)
    op.create_index('ix_user_sessions_expires_at', 'user_sessions', ['expires_at'], unique=False)
    op.create_index('ix_user_sessions_is_active', 'user_sessions', ['is_active'], unique=False)


def downgrade():
    # Remove indexes from user_sessions table
    op.drop_index('ix_user_sessions_is_active', table_name='user_sessions')
    op.drop_index('ix_user_sessions_expires_at', table_name='user_sessions')
    op.drop_index('ix_user_sessions_user_id', table_name='user_sessions')
    
    # Remove indexes from users table
    op.drop_index('ix_users_is_verified', table_name='users')
    op.drop_index('ix_users_is_active', table_name='users')
    op.drop_index('ix_users_role', table_name='users')
    
    # Remove indexes from sources table
    op.drop_index('ix_sources_last_crawled_at', table_name='sources')
    op.drop_index('ix_sources_bias_score', table_name='sources')
    op.drop_index('ix_sources_reliability_score', table_name='sources')
    op.drop_index('ix_sources_category', table_name='sources')
    op.drop_index('ix_sources_name', table_name='sources')
    
    # Remove compound indexes from articles table
    op.drop_index('ix_articles_status_published', table_name='articles')
    op.drop_index('ix_articles_source_status', table_name='articles')
    
    # Remove indexes from articles table
    op.drop_index('ix_articles_fact_opinion_ratio', table_name='articles')
    op.drop_index('ix_articles_emotional_language', table_name='articles')
    op.drop_index('ix_articles_political_bias', table_name='articles')
    op.drop_index('ix_articles_discovered_at', table_name='articles')
    op.drop_index('ix_articles_published_at', table_name='articles')
    op.drop_index('ix_articles_status', table_name='articles')
    op.drop_index('ix_articles_source_id', table_name='articles')