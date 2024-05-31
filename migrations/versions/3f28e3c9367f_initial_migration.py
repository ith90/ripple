"""Initial migration.

Revision ID: 3f28e3c9367f
Revises: 
Create Date: 2024-05-30 23:03:11.539441

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f28e3c9367f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('emotions')
    op.drop_table('users')
    op.drop_table('weather')
    op.drop_table('entry')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('entry',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('text', sa.VARCHAR(length=300), nullable=False),
    sa.Column('timestamp', sa.DATETIME(), nullable=True),
    sa.Column('weather_id', sa.INTEGER(), nullable=True),
    sa.Column('emotion_id', sa.INTEGER(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['emotion_id'], ['emotions.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['weather_id'], ['weather.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('weather',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('description', sa.VARCHAR(), nullable=False),
    sa.Column('temp', sa.FLOAT(), nullable=False),
    sa.Column('feels_like', sa.FLOAT(), nullable=False),
    sa.Column('clouds', sa.INTEGER(), nullable=False),
    sa.Column('rain_1h', sa.FLOAT(), nullable=True),
    sa.Column('snow_1h', sa.FLOAT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('username', sa.TEXT(), nullable=False),
    sa.Column('hash', sa.TEXT(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('emotions',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('gratitude', sa.FLOAT(), nullable=True),
    sa.Column('admiration', sa.FLOAT(), nullable=True),
    sa.Column('joy', sa.FLOAT(), nullable=True),
    sa.Column('approval', sa.FLOAT(), nullable=True),
    sa.Column('caring', sa.FLOAT(), nullable=True),
    sa.Column('pride', sa.FLOAT(), nullable=True),
    sa.Column('excitement', sa.FLOAT(), nullable=True),
    sa.Column('neutral', sa.FLOAT(), nullable=True),
    sa.Column('relief', sa.FLOAT(), nullable=True),
    sa.Column('optimism', sa.FLOAT(), nullable=True),
    sa.Column('realization', sa.FLOAT(), nullable=True),
    sa.Column('love', sa.FLOAT(), nullable=True),
    sa.Column('annoyance', sa.FLOAT(), nullable=True),
    sa.Column('desire', sa.FLOAT(), nullable=True),
    sa.Column('disapproval', sa.FLOAT(), nullable=True),
    sa.Column('sadness', sa.FLOAT(), nullable=True),
    sa.Column('surprise', sa.FLOAT(), nullable=True),
    sa.Column('disappointment', sa.FLOAT(), nullable=True),
    sa.Column('remorse', sa.FLOAT(), nullable=True),
    sa.Column('grief', sa.FLOAT(), nullable=True),
    sa.Column('amusement', sa.FLOAT(), nullable=True),
    sa.Column('confusion', sa.FLOAT(), nullable=True),
    sa.Column('anger', sa.FLOAT(), nullable=True),
    sa.Column('curiosity', sa.FLOAT(), nullable=True),
    sa.Column('disgust', sa.FLOAT(), nullable=True),
    sa.Column('fear', sa.FLOAT(), nullable=True),
    sa.Column('embarrassment', sa.FLOAT(), nullable=True),
    sa.Column('nervousness', sa.FLOAT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
