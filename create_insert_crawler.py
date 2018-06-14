from datetime import datetime
import time
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select, exists, update
from sqlalchemy import and_, desc
from models import *
from utils import *


while(True):
    if datetime.now().hour == 1:
        start_time = time.time() 
        driver = setting_selenium()
        driver = main_hompage_get(driver=driver)
        detail_sale_url = get_detail_sales_url(selenium=driver)
        total_result, publisher_collect, developer_collect = detail_sales_url_crawler(detail_sale_url=detail_sale_url,selenium=driver)
        time.sleep(10)
        driver = main_hompage_get(driver=driver)
        total_result = main_homepage_crawler(total_result=total_result,selenium=driver)
        print("--- %s seconds ---" %(time.time() - start_time))
        app_type_collect = list(set([i.get('App Type','Package') for i in total_result]))
        write_pickle('total_result', total_result)
        write_pickle('publisher_collect', list(set(publisher_collect)))
        write_pickle('developer_collect', list(set(developer_collect)))
        write_pickle('app_type_collect', list(set(app_type_collect)))
        total_result = read_pickle('total_result')
        publisher_collect = read_pickle('publisher_collect')
        developer_collect = read_pickle('developer_collect')
        app_type_collect = read_pickle('app_type_collect')
        
        create_db()
        engine = sqlalchemy.create_engine(get_db_information())
        engine.connect()
        Session = sessionmaker(bind=engine)
        session = Session()
        publisher_collect = ['unknown'] + publisher_collect
        for publisher in publisher_collect:
            if session.query(exists().where(PUBLISHER.publisher_name==publisher)).scalar():
                continue
            else:
                session.add(PUBLISHER(publisher))
        session.commit()
        session.close()
        developer_collect = ['unknown'] + developer_collect
        for developer in developer_collect:
            if session.query(exists().where(DEVELOPER.developer_name==developer)).scalar():
                continue
            else:
                session.add(DEVELOPER(developer))
        session.commit()
        session.close()
        
        for app_type in app_type_collect:
            if session.query(exists().where(GAME.game_name==app_type)).scalar():
                continue
            else:
                session.add(GAME(app_type))
        session.commit()
        session.close()
        
        
        for instance in total_result:
            if session.query(TOTAL_APP).filter(TOTAL_APP.app_id==int(instance['App ID'])).filter(TOTAL_APP.price==str(instance['Price'])).scalar():
                continue
            elif session.query(TOTAL_APP).filter(TOTAL_APP.app_id==int(instance['App ID'])).filter(TOTAL_APP.price!=str(instance['Price'])).scalar():
                session.query(TOTAL_APP).filter(TOTAL_APP.app_id==int(instance['App ID'])).update({"price":str(instance['Price'])})
            else:
                pub_id = session.query(PUBLISHER.publisher_id).filter(PUBLISHER.publisher_name==instance.get('Publisher','unknown')).all()
                dev_id = session.query(DEVELOPER.developer_id).filter(DEVELOPER.developer_name==instance.get('Developer','unknown')).all()
                game_id = session.query(GAME.game_id).filter(GAME.game_name==instance.get('App Type','Package')).all()
                session.add(TOTAL_APP(app_id=instance['App ID'],app_name=instance['Name'],app_type=game_id[0][0],\
                                      developer_id=dev_id[0][0],price=str(instance['Price']),publisher_id=pub_id[0][0],rating=instance['Rating'],\
                                      release_date='1900-01-01'if instance['Release Date'] == '' else instance['Release Date']))
        session.commit()
        session.close()   
        
        session.query(DISCOUNT_APP).delete()
        session.commit()
        session.close()   

        for instance in total_result:
            if session.query(exists().where(DISCOUNT_APP.app_id==int(instance['App ID']))).scalar():
                continue
            else:
                session.add(DISCOUNT_APP(app_id=instance['App ID'],start_date=instance['Start Date'],end_date=instance['End Date'],\
                                         discount_rate=instance['Discount Rate']))
        session.commit()
        session.close()  
        
        button_collection = [[0,"쇼핑", None],
                     [1,"내 기록", None],
                     [2,"이름 검색", 0],
                     [3,"top10 조회", 0],
                     [4,"만족도순", 3],  #1
                     [5,"할인율순", 3],  #2 
                     [6,"출시일순", 3],   # 3
                     [7,"높은 가격순", 3],  # 4 
                     [8,"낮은 가격순", 3],  # 5
                     [9,"마감순", 3],   # 6
                     [10,"최다 구매순", 3],  # 7
                     [11,"만족도순_1",9998],
                     [12,"할인율순_1",9998],
                     [13,"출시일순_1",9998],
                     [14,"높은 가격순_1",9998],
                     [15,"낮은 가격순_1",9998],
                     [16,"마감순_1",9998],
                     [17,"최다 구매순_1",9998],
                     [18,"장바구니 목록", 1],
                     [19,"구매 목록", 1],
                     [20,"장바구니 취소", 9999],
                     [21,"구매 취소", 9999],
                     [22,"장바구니", 9999],
                     [23,"구매하기", 9999]]
        
        for instance in button_collection:
            if session.query(exists().where(BUTTONS.category_id ==instance[0])).scalar():
                continue
            else:
                session.add(BUTTONS(category_id=instance[0],button_name=instance[1],parent_id=instance[2]))
        session.commit()
        session.close()  
        
    else:
        time.sleep(3600)
        