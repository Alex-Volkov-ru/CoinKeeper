"""Added incomes relation to IncomeCategory

Revision ID: e5fd1066d47f
Revises: f9146be923ee
Create Date: 2025-03-03 19:17:52.601604

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e5fd1066d47f"
down_revision: Union[str, None] = "f9146be923ee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
