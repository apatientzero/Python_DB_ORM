


# --- 1. Defining models (so that the script is self-contained) ---

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


# --- 2. Setting up the connection and executing the request ---


# ... (Классы моделей Publisher, Book, Shop, Stock, Sale остаются точно такими же, как в предыдущем коде) ...
# Я не буду дублировать их здесь для краткости, просто оставьте классы Base, Publisher, Book и т.д. выше.

def main():
    # --- НАСТРОЙКИ ПОДКЛЮЧЕНИЯ ---
    # Формат: postgresql://USER:PASSWORD@HOST:PORT/DATABASE_NAME
    # Host обычно 'localhost', порт по умолчанию '5432' (можно не указывать)

    DB_USER = "postgres"  # Ваш пользователь (часто postgres)
    DB_PASSWORD = "your_password"  # Ваш пароль
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "bookstore_db"  # Имя базы, которую вы создали в шаге 2

    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    try:
        # Создаем движок
        engine = create_engine(DATABASE_URL, echo=False)

        # Проверка соединения (опционально, но полезно для отладки)
        with engine.connect() as conn:
            print("✅ Успешное подключение к PostgreSQL!")

    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        print("Проверьте: установлен ли psycopg2, правильность логина/пароля и существует ли база данных.")
        return

    # Создаем таблицы в PostgreSQL, если их нет
    Base.metadata.create_all(engine)

    # --- ЛОГИКА ЗАПОЛНЕНИЯ И ЗАПРОСА (ОСТАЕТСЯ БЕЗ ИЗМЕНЕНИЙ) ---
    # Так как SQLAlchemy абстрагирует СУБД, код ниже работает идентично и для SQLite, и для PG.

    with Session(engine) as session:
        # Проверяем, есть ли данные, чтобы не дублировать их при каждом запуске
        if session.query(Publisher).count() == 0:
            print("База пуста. Заполняю тестовыми данными...")

            pub_1 = Publisher(name="Пушкин")
            pub_2 = Publisher(name="Толстой")

            shop_1 = Shop(name="Буквоед")
            shop_2 = Shop(name="Лабиринт")
            shop_3 = Shop(name="Книжный дом")

            # Важно: в PostgreSQL ID генерируются автоматически (SERIAL/IDENTITY),
            # поэтому мы не передаем id явно, а добавляем объекты и делаем commit.
            session.add_all([pub_1, pub_2, shop_1, shop_2, shop_3])
            session.commit()  # Коммит нужен, чтобы присвоились ID

            # Теперь, когда ID присвоены, создаем книги
            book_1 = Book(title="Капитанская дочка", id_publisher=pub_1.id)
            book_2 = Book(title="Руслан и Людмила", id_publisher=pub_1.id)
            book_3 = Book(title="Евгений Онегин", id_publisher=pub_1.id)
            book_4 = Book(title="Война и мир", id_publisher=pub_2.id)

            session.add_all([book_1, book_2, book_3, book_4])
            session.commit()

            stock_1 = Stock(id_book=book_1.id, id_shop=shop_1.id, count=10)
            stock_2 = Stock(id_book=book_2.id, id_shop=shop_1.id, count=5)
            stock_3 = Stock(id_book=book_1.id, id_shop=shop_2.id, count=7)
            stock_4 = Stock(id_book=book_3.id, id_shop=shop_3.id, count=3)

            session.add_all([stock_1, stock_2, stock_3, stock_4])
            session.commit()

            sales_data = [
                Sale(price=600, date_sale=datetime(2022, 11, 9), id_stock=stock_1.id, count=1),
                Sale(price=500, date_sale=datetime(2022, 11, 8), id_stock=stock_2.id, count=1),
                Sale(price=580, date_sale=datetime(2022, 11, 5), id_stock=stock_3.id, count=1),
                Sale(price=490, date_sale=datetime(2022, 11, 2), id_stock=stock_4.id, count=1),
                Sale(price=600, date_sale=datetime(2022, 10, 26), id_stock=stock_1.id, count=1),
            ]
            session.add_all(sales_data)
            session.commit()
            print("Данные добавлены.\n")

    # --- ЗАПРОС К ПОЛЬЗОВАТЕЛЮ И ВЫВОД (БЕЗ ИЗМЕНЕНИЙ) ---
    search_input = input("Введите имя издателя (например, Пушкин): ").strip()

    with Session(engine) as session:
        publisher = None

        if not search_input.isdigit():
            publisher = session.query(Publisher).filter(Publisher.name.ilike(f"%{search_input}%")).first()
        else:
            publisher = session.query(Publisher).filter(Publisher.id == int(search_input)).first()

        if not publisher:
            print("Издатель не найден.")
            return

        print(f"\nПродажи книг издательства '{publisher.name}':\n")
        print(f"{'Книга':<25} | {'Магазин':<15} | {'Цена':<6} | {'Дата'}")
        print("-" * 70)

        query = (
            session.query(Book.title, Shop.name, Sale.price, Sale.date_sale)
            .join(Stock, Sale.id_stock == Stock.id)
            .join(Book, Stock.id_book == Book.id)
            .join(Shop, Stock.id_shop == Shop.id)
            .filter(Book.id_publisher == publisher.id)
            .order_by(Sale.date_sale.desc())
        )

        results = query.all()

        if not results:
            print("Продаж не найдено.")
            return

        for title, shop_name, price, date_sale in results:
            if isinstance(date_sale, datetime):
                date_str = date_sale.strftime("%d-%m-%Y")
            else:
                date_str = str(date_sale)

            print(f"{title:<25} | {shop_name:<15} | {price:<6} | {date_str}")


if __name__ == "__main__":
    main()