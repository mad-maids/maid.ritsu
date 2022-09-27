from sqlalchemy import Column, String, insert, select, delete, SmallInteger, ForeignKey, and_
from sqlalchemy.orm import sessionmaker

from tgbot.models.students import Student
from tgbot.services.db_base import Base


class Car(Base):
    __tablename__ = "car"
    car_number = Column(String(), primary_key=True)
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
    async def get_car_by_tg(cls, session_maker: sessionmaker,
                            tg_id: int, status: int = 1) -> 'Car':
        async with session_maker() as db_session:
            sql = select(cls).where(and_(cls.owner == tg_id, cls.status == status))
            request = await db_session.execute(sql)
            car: cls = request.scalar()
            await db_session.commit()
            return car

    @classmethod
    async def get_all_by_tg(cls, session_maker: sessionmaker,
                            tg_id: int, status: int = 1):
        async with session_maker() as db_session:
            sql = select(cls).where(and_(cls.owner == tg_id, cls.status == status))
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
    async def delete_car(cls, session_maker: sessionmaker,
                         car_number: str):
        async with session_maker() as db_session:
            sql = delete(cls).where(cls.car_number == car_number)
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    @classmethod
    async def delete_all_by_tg(cls, session_maker: sessionmaker, tg_id: int, status: int = 1):
        async with session_maker() as db_session:
            sql = delete(cls).where(and_(cls.owner == tg_id, cls.status == status))
            request = await db_session.execute(sql)
            await db_session.commit()
            return request
