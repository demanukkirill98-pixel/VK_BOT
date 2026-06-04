import vk_api
import mysql.connector
import time
import threading

VK_TOKEN = "vk1.a.xie8b5Il8ehezLE3JOCsIBTP3TeENvzecg8d5PRfGiU4RNqHDW9L4bRyz_1M6fz32BegIOViPNJpokpHpKUFuT_E5cKsmFk2sy9PNXTIfZ1BUTs4nUJos7QC1if9IXV4QT_kO3MCbR6b4yHYikjUeb4I9_uZ-YGsdYlY6crCk0dQ1VS2kGGUW49TgweKafX-vognYAwuHxuvHswMC3whaQ"
ADMIN_VK_IDS = [835770623]
BOT_GROUP_ID = -239035916

DB_CONFIG = {
    'host': '149.202.88.119',
    'user': 'gs341801',
    'password': 'X0w20ypr9q0B',
    'database': 'gs341801',
    'connect_timeout': 5
}

def set_admin_in_db(player_name, level):
    conn = None
    cursor = None
    try:
        print(f"🟡 [1/4] Подключаюсь к БД {DB_CONFIG['host']}...")
        conn = mysql.connector.connect(**DB_CONFIG)
        print(f"🟢 [2/4] Подключено!")
        
        cursor = conn.cursor()
        print(f"🟡 [3/4] Выполняю UPDATE...")
        
        cursor.execute("UPDATE accounts SET admin = %s WHERE name = %s", (level, player_name))
        conn.commit()
        print(f"🟢 [4/4] Запрос выполнен, изменено строк: {cursor.rowcount}")
        
        if cursor.rowcount > 0:
            return True, f"✅ {player_name} получил {level} уровень админа"
        return False, f"❌ Игрок {player_name} не найден"
        
    except mysql.connector.Error as e:
        print(f"🔴 Ошибка MySQL: {e}")
        return False, f"❌ Ошибка БД: {e}"
    except Exception as e:
        print(f"🔴 Ошибка: {e}")
        return False, f"❌ Ошибка: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("🔌 Соединение закрыто")

vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()

def send_message(user_id, text):
    try:
        vk.messages.send(user_id=user_id, message=text, random_id=0)
        print(f"📤 Ответ отправлен: {text[:40]}...")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

def process_command(user_id, text, user_name):
    print(f"👤 Обработка команды от {user_name}")
    parts = text.split()
    if len(parts) != 3:
        send_message(user_id, "❌ /setadmin [ник] [уровень 1-13]")
        return
    nick, level = parts[1], parts[2]
    if not level.isdigit() or int(level) < 1 or int(level) > 13:
        send_message(user_id, "❌ Уровень 1-13")
        return
    
    send_message(user_id, f"🔄 Выдаю {nick} {level} уровень...")
    success, result = set_admin_in_db(nick, int(level))
    send_message(user_id, result)

def get_user_name(user_id):
    if user_id < 0:
        return "Группа"
    try:
        user = vk.users.get(user_ids=user_id)
        return f"{user[0]['first_name']} {user[0]['last_name']}"
    except:
        return f"ID{user_id}"

def check_messages():
    try:
        messages = vk.messages.getConversations(offset=0, count=10, filter_unread=1)
        items = messages.get('items', [])
        if not items:
            return
        
        for item in items:
            msg = item['last_message']
            user_id = msg['from_id']
            text = msg['text'].strip()
            
            if user_id == BOT_GROUP_ID:
                continue
            if user_id not in ADMIN_VK_IDS:
                print(f"⚠️ Доступ запрещен: {get_user_name(user_id)}")
                continue
            
            user_name = get_user_name(user_id)
            print(f"📩 {user_name}: {text}")
            
            if text.lower().startswith('/setadmin'):
                threading.Thread(target=process_command, args=(user_id, text, user_name), daemon=True).start()
            
            vk.messages.markAsRead(peer_id=user_id)
    except Exception as e:
        print(f"❌ Ошибка check_messages: {e}")

print("=" * 50)
print("✅ VK Админ-бот (БД версия)")
print(f"👑 Ваш ID: {ADMIN_VK_IDS[0]}")
print("💬 /setadmin [ник] [уровень 1-13]")
print("=" * 50)

while True:
    try:
        check_messages()
        time.sleep(2)
    except KeyboardInterrupt:
        print("\n❌ Бот остановлен")
        break
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        time.sleep(5)
