from sqlalchemy import Column, BigInteger, String, insert, select, update, SmallInteger, and_, delete
from sqlalchemy.orm import sessionmaker

from tgbot.services.db_base import Base


class Student(Base):

    __tablename__ = "student"

    tg_id = Column(BigInteger, primary_key=True)
    first_name = Column(String(100), nullable=True)
    phone_number = Column(String, nullable=True)
    status = Column(SmallInteger, default=1)

    @classmethod
    async def create_student(cls, session_maker: sessionmaker, tg_id: int,
                             first_name: str=None, phone_number: str = None, status: int = 1 ):
        async with session_maker() as db_session:
            sql = insert(cls).values(tg_id=tg_id, first_name=first_name, phone_number=phone_number, status=status).returning("*")
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    @classmethod
    async def get_student(cls, session_maker: sessionmaker,
                          tg_id: int, status: int = 1) -> 'Student':
        async with session_maker() as db_session:
            sql = select(cls).where(and_(cls.tg_id == tg_id, cls.status == status))
            request = await db_session.execute(sql)
            student: cls = request.scalar()
            await db_session.commit()
            return student

    async def update_client(self, session_maker: sessionmaker, updated_fields: dict) -> 'Student':
        async with session_maker() as db_session:
            sql = update(Student).where(Student.tg_id == self.tg_id).values(**updated_fields)
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    @classmethod
    async def remove_student(cls, session_maker: sessionmaker, tg_id: int):
        async with session_maker() as db_session:
            sql = delete(Student).where(Student.tg_id == tg_id)
            request = await db_session.execute(sql)
            await db_session.commit()
            return request
