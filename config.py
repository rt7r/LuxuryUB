from sample_config import Config

class Development(Config):
    # --- إعدادات الحساب الأساسية (تُجلب من my.telegram.org) ---
    APP_ID = خلي هنا الاب ايدي
    API_HASH = "خلي هنا الايبياي هاش"

    ALIVE_NAME = "Luxury User" #غيره وحط اسم حسابك
    
    DB_URI = "sqlite:///luxury.db" #لا تغير ولا تسوي اي شي

    # --- الجلسة والتوكن ---
    STRING_SESSION = "كود الجلسة"

    TG_BOT_TOKEN = "توكن"
    # توكن البوت المساعد من @BotFather

    #الباقي لا تغير منه اي شي
    COMMAND_HAND_LER = "."
    SUDO_COMMAND_HAND_LER = "."

    OWNER_ID = هنا 
#فوك خلي ايدي حسابك
    SUDO_USERS = [هنا, 1165225957] 
#فوك بجانب الايدي المحطوط حط ايدي حسابك مثل: 
#SUDO_USERS = [123456789, 1165225957] 

    UPSTREAM_REPO = "https://github.com/rt7r/LuxuryUB"
    UPSTREAM_BRANCH = "main"

    PRIVATE_GROUP_BOT_API_ID = 0 # ايدي كروب السجل (Log)
    PM_LOGGER_GROUP_ID = 0 # ايدي كروب سجل الخاص