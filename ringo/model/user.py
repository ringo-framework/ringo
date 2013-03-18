from ringo.model import Base, Column, Integer, Text


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)


class Usergroup(Base):
    __tablename__ = 'usergroups'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)


class Permission(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
