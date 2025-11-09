from sqlalchemy import Column,String,ForeignKey,Integer,DateTime,Text,func
import uuid 
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
from api.Database.database import Base








class NewsCart(Base):
    __tablename__ = 'news_cart'
    
    
    id = Column(String, primary_key=True,unique=True)
    title = Column(String(500),nullable=False)
    cover_image = Column(String(500),nullable=False)
    source = Column(String,nullable=False)
    category = Column(String(100))
    time_of_release = Column(DateTime(timezone=True),nullable = False)
    detail = relationship('NewsInDetail',
                          back_populates="cart",
                          uselist=False,
                          single_parent = True,
                          cascade = 'all, delete-orphan')
    news_in_nepali = relationship('NewsInNepali',
                                   back_populates='my_cart',
                                   uselist=False,
                                   single_parent = True,
                                   cascade = 'all, delete-orphan')




class   NewsInDetail(Base):
    __tablename__ = 'news_in_detail'

    id = Column(Integer, primary_key=True,autoincrement=True)
    description = Column(Text)
    cart_id = Column(String, ForeignKey('news_cart.id'),unique=True)
    cart = relationship('NewsCart',
                        back_populates="detail",
                        single_parent = True,
                        cascade = 'all, delete-orphan')






class NewsInNepali(Base):
    __tablename__ = 'news_in_nepali'

    id = Column(Integer, primary_key=True,autoincrement=True)
    title = Column(String(500),nullable=False)
    description = Column(Text)
    cart_id = Column(String, ForeignKey('news_cart.id'),unique=True)
    
    my_cart = relationship('NewsCart',
                        back_populates='news_in_nepali',
                        single_parent = True,
                        cascade = 'all, delete-orphan')
    
