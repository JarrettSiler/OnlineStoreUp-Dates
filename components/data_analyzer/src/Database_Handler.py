import os,sys, os.path
from sqlalchemy import create_engine, Column, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
sys.path.append(root_dir)


class dbEntry(Base):
    __tablename__ = 'Listings'

    itemName = Column('itemName', String, primary_key=True)
    itemPrice = Column('itemPrice', String)
    itemLocation = Column('itemLocation', String)
    itemInfo = Column('itemInfo', String)
    itemURL = Column('itemURL', String)

def is_existing(fileName):
    path = os.path.join(root_dir, 'database_storage', 'Watchlist', f"{fileName}.db")
    if os.path.isfile(path):
        return True
    else:
        return False
    
def check_for_new_items(fileName):
    watchlist_path = os.path.join(root_dir, 'database_storage', 'Watchlist', f"{fileName}.db")
    tba_path = os.path.join(root_dir, 'database_storage', 'To Be Analyzed', f"{fileName}.db")

    #create engines
    watchlist_engine = create_engine(f"sqlite:///{watchlist_path}", echo=True)
    tba_engine = create_engine(f"sqlite:///{tba_path}", echo=True)
    Base.metadata.bind = tba_engine

    WLSession = sessionmaker(bind=watchlist_engine)
    TBASession = sessionmaker(bind=tba_engine)
    wlsession = WLSession()
    tbasession = TBASession()

    # Query all entries in the Listings table for both databases
    wllistings = wlsession.query(dbEntry).all()
    tbalistings = tbasession.query(dbEntry).all()

    # compare item entries in each dabatbase:
    new_items = []
    
    for tbalisting in tbalistings:
        found = False
        new_item = [
            tbalisting.itemName,
            tbalisting.itemPrice,
            tbalisting.itemInfo,
            tbalisting.itemLocation,
            tbalisting.itemURL,
        ]

        for wllisting in wllistings:
            existing_item = [
                wllisting.itemName,
                wllisting.itemPrice,
                wllisting.itemInfo,
                wllisting.itemLocation,
                wllisting.itemURL,
            ]

            if new_item == existing_item:
                found = True
                break

        if not found:
            new_items.append(new_item)

    # Find items in the second database that are not in the first

    wlsession.close()
    watchlist_engine.dispose()
    tbasession.close()
    tba_engine.dispose()

    return new_items

def get_item_count(fileName): #returns number of items in db
    watchlist_path = os.path.join(root_dir, 'database_storage', 'Watchlist', f"{fileName}.db")
    watchlist_engine = create_engine(f"sqlite:///{watchlist_path}", echo=True)
    
    WLSession = sessionmaker(bind=watchlist_engine)
    wlsession = WLSession()

    try:
        # Use the func.count() function to get the count of items in the Listings table
        item_count = wlsession.query(func.count(dbEntry.itemName)).scalar()
        return str(item_count)
    except Exception as e:
        print(f"Error getting item count: {e}")
        return None
    finally:
        wlsession.close()
        watchlist_engine.dispose()