from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base, DeclarativeMeta

Base: DeclarativeMeta = declarative_base()


class AccountTransactionTemplate(Base):
    __tablename__ = 'accounts_transaction_template'
    user = Column(String, primary_key=True)
    balance = Column(Integer, nullable=False)