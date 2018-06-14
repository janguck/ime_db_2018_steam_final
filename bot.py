from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select, exists, update
from sqlalchemy import and_
from sqlalchemy import text
from datetime import datetime
from datetime import date
from models import *
from utils import *

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = get_db_information()
db = SQLAlchemy(app)

engine = sqlalchemy.create_engine(get_db_information())
engine.connect()
Session = sessionmaker(bind=engine)
session = Session()


@app.route('/keyboard')
def Keyboard():
 
    dataSend = {
        "type" : "buttons",
        "buttons" : ["쇼핑", "내 기록"],
    }
 
    return jsonify(dataSend)
 
def add_user_select_action(user_session=None, content=None):
    session.add(USER_SELECT_ACTION(user_session=user_session, button_id=session.query(BUTTONS.category_id).filter(BUTTONS.button_name==content).all()[0][0]))
    session.commit()
    session.close()
def get_button(content=None):
    return [i[0] for i in session.query(BUTTONS.button_name).filter(BUTTONS.parent_id==session.query(BUTTONS.category_id).filter(BUTTONS.button_name==content).all()[0][0]).all()]+['0']
def check_exists_user_session(user_session=None):
    if session.query(exists().where(USER.user_session==user_session)).scalar():
        pass
    else:
        session.add(USER(user_session=user_session))
        session.commit()
        session.close()   
def is_exists_app_id(app_name=None):
    try:
        sql = text('SELECT t.app_id FROM TOTAL_APP as t INNER JOIN DISCOUNT_APP as d on d.app_id = t.app_id WHERE t.app_name="{}"'.format(app_name))
        result = engine.execute(sql)
        return [i[0] for i in result][0]
    except:
        return False
def current_user_select_app(user_session=None):
    sql = text("""SELECT app_id from  USER_SELECT_APP where dummy_id in  (SELECT max(dummy_id) \
 FROM USER_SELECT_APP where user_session='{}')""".format(user_session))
    result = engine.execute(sql)
    return [i[0] for i in result ][0]  #'쇼핑' 의 형태
def current_user_select_action(user_session=None):
    sql = text("""SELECT button_name from  BUTTONS where category_id \
 in(SELECT button_id from  USER_SELECT_ACTION where dummy_id in  (SELECT max(dummy_id) \
 FROM USER_SELECT_ACTION where user_session='{}'))""".format("bFbtHnYZHDId"))
    result = engine.execute(sql)
    return [i[0] for i in result ][0]
def satisfactory_top_10():
    sql = text('SELECT app_name FROM TOTAL_APP ORDER BY rating DESC limit 10')
    result = engine.execute(sql)
    return [i[0] for i in result]+['0']
def discount_top_10():
    sql = text('SELECT app_name FROM DISCOUNT_APP inner join TOTAL_APP on TOTAL_APP.app_id = DISCOUNT_APP.app_id order by discount_rate desc limit 10')
    result = engine.execute(sql)
    return [i[0] for i in result]+['0']
def release_top_10():
    sql = text('select app_name from TOTAL_APP order by release_date asc limit 10')
    result = engine.execute(sql)
    return [i[0] for i in result]+['0']
def low_price_top_10():
    sql = text('select app_name, price from TOTAL_APP inner join DISCOUNT_APP as da on TOTAL_APP.app_id = da.app_id order by price asc limit 10')
    result = engine.execute(sql)
    return [i[0] for i in result]+['0']
def high_price_top_10():
    sql = text('select app_name from TOTAL_APP inner join DISCOUNT_APP as da on TOTAL_APP.app_id = da.app_id order by price desc limit 10')
    result = engine.execute(sql)
    return [i[0] for i in result]+['0']
def deadline_top_10():
    sql = text('select app_name from TOTAL_APP as t inner join DISCOUNT_APP as d on t.app_id = d.app_id where end_date>=CURDATE() order by end_date asc limit 10')
    result = engine.execute(sql)
    return [i[0] for i in result]+['0']
def popular_top_10():
    sql = text('select ta.app_name from PURCHASE as p inner join TOTAL_APP as ta ON ta.app_id = p.app_id group by p.app_id order by count(p.app_id) desc limit 10')
    result = engine.execute(sql)
    return [i[0] for i in result]+['0']

def add_user_select_app(user_session=None, app_id=None):
    session.add(USER_SELECT_APP(user_session=user_session, app_id=app_id))
    session.commit()
    session.close()
def purchase(app_id=None, user_session=None):
    sql = text('select t.price*da.discount_rate*1/100 as purchase_price from TOTAL_APP as t inner join DISCOUNT_APP as da on t.app_id=da.app_id where t.app_id={}'.format(app_id))
    result = engine.execute(sql)
    purchase_price = [i[0] for i in result][0]
    sql = text('SELECT * from CART as c where c.app_id="{}"'.format(app_id))
    result = engine.execute(sql)
    app_cart = [i[0] for i in result]
    if len(app_cart) != 0:
        refund_cart(app_id=app_id,user_session=user_session)
    sql = text("""INSERT INTO PURCHASE (app_id, user_session,purchase_price) VALUES ({},'{}',{})""".format(app_id, user_session, purchase_price))
    result = engine.execute(sql)
def refund_purchase(app_id=None, user_session=None):
    sql = text('select t.price*da.discount_rate*1/100 as purchase_price from TOTAL_APP as t inner join DISCOUNT_APP as da on t.app_id=da.app_id where t.app_id={}'.format(app_id))
    result = engine.execute(sql)
    purchase_price = [i[0] for i in result][0]
    sql = text("""DELETE FROM PURCHASE where app_id={} and user_session='{}' and purchase_price={}""".format(app_id, user_session, purchase_price))
    result = engine.execute(sql)
def cart(app_id=None, user_session=None):
    sql = text("""INSERT INTO CART (app_id, user_session) VALUES ({},'{}')""".format(app_id, user_session))
    result = engine.execute(sql)
def refund_cart(app_id=None, user_session=None):
    sql = text("""DELETE FROM CART WHERE app_id={} and user_session='{}'""".format(app_id, user_session))
    result = engine.execute(sql)
def end_message(content=None):
    return  {
             'keyboard': {
                'type': 'buttons',
                'buttons':["쇼핑", "내 기록"]
            },
            "message": {
                "text": "{}가 완료됬습니다.\n어떤 기능을 사용하시겠습니까?".format(content)
            }
        }
def get_app_information(app_name=None):
    sql = text('SELECT d.end_date FROM TOTAL_APP as t INNER JOIN DISCOUNT_APP as d on d.app_id = t.app_id WHERE t.app_name="{}"'.format(app_name))
    result = engine.execute(sql)
    end_date = [i[0] for i in result][0]
    now=datetime.now()
    d0 = date(now.year, now.month, now.day) 
    d1 = date(end_date.year , end_date.month , end_date.day) 
    delta = d1 - d0 #
    sql = text('SELECT t.app_name, d.discount_rate, t.price*d.discount_rate*0.01, "{}" FROM TOTAL_APP as t INNER JOIN DISCOUNT_APP as d on d.app_id = t.app_id where t.app_name="{}"'.format(delta.days,app_name))
    result = engine.execute(sql)
    game_info = [[i[0],i[1],i[2],i[3]] for i in result][0]
    str_info = "게임정보\n게임이름 : {}\n할인율 : {}\n가격 : {}\n 남은 할인 기간 : {}".format(game_info[0], game_info[1], game_info[2], game_info[3])
    return str_info

def check_button(app_id=None):
    sql = text('SELECT * from PURCHASE as c where c.app_id="{}"'.format(app_id))
    result = engine.execute(sql)
    app_purchase = [i[0] for i in result]
    sql = text('SELECT * from CART as c where c.app_id="{}"'.format(app_id))
    result = engine.execute(sql)
    app_cart = [i[0] for i in result]
    if len(app_purchase) == 0 and len(app_cart) != 0:
        buttons = ['구매하기','장바구니 취소'] + ['0']
    elif len(app_purchase) != 0 and len(app_cart) == 0:
        buttons = ['구매 취소'] + ['0']
    else:
        buttons = ['구매하기','장바구니'] + ['0']
    return buttons

def show_cart_list(user_session=None):
    sql = text('SELECT ta.app_name FROM TOTAL_APP AS ta INNER JOIN CART AS c ON c.app_id = ta.app_id WHERE c.user_session = "{}"'.format(user_session))
    result = engine.execute(sql)
    cartlist = [i[0] for i in result] +['0']
    return cartlist
def show_purchase_list(user_session=None):
    sql = text('SELECT ta.app_name FROM TOTAL_APP AS ta INNER JOIN PURCHASE AS p ON p.app_id = ta.app_id WHERE p.user_session = "{}"'.format(user_session))
    result = engine.execute(sql)
    purchaselist = [i[0] for i in result] +['0']
    return purchaselist
@app.route('/message', methods=['POST'])
def Message():

    dataReceive = request.get_json()
    content = dataReceive['content']
    user_session = dataReceive['user_key']
    print(content)
    print("---------------------------------",user_session)
    check_exists_user_session(user_session=user_session)
    if content == '0':
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':["쇼핑", "내 기록"]
            },
            "message": {
                "text": "어떤 기능을 사용하시겠습니까?"
            }
        }
    
    elif content == "구매하기":
        purchase(app_id=current_user_select_app(user_session=user_session), user_session=user_session)
        dataSend = end_message(content=content) 
    elif content == "장바구니":
        cart(app_id=current_user_select_app(user_session=user_session), user_session=user_session)
        dataSend = end_message(content=content) 
    elif content == "구매 취소":
        refund_purchase(app_id=current_user_select_app(user_session=user_session), user_session=user_session)
        dataSend = end_message(content=content) 
    elif content == "장바구니 취소":
        refund_cart(app_id=current_user_select_app(user_session=user_session), user_session=user_session)
        dataSend = end_message(content=content) 
    elif content == "쇼핑":
        
        add_user_select_action(user_session=user_session, content=content)
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':get_button(content=content)
            },
            "message": {
                "text": "어떤 방법으로 쇼핑하겠습니까?"
            }
        }
        
        
    elif content == "내 기록":
        
        add_user_select_action(user_session=user_session, content=content)
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':get_button(content=content)
            },
            "message": {
                "text": "어떤 기능을 선택하시겠습니까?"
            }
        }
        
    elif content == "장바구니 목록":
        
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':show_cart_list(user_session=user_session)
            },
            "message": {
                "text": "장바구니 목록입니다. 보고싶은 게임을 선택해주세요."
            }
        }
        
    elif content == "구매 목록":
        
        add_user_select_action(user_session=user_session, content=content)
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':show_purchase_list(user_session=user_session)
            },
            "message": {
                "text": "구매 목록입니다. 보고싶은 게임을 선택해주세요."
            }
        }    
        
        
        
    elif content == "이름 검색":
        add_user_select_action(user_session=user_session, content=content)
        dataSend = {
            "message": {
                "text": "이름을 입력해주세요."
            }
        }
    elif current_user_select_action(user_session=user_session) == "이름 검색":
        
        if is_exists_app_id(app_name=content) != False:
            add_user_select_app(user_session=user_session, app_id=is_exists_app_id(app_name=content))
            dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':check_button(app_id=is_exists_app_id(app_name=content))
            },
            "message": {
                "text": get_app_information(app_name=content)
            }
            }
        else:
            dataSend = {
                "message": {
                    "text": "틀렸습니다. 다시 입력해주세요."
                }
            }
            
    
    elif content == "top10 조회":
        add_user_select_action(user_session=user_session, content=content)
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':get_button(content=content)
            },
            "message": {
                "text": "어떤 기준으로 쇼핑하겠습니까?"
            }
        }
    
    
    elif content == "만족도순":
        
        add_user_select_action(user_session=user_session, content=content)
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':satisfactory_top_10()
            },
            "message": {
                "text": "{}입니다. 선택해주세요.".format(content)
            }
        }
    elif content == "할인율순":
               
        add_user_select_action(user_session=user_session, content=content)
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':discount_top_10()
            },
            "message": {
                "text": "{}입니다. 선택해주세요.".format(content)
            }
        }
    elif content == "출시일순":
                
        add_user_select_action(user_session=user_session, content=content)
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':release_top_10()
            },
            "message": {
                "text": "{}입니다. 선택해주세요.".format(content)
            }
        }
    elif content == "높은 가격순":
        
        add_user_select_action(user_session=user_session, content=content)
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':high_price_top_10()
            },
            "message": {
                "text": "{}입니다. 선택해주세요.".format(content)
            }
        }
    elif content == "낮은 가격순":
                
        add_user_select_action(user_session=user_session, content=content)
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':low_price_top_10()
            },
            "message": {
                "text": "{}입니다. 선택해주세요.".format(content)
            }
        }
    elif content == "마감순":
        
        add_user_select_action(user_session=user_session, content=content)
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons': deadline_top_10()
            },
            "message": {
                "text": "{}입니다. 선택해주세요.".format(content)
            }
        }
    elif content == "최다 구매순":
                
        add_user_select_action(user_session=user_session, content=content)
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':popular_top_10()
            },
            "message": {
                "text": "{}입니다. 선택해주세요.".format(content)
            }
        }

        
    elif current_user_select_action(user_session=user_session) == "만족도순":
        
        add_user_select_app(user_session=user_session, app_id=is_exists_app_id(app_name=content))
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':check_button(app_id=is_exists_app_id(app_name=content))
            },
            "message": {
                "text": get_app_information(app_name=content)
            }
        }
    elif current_user_select_action(user_session=user_session) == "할인율순":
               
        add_user_select_app(user_session=user_session, app_id=is_exists_app_id(app_name=content))
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':check_button(app_id=is_exists_app_id(app_name=content))
            },
            "message": {
                "text": get_app_information(app_name=content)
            }
        }
    elif current_user_select_action(user_session=user_session) == "출시일순":
                
        add_user_select_app(user_session=user_session, app_id=is_exists_app_id(app_name=content))
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':check_button(app_id=is_exists_app_id(app_name=content))
            },
            "message": {
                "text": get_app_information(app_name=content)
            }
        }
    elif current_user_select_action(user_session=user_session) == "높은 가격순":
        
        add_user_select_app(user_session=user_session, app_id=is_exists_app_id(app_name=content))
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':check_button(app_id=is_exists_app_id(app_name=content))
            },
            "message": {
                "text": get_app_information(app_name=content)
            }
        }
    elif current_user_select_action(user_session=user_session) == "낮은 가격순":
                
        add_user_select_app(user_session=user_session, app_id=is_exists_app_id(app_name=content))
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':check_button(app_id=is_exists_app_id(app_name=content))
            },
            "message": {
                "text": get_app_information(app_name=content)
            }
        }
    elif current_user_select_action(user_session=user_session) == "마감순":
        
        add_user_select_app(user_session=user_session, app_id=is_exists_app_id(app_name=content))
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':check_button(app_id=is_exists_app_id(app_name=content))
            },
            "message": {
                "text": get_app_information(app_name=content)
            }
        }
    elif current_user_select_action(user_session=user_session) == "최다 구매순":
                
        add_user_select_app(user_session=user_session, app_id=is_exists_app_id(app_name=content))
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':check_button(app_id=is_exists_app_id(app_name=content))
            },
            "message": {
                "text": get_app_information(app_name=content)
            }
        }
        
    else:
        
        add_user_select_app(user_session=user_session, app_id=is_exists_app_id(app_name=content))
        dataSend = {
             'keyboard': {
                'type': 'buttons',
                'buttons':check_button(app_id=is_exists_app_id(app_name=content))
            },
            "message": {
                "text": get_app_information(app_name=content)
            }
        }
        
 
    return jsonify(dataSend)
 
 
 
if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 8886)