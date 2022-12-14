from sqlalchemy import Column, String, insert, select, delete, SmallInteger, ForeignKey, and_, BigInteger, update
from sqlalchemy.orm import sessionmaker

from tgbot.models.students import Student
from tgbot.services.db_base import Base


class Car(Base):
    __tablename__ = "car"

    car_order = Column(BigInteger(), primary_key=True)
    car_number = Column(String())
    owner = Column(ForeignKey(Student.tg_id))
    status = Column(SmallInteger, default=1)

    @classmethod
    async def add_car(cls, session_maker: sessionmaker, car_number: str, owner: int, status: int = 1) -> 'Car':
        async with session_maker() as db_session:
            sql = insert(cls).values(car_number=car_number,
                                     owner=owner,
                                     status=status).returning("*")
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    @classmethod
    async def get_car(cls, session_maker: sessionmaker,
                      car_number: str, status: int = 1) -> 'Car':
        async with session_maker() as db_session:
            sql = select(cls).where(cls.car_number == car_number, cls.status == status)
            request = await db_session.execute(sql)
            car: cls = request.scalar()
            await db_session.commit()
            return car

    @classmethod
    async def get_cars(cls, session_maker: sessionmaker,
                       car_number: str):
        async with session_maker() as db_session:
            sql = select(cls).where(cls.car_number == car_number)
            request = await db_session.execute(sql)
            cars = request.scalars().all()
            await db_session.commit()
            return cars

    @classmethod
    async def get_active_car(cls, session_maker: sessionmaker,
                             car_number: str, status: int = 1) -> 'Car':
        async with session_maker() as db_session:
            sql = select(cls).where(cls.car_number == car_number, cls.status == status)
            request = await db_session.execute(sql)
            car: cls = request.scalar()
            await db_session.commit()
            return car

    @classmethod
    async def get_car_by_tg(cls, session_maker: sessionmaker,
                            tg_id: int, status: int = 1) -> 'Car':

        async with session_maker() as db_session:
            sql = select(cls).where(cls.owner == tg_id, cls.status == status)
            request = await db_session.execute(sql)
            car: cls = request.scalar()
            await db_session.commit()
            return car


    @classmethod
    async def get_all_active_by_tg(cls, session_maker: sessionmaker,
                                   tg_id: int, status: int = 1):
        async with session_maker() as db_session:
            sql = select(cls).where(and_(cls.owner == tg_id, cls.status == status))
            request = await db_session.execute(sql)
            cars: cls = request.scalars()
            await db_session.commit()
            return cars

    @classmethod
    async def get_all_by_tg(cls, session_maker: sessionmaker,
                            tg_id: int, status: int = 1):
        async with session_maker() as db_session:
            sql = select(cls).where(cls.owner == tg_id, cls.status == status)
            request = await db_session.execute(sql)
            cars: cls = request.scalars()
            await db_session.commit()
            return cars

    @classmethod
    async def get_all_by_number(cls, session_maker: sessionmaker,
                                car_number: str, status: int = 1):
        async with session_maker() as db_session:
            sql = select(cls).where(and_(cls.car_number == car_number, cls.status == status))
            request = await db_session.execute(sql)
            cars: cls = request.all()
            await db_session.commit()
            return cars

    @classmethod
    async def get_all_by_number_like(cls, session_maker: sessionmaker,
                                     car_number: str, status: int = 1):
        async with session_maker() as db_session:
            sql = select(cls).where(cls.status == status).filter(cls.car_number.like(car_number))
            request = await db_session.execute(sql)
            cars: cls = request.scalars()
            await db_session.commit()
            return cars

    @classmethod
    async def delete_all_by_tg(cls, session_maker: sessionmaker, tg_id: int, status: int = 1):
        async with session_maker() as db_session:
            sql = delete(cls).where(and_(cls.owner == tg_id, cls.status == status))
            request = await db_session.execute(sql)
            await db_session.commit()
            return request

    @classmethod
    async def get_owner_by_car(cls, session_maker: sessionmaker,
                               car_number: str, status: int = 1):
        async with session_maker() as db_session:
            sql = select(cls.owner).where(and_(cls.car_number == car_number, cls.status == status))
            request = await db_session.execute(sql)
            owner_id: cls = request.scalar()
            await db_session.commit()
            return owner_id

    @staticmethod
    async def update_status_by_order(session_maker: sessionmaker, order: int, status: dict):
        async with session_maker() as db_session:
            sql = update(Car).where(Car.car_order == order).values(**status)
            request = await db_session.execute(sql)
            await db_session.commit()
            return request

    @staticmethod
    async def update_status(session_maker: sessionmaker,
                            owner: int, car_number: str, status: dict):
        async with session_maker() as db_session:
            sql = update(Car).where(and_(Car.car_number == car_number,
                                         Car.owner == owner)).values(**status)
            request = await db_session.execute(sql)
            await db_session.commit()
            return request

    @classmethod
    async def delete_car(cls, session_maker: sessionmaker,
                         car_number: str):
        async with session_maker() as db_session:
            sql = delete(cls).where(cls.car_number == car_number)
            result = await db_session.execute(sql)
            await db_session.commit()
            return result
