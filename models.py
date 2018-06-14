from sqlalchemy import Column, String, Integer, Date, Float, UniqueConstraint, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.schema import Sequence
from base import Base 

class BUTTONS(Base):    
    
    __tablename__ = 'BUTTONS' 
 
    category_id = Column(Integer, primary_key=True)     
    button_name = Column(String(250), primary_key=True) 
    parent_id = Column(Integer)
    
    def __init__(self, category_id, button_name, parent_id):         
        self.category_id = category_id  
        self.button_name = button_name
        self.parent_id = parent_id
        
class USER(Base):    
    
    __tablename__ = 'USER' 
 
    user_session = Column(String(250), primary_key=True)     
    
    def __init__(self, user_session):         
        self.user_session = user_session  
        
class USER_SELECT_APP(Base):    
    
    __tablename__ = 'USER_SELECT_APP' 
    
    dummy_id = Column(Integer, primary_key=True, autoincrement=True)     
    user_session = Column(String(250), ForeignKey("USER.user_session"))    
    app_id = Column(Integer, ForeignKey("DISCOUNT_APP.app_id", onupdate="CASCADE", ondelete="CASCADE"))
    
    def __init__(self, user_session, app_id):         
        self.user_session = user_session
        self.app_id = app_id
        
class USER_SELECT_ACTION(Base):    
    
    __tablename__ = 'USER_SELECT_ACTION' 
    
    dummy_id = Column(Integer, primary_key=True, autoincrement=True)     
    user_session = Column(String(250), ForeignKey("USER.user_session"))    
    button_id = Column(Integer, ForeignKey("BUTTONS.category_id"))
    
    def __init__(self, user_session, button_id):         
        self.user_session = user_session
        self.button_id = button_id
        
class PUBLISHER(Base):   
    
    __tablename__ = 'PUBLISHER' 
    
    publisher_id = Column(Integer, primary_key=True, autoincrement=True) 
    #publisher_id = Column(Integer, primary_key=True, Sequence('article_aid_seq', start=0, increment=1)) 
    
    publisher_name = Column(String(250))
    
    def __init__(self, publisher_name):         
        #self.publisher_id = publisher_id         
        self.publisher_name = publisher_name
        
class DEVELOPER(Base):   
    
    __tablename__ = 'DEVELOPER' 
    
    developer_id = Column(Integer, primary_key=True, autoincrement=True)     
    developer_name = Column(String(250))
    
    def __init__(self, developer_name):         
        #self.developer_id = developer_id         
        self.developer_name = developer_name
        
class GAME(Base):   
    
    __tablename__ = 'GAME' 
    
    game_id = Column(Integer, primary_key=True, autoincrement=True)     
    game_name = Column(String(250))
    
    def __init__(self, game_name):         
        #self.developer_id = developer_id         
        self.game_name = game_name
        
class TOTAL_APP(Base):   
    
    __tablename__ = 'TOTAL_APP' 
    
    app_id = Column(Integer, primary_key=True)     
    app_name = Column(String(250))
    app_type = Column(Integer, ForeignKey("GAME.game_id"))
    price = Column(String(250))
    publisher_id = Column(Integer, ForeignKey("PUBLISHER.publisher_id"))
    release_date = Column(Date)
    developer_id = Column(Integer, ForeignKey("DEVELOPER.developer_id"))
    rating = Column(String(250))
    
    
    def __init__(self, app_id, app_name, app_type, price, publisher_id, release_date, developer_id, rating):         
        self.app_id = app_id         
        self.app_name = app_name
        self.app_type = app_type         
        self.price = price
        self.publisher_id = publisher_id         
        self.release_date = release_date
        self.developer_id = developer_id 
        self.rating = rating 
        
class DISCOUNT_APP(Base):   
    
    __tablename__ = 'DISCOUNT_APP' 
    
    app_id = Column(Integer, ForeignKey("TOTAL_APP.app_id"), primary_key=True)     
    start_date = Column(Date)
    end_date = Column(Date)
    discount_rate = Column(Integer)
    
    def __init__(self, app_id, start_date, end_date, discount_rate):         
        self.app_id = app_id         
        self.start_date = start_date
        self.end_date = end_date         
        self.discount_rate = discount_rate
        
class CART(Base):   
    
    __tablename__ = 'CART' 
    __table_args__ = (PrimaryKeyConstraint('app_id', 'user_session', name='cart_sesstion'),)
    
    app_id = Column(Integer, ForeignKey("DISCOUNT_APP.app_id", onupdate="CASCADE", ondelete="CASCADE"))     
    user_session = Column(String(250), ForeignKey("USER.user_session"))
    
    def __init__(self, app_id, user_session):         
        self.app_id = app_id         
        self.user_session = user_session
        
class PURCHASE(Base):   
    
    __tablename__ = 'PURCHASE' 
    __table_args__ = (PrimaryKeyConstraint('app_id', 'user_session', name='app_id_sesstion'),)
        
    app_id = Column(Integer, ForeignKey("TOTAL_APP.app_id"))     
    user_session = Column(String(250), ForeignKey("USER.user_session"))
    purchase_price = Column(String(250))
    
    def __init__(self, app_id, user_session, purchase_price):         
        self.app_id = app_id         
        self.user_session = user_session
        self.purchase_price = purchase_price