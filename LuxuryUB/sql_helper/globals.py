try:
    from . import BASE, SESSION
except ImportError as e:
    raise AttributeError from e

from sqlalchemy import Column, String, UnicodeText, Integer, and_

class Globals(BASE):
    __tablename__ = "luxury_globals" # تغيير الاسم لتمييزه عن السورس القديم
    owner_id = Column(Integer, primary_key=True, nullable=False) # معرف مالك الحساب
    variable = Column(String, primary_key=True, nullable=False)
    value = Column(UnicodeText, nullable=False)

    def __init__(self, owner_id, variable, value):
        self.owner_id = owner_id
        self.variable = str(variable)
        self.value = value

Globals.__table__.create(checkfirst=True)

def gvarstatus(owner_id, variable):
    """جلب قيمة المتغير بناءً على ايدي المالك واسم المتغير"""
    try:
        result = (
            SESSION.query(Globals)
            .filter(and_(Globals.owner_id == owner_id, Globals.variable == str(variable)))
            .first()
        )
        return result.value if result else None
    except Exception:
        return None
    finally:
        SESSION.close()

def addgvar(owner_id, variable, value):
    """إضافة أو تحديث متغير لمستخدم معين"""
    existing = SESSION.query(Globals).filter(
        and_(Globals.owner_id == owner_id, Globals.variable == str(variable))
    ).one_or_none()
    
    if existing:
        delgvar(owner_id, variable)
        
    adder = Globals(owner_id, str(variable), value)
    SESSION.add(adder)
    SESSION.commit()

def delgvar(owner_id, variable):
    """حذف متغير خاص بمستخدم معين"""
    rem = (
        SESSION.query(Globals)
        .filter(and_(Globals.owner_id == owner_id, Globals.variable == str(variable)))
        .delete(synchronize_session="fetch")
    )
    if rem:
        SESSION.commit()