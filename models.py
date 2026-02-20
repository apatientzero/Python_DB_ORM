from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Publisher(Base):
    __tablename__ = 'publisher'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    books = relationship("Book", back_populates="publisher")


class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    id_publisher = Column(Integer, ForeignKey("publisher.id"), nullable=False)
    publisher = relationship("Publisher", back_populates="books")
    stock_items = relationship("Stock", back_populates="book")


class Shop(Base):
    __tablename__ = 'shop'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    stock_items = relationship("Stock", back_populates="shop")


class Stock(Base):
    __tablename__ = 'stock'
    id = Column(Integer, primary_key=True)
    id_book = Column(Integer, ForeignKey("book.id"), nullable=False)
    id_shop = Column(Integer, ForeignKey("shop.id"), nullable=False)
    count = Column(Integer, nullable=False, default=0)

    # Guarantee the uniqueness of the book-store pair
    __table_args__ = (UniqueConstraint('id_book', 'id_shop', name='uq_book_shop'),)

    book = relationship("Book", back_populates="stock_items")
    shop = relationship("Shop", back_populates="stock_items")
    sales = relationship("Sale", back_populates="stock")


class Sale(Base):
    __tablename__ = 'sale'
    id = Column(Integer, primary_key=True)
    price = Column(Float, nullable=False)
    date_sale = Column(DateTime, nullable=False)
    id_stock = Column(Integer, ForeignKey("stock.id"), nullable=False)
    count = Column(Integer, nullable=False)
    stock = relationship("Stock", back_populates="sales")
