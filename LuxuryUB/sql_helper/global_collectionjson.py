from sqlalchemy import Column, UnicodeText, Integer, and_
from sqlalchemy_json import MutableJson, NestedMutableJson

from . import BASE, SESSION

class Cat_GlobalCollection_Json(BASE):
    __tablename__ = "luxury_collection_json" # اسم الجدول الجديد
    owner_id = Column(Integer, primary_key=True, nullable=False) # بصمة المالك
    keywoard = Column(UnicodeText, primary_key=True, nullable=False)
    json = Column(MutableJson)
    njson = Column(NestedMutableJson)

    def __init__(self, owner_id, keywoard, json, njson):
        self.owner_id = owner_id
        self.keywoard = keywoard
        self.json = json
        self.njson = njson

Cat_GlobalCollection_Json.__table__.create(checkfirst=True)

def get_collection(owner_id, keywoard):
    """جلب بيانات JSON الخاصة بمستخدم معين"""
    try:
        return SESSION.query(Cat_GlobalCollection_Json).filter(
            and_(
                Cat_GlobalCollection_Json.owner_id == owner_id,
                Cat_GlobalCollection_Json.keywoard == keywoard
            )
        ).first()
    finally:
        SESSION.close()

def add_collection(owner_id, keywoard, json, njson=None):
    """إضافة أو تحديث بيانات JSON لمستخدم معين"""
    if njson is None:
        njson = {}
    
    to_check = get_collection(owner_id, keywoard)
    if to_check:
        SESSION.delete(to_check)
        SESSION.commit()
        
    keyword_items = Cat_GlobalCollection_Json(owner_id, keywoard, json, njson)
    SESSION.add(keyword_items)
    SESSION.commit()
    return True

def del_collection(owner_id, keywoard):
    """حذف بيانات معينة لمستخدم معين"""
    to_check = get_collection(owner_id, keywoard)
    if not to_check:
        return False
    
    SESSION.delete(to_check)
    SESSION.commit()
    return True

def get_collections(owner_id):
    """جلب كل مجموعات الـ JSON الخاصة بمستخدم واحد فقط"""
    try:
        return SESSION.query(Cat_GlobalCollection_Json).filter(
            Cat_GlobalCollection_Json.owner_id == owner_id
        ).all()
    finally:
        SESSION.close()