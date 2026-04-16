import threading
from sqlalchemy import Column, PickleType, UnicodeText, distinct, func, Integer, and_
from . import BASE, SESSION

class Cat_GlobalCollection(BASE):
    __tablename__ = "luxury_global_collection" # اسم الجدول المحدث
    owner_id = Column(Integer, primary_key=True, nullable=False) # بصمة المالك
    keywoard = Column(UnicodeText, primary_key=True)
    contents = Column(PickleType, primary_key=True, nullable=False)

    def __init__(self, owner_id, keywoard, contents):
        self.owner_id = owner_id
        self.keywoard = keywoard
        self.contents = tuple(contents)

    def __repr__(self):
        return "<Luxury Global Collection (Owner: %s) lists '%s' for %s>" % (
            self.owner_id, self.contents, self.keywoard,
        )

# إنشاء الجدول
Cat_GlobalCollection.__table__.create(checkfirst=True)
CAT_GLOBALCOLLECTION = threading.RLock()

class COLLECTION_SQL:
    def __init__(self):
        # تحويل الذاكرة لهيكل يدعم تعدد المستخدمين: {owner_id: {keyword: set()}}
        self.CONTENTS_LIST = {}

COLLECTION_SQL_ = COLLECTION_SQL()

def add_to_collectionlist(owner_id, keywoard, contents):
    with CAT_GLOBALCOLLECTION:
        keyword_items = Cat_GlobalCollection(owner_id, keywoard, tuple(contents))
        SESSION.merge(keyword_items)
        SESSION.commit()
        
        # تحديث الذاكرة المؤقتة للمالك المحدد
        if owner_id not in COLLECTION_SQL_.CONTENTS_LIST:
            COLLECTION_SQL_.CONTENTS_LIST[owner_id] = {}
        COLLECTION_SQL_.CONTENTS_LIST[owner_id].setdefault(keywoard, set()).add(tuple(contents))

def rm_from_collectionlist(owner_id, keywoard, contents):
    with CAT_GLOBALCOLLECTION:
        keyword_items = SESSION.query(Cat_GlobalCollection).filter(
            and_(
                Cat_GlobalCollection.owner_id == owner_id,
                Cat_GlobalCollection.keywoard == keywoard,
                Cat_GlobalCollection.contents == tuple(contents)
            )
        ).first()
        
        if keyword_items:
            if owner_id in COLLECTION_SQL_.CONTENTS_LIST:
                if tuple(contents) in COLLECTION_SQL_.CONTENTS_LIST[owner_id].get(keywoard, set()):
                    COLLECTION_SQL_.CONTENTS_LIST[owner_id].get(keywoard, set()).remove(tuple(contents))
            SESSION.delete(keyword_items)
            SESSION.commit()
            return True
        return False

def is_in_collectionlist(owner_id, keywoard, contents):
    with CAT_GLOBALCOLLECTION:
        if owner_id not in COLLECTION_SQL_.CONTENTS_LIST:
            return False
        keyword_items = COLLECTION_SQL_.CONTENTS_LIST[owner_id].get(keywoard, set())
        return any(tuple(contents) == list1 for list1 in keyword_items)

def del_keyword_collectionlist(owner_id, keywoard):
    with CAT_GLOBALCOLLECTION:
        SESSION.query(Cat_GlobalCollection).filter(
            and_(Cat_GlobalCollection.owner_id == owner_id, Cat_GlobalCollection.keywoard == keywoard)
        ).delete()
        if owner_id in COLLECTION_SQL_.CONTENTS_LIST:
            COLLECTION_SQL_.CONTENTS_LIST[owner_id].pop(keywoard, None)
        SESSION.commit()

def get_item_collectionlist(owner_id, keywoard):
    if owner_id not in COLLECTION_SQL_.CONTENTS_LIST:
        return set()
    return COLLECTION_SQL_.CONTENTS_LIST[owner_id].get(keywoard, set())

def get_collectionlist_items(owner_id):
    try:
        chats = SESSION.query(Cat_GlobalCollection.keywoard).filter(
            Cat_GlobalCollection.owner_id == owner_id
        ).distinct().all()
        return [i[0] for i in chats]
    finally:
        SESSION.close()

# دالة التحميل عند تشغيل السورس (محدثة لكل المستخدمين)
def __load_item_collectionlists():
    try:
        all_data = SESSION.query(Cat_GlobalCollection).all()
        for x in all_data:
            if x.owner_id not in COLLECTION_SQL_.CONTENTS_LIST:
                COLLECTION_SQL_.CONTENTS_LIST[x.owner_id] = {}
            if x.keywoard not in COLLECTION_SQL_.CONTENTS_LIST[x.owner_id]:
                COLLECTION_SQL_.CONTENTS_LIST[x.owner_id][x.keywoard] = []
            COLLECTION_SQL_.CONTENTS_LIST[x.owner_id][x.keywoard] += [x.contents]

        # تحويل القوائم إلى مجموعات (Sets) لسرعة البحث
        for owner in COLLECTION_SQL_.CONTENTS_LIST:
            for kw in COLLECTION_SQL_.CONTENTS_LIST[owner]:
                COLLECTION_SQL_.CONTENTS_LIST[owner][kw] = set(COLLECTION_SQL_.CONTENTS_LIST[owner][kw])
    finally:
        SESSION.close()

__load_item_collectionlists()