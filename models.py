from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import Base  # <-- db_async o‘rniga db

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(64), default="")
    lang = Column(String(4), default="uz")
    balance = Column(Integer, default=0)

    transactions = relationship("Transaction", back_populates="user", lazy="selectin")
    orders = relationship("Order", back_populates="user", lazy="selectin")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    kind = Column(String(32))  # rank|coin
    name = Column(String(128))
    price = Column(Integer)
    description = Column(Text, default="")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer)
    status = Column(String(32), default="pending")  # pending|approved|rejected
    file_id = Column(String(256), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="transactions", lazy="joined")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    nickname = Column(String(64))
    status = Column(String(32), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="orders", lazy="joined")
    product = relationship("Product", lazy="joined")
