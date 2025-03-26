import telebot
import requests
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# Bot & API Credentials
BOT_TOKEN = "7645346698:AAFpJwDQYBvyrJdYtyPdhEXkSBH9b_wBNYU"
bot = telebot.TeleBot(BOT_TOKEN)

SMM_KOCH_API = "a2ff33e3c254400aadd5d5414a1f248a8ac33636"
SMM_KOCH_URL = "https://cheapsmmmarket.com/api/v2"
REQUIRED_CHANNELS = ["@UniqueEnoughBGMI", "@NewOneCool"]  # Replace with actual channel usernames
ADMIN_CHAT_ID = 6966950770
BALANCE_FILE = "wallet.txt"

SERVICE_PRICES = {
    "23337": 4,    # Views
    "23712": 6,   # Likes
    "23320": 100,  # Followers
    "22386": 70, #Telegram Subscribers 
    "22463": 10, #Telegram Likes 
    "23286": 5, #Telegram Views
}

active_users = {}
admin_states = {}  # Dictionary to track admin actions

# -------- Reply Keyboards --------
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("Demo Video 📷"))
    markup.row(KeyboardButton("📌 Order"), KeyboardButton("💰 Prices"))
    markup.row(KeyboardButton("Get Credits"), KeyboardButton("Refer For 2 Credit"))
    markup.row(KeyboardButton("💳 Check Balance"), KeyboardButton("📦 Track Order"))
    markup.row(KeyboardButton("🔐 Admin Panel"))
    return markup

def order_platform_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("📷 Instagram"), KeyboardButton("✈️ Telegram"), KeyboardButton("▶️ YouTube"))
    markup.row(KeyboardButton("🔙 Back to Main Menu"))
    return markup

def cancel_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("❌ Cancel Order"))
    return markup

def show_all_users():
    users_data = []
    
    # Load all registered users
    if not os.path.exists("users.txt"):
        return "❌ No users found."
    
    with open("users.txt", "r") as file:
        user_ids = file.read().splitlines()

    # Fetch balances from wallet.txt
    balances = {}
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, "r") as file:
            for line in file:
                user_data = line.strip().split(",")
                if len(user_data) == 2:
                    user_id, balance = user_data
                    balances[user_id] = balance

    # Prepare the user list
    for user_id in user_ids:
        balance = balances.get(user_id, "0")  # Default balance is 0 if not found
        users_data.append(f"👤 User: `{user_id}` | 💰 Balance: `{balance}` credits")

    return "\n".join(users_data) if users_data else "❌ No users found."

# -------- User Functions --------
def get_balance(user_id):
    try:
        with open(BALANCE_FILE, "r") as file:
            for line in file:
                user_data = line.strip().split(",")
                if len(user_data) == 2 and user_data[0] == str(user_id):
                    return float(user_data[1])
        return 0.0
    except:
        return 0.0

def set_balance(user_id, new_balance):
    users = {}

    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, "r") as file:
            for line in file:
                try:
                    user, balance = line.strip().split(",")
                    users[user] = float(balance)
                except:
                    continue

    users[str(user_id)] = new_balance

    with open(BALANCE_FILE, "w") as file:
        for user, balance in users.items():
            file.write(f"{user},{balance}\n")

def admin_panel_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("➕ Add Coins"), KeyboardButton("💰 Check SMM Balance"))
    markup.row(KeyboardButton("📜 View All Orders"), KeyboardButton("📋 Show Users"))
    markup.row(KeyboardButton("📢 Broadcast"))
    markup.row(KeyboardButton("🔙 Back to Main Menu"))
    return markup

@bot.message_handler(func=lambda message: message.text == "Get Credits")
def send_credit_info(message):
    photo_path = "credit.jpg"  # Make sure this file exists in the same directory as your bot script
    caption = "Pay to this QR and send screenshot to @UniqueParadox_bot.\n\nPrice 💵 -\n\n10 Credits - 10₹\n20 Credits - 19₹\n50 Credits - 45₹\n100 Credits - 90₹"
    
    with open(photo_path, "rb") as photo:
        bot.send_photo(message.chat.id, photo, caption=caption)

def get_full_order_status(order_id):
    try:
        response = requests.post(SMM_KOCH_URL, data={
            "key": SMM_KOCH_API,
            "action": "status",
            "order": order_id
        })

        if response.status_code != 200:
            return f"❌ HTTP Error {response.status_code}"

        data = response.json()
        print(f"Order Status API Response: {data}")  # Debugging

        if "error" in data:
            return f"❌ API Error: {data.get('error', 'Unknown error')}"

        status = data.get("status", "Unknown")
        quantity = data.get("quantity", "N/A")
        start_count = int(data.get("start_count", 0))  # Convert to integer
        remaining = int(data.get("remains", 0))  # Convert to integer
        completed = start_count - remaining  # Now subtraction works
        link = data.get("link", "N/A")
        service_name = data.get("service", "N/A")  # Some APIs return service ID; adjust if needed

        # Convert remaining count to "Fully Completed" if it's zero
        remaining_text = "✅ Fully Completed" if remaining == 0 else f"❌ Remaining - {remaining}"

        return (
            f"📌 **Order ID:** `{order_id}`\n"
            f"🔗 **Link:** {link}\n"
            f"🛒 **Service:** {service_name}\n"
            f"📦 **Quantity:** {quantity}\n"
            f"🚀 **Start Count:** {start_count}\n"
            f"✅ **Completed:** {completed}\n"
            f"📊 **Status:** {status}\n"
            f"{remaining_text}"
        )

    except requests.exceptions.RequestException as e:
        return f"❌ Network Error: {str(e)}"
    except ValueError:
        return "❌ Data Error: Unable to process order details."


@bot.message_handler(func=lambda message: message.text == "📜 View All Orders")
def view_all_orders(message):
    if message.chat.id != ADMIN_CHAT_ID:
        bot.send_message(message.chat.id, "❌ This function is for admin only.")
        return

    if not os.path.exists("orders.txt"):
        bot.send_message(ADMIN_CHAT_ID, "❌ No orders found.")
        return

    with open("orders.txt", "r") as f:
        orders = [line.strip().split(",") for line in f.readlines()]

    if not orders:
        bot.send_message(ADMIN_CHAT_ID, "❌ No orders found.")
        return

    order_messages = []
    for order in orders:
        user_id, order_id = order
        order_details = get_full_order_status(order_id)

        order_messages.append(f"👤 User: `{user_id}`\n{order_details}")

    response_text = "\n\n".join(order_messages) if order_messages else "❌ No orders found."
    
    bot.send_message(ADMIN_CHAT_ID, f"📜 **All Orders:**\n\n{response_text}", parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.text == "Demo Video 📷")
def send_demo_video(message):
    video_path = "demo.mp4"  # Ensure this file exists in the same directory as your script
    caption = "📽️ Watch this video before using."

    try:
        with open(video_path, "rb") as video:
            bot.send_video(message.chat.id, video, caption=caption)
    except FileNotFoundError:
        bot.send_message(message.chat.id, "❌ Demo video not found. Please contact support.")


@bot.message_handler(func=lambda message: message.text == "🔐 Admin Panel")
def admin_panel(message):
    if message.chat.id != ADMIN_CHAT_ID:
        bot.send_message(message.chat.id, "❌ This function is for admin only.")
        return

    admin_states.pop(message.chat.id, None)  # Reset admin state when entering the panel
    bot.send_message(message.chat.id, "👑 Admin Panel", reply_markup=admin_panel_menu())

@bot.message_handler(func=lambda message: message.text == "➕ Add Coins")
def ask_for_user_id(message):
    if message.chat.id != ADMIN_CHAT_ID:
        bot.send_message(message.chat.id, "❌ This function is for admin only.")
        return

    admin_states[message.chat.id] = "waiting_for_user_id"
    bot.send_message(message.chat.id, "Enter User ID and Amount (Format: user_id amount)")

@bot.message_handler(func=lambda message: message.chat.id in admin_states and admin_states[message.chat.id] == "waiting_for_user_id")
def add_coins(message):
    if message.chat.id != ADMIN_CHAT_ID:
        bot.send_message(message.chat.id, "❌ This function is for admin only.")
        return

    try:
        user_id, amount = message.text.split()
        user_id, amount = int(user_id), float(amount)

        current_balance = get_balance(user_id)
        new_balance = current_balance + amount
        set_balance(user_id, new_balance)

        bot.send_message(message.chat.id, f"✅ Added {amount} credits to {user_id}. New Balance: {new_balance}")
        bot.send_message(user_id, f"🎉 Admin added {amount} credits to your balance. New Balance: {new_balance}")

        admin_states.pop(message.chat.id, None)  # ✅ Reset state after successful input
    except:
        bot.send_message(message.chat.id, "❌ Invalid format! Use: user_id amount")

def check_smm_balance():
    try:
        response = requests.post("https://cheapsmmmarket.com/api/v2", data={
            "key": "a2ff33e3c254400aadd5d5414a1f248a8ac33636",  # Replace with your actual API key
            "action": "balance"
        })
        
        # Log the raw response to debug
        print("SMM Balance Response:", response.text)

        if response.status_code != 200:
            return f"❌ HTTP Error {response.status_code}"

        data = response.json()
        
        if "balance" in data:
            return f"💰 SMM Balance: {data['balance']} Rs."
        else:
            return f"❌ API Error: {data.get('error', 'Unknown error')}"
    
    except requests.exceptions.RequestException as e:
        return f"❌ Network Error: {str(e)}"

@bot.message_handler(func=lambda message: message.text == "💰 Check SMM Balance")
def smm_balance(message):
    if message.chat.id != ADMIN_CHAT_ID:
        bot.send_message(message.chat.id, "❌ This function is for admin only.")
        return

    balance_info = check_smm_balance()
    bot.send_message(message.chat.id, balance_info)


@bot.message_handler(func=lambda message: message.text == "Refer For 2 Credit")
def generate_referral_link(message):
    user_id = message.chat.id
    referral_link = f"https://t.me/MoyeInstaBooserBot?start={user_id}"  # Replace 'YOUR_BOT_USERNAME' with your bot's username
    
    bot.send_message(user_id, f"🔗 Share this referral link:\n{referral_link}\n\n👥 When someone joins using your link, you both get 2 credits!")


def is_member(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            chat_member = bot.get_chat_member(channel, user_id)
            if chat_member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True


# -------- Bot Handlers --------
@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.chat.id)
    text = message.text.strip()
    referred_by = None

    # Check if the user joined via a referral link
    if " " in text:
        referred_by = text.split()[1]

    # ✅ Restrict access if user hasn't joined all channels
    if not is_member(message.chat.id):
        bot.send_message(message.chat.id, 
                         "⚠️ You must join all required channels to use this bot.\n\n"
                         "Join these channels:\n" +
                         "\n".join([f"🔗 {channel}" for channel in REQUIRED_CHANNELS]) +
                         "\n\nAfter joining, press /start again.")
        return

    # ✅ Register the user if not already registered
    with open("users.txt", "a+") as file:
        file.seek(0)
        users = file.read().splitlines()
        if user_id not in users:
            file.write(f"{user_id}\n")

            # ✅ Referral Bonus (Only if the user has joined all channels)
            if referred_by and referred_by.isdigit() and is_member(user_id):
                referrer_id = int(referred_by)

                # Add 2 credits to both referrer and new user
                set_balance(referrer_id, get_balance(referrer_id) + 2)
                set_balance(user_id, get_balance(user_id) + 2)

                bot.send_message(referrer_id, "🎉 Someone joined using your referral link! You earned 2 credits!")
                bot.send_message(user_id, "🎉 You joined through a referral link! You got 2 credits!")

    bot.send_message(user_id, "Welcome! Use the buttons below to navigate:", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "💰 Prices")
def show_prices(message):
    prices_text = "\n".join([
        f"📌 {service_name} (ID: {service_id}) - {price} credits per 1000"
        for service_id, (service_name, price) in {
            "23337": ("Views", 4),
            "23712": ("Likes", 6),
            "23320": ("Followers", 100),
            "23286": ("👀 Views", 5),
            "22463": ("❤️ Likes", 10),
            "22386": ("👥 Members", 70),
        }.items()
    ])
    
    bot.send_message(message.chat.id, f"💰 Service Prices:\n\n{prices_text}", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "💳 Check Balance")
def check_balance(message):
    user_id = message.chat.id
    balance = get_balance(user_id)
    bot.send_message(user_id, f"💰 Your balance: {balance} credits", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "📌 Order")
def order(message):
    bot.send_message(message.chat.id, "Choose a platform:", reply_markup=order_platform_menu())

@bot.message_handler(func=lambda message: message.text in ["📷 Instagram", "✈️ Telegram", "▶️ YouTube"])
def select_platform(message):
    platform = message.text

    if platform == "📷 Instagram":
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(KeyboardButton("📺 Views"), KeyboardButton("❤️ Likes"), KeyboardButton("👥 Followers"))
    elif platform == "✈️ Telegram":
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(KeyboardButton("👀 Views"), KeyboardButton("🔥 Reactions"), KeyboardButton("👥 Members"))
    elif platform == "▶️ YouTube":
        bot.send_message(message.chat.id, "🎥 Use this bot to boost your YouTube channel: @MoyeYTBot")
        return  # No buttons needed for YouTube

    markup.row(KeyboardButton("🔙 Back to Order Menu"))
    bot.send_message(message.chat.id, f"Choose a service for {platform}:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in ["📺 Views", "❤️ Likes", "👥 Followers", "YT Views", "YT Likes", "YT Subscribers", "👀 Views", "🔥 Reactions", "👥 Members"])
def select_order_service(message):
    user_id = message.chat.id
    service_map = {"📺 Views": "23337", "❤️ Likes": "23712", "👥 Followers": "23320", "YT Views": "3928", "YT Likes": "3937", "YT Subscribers": "3781", "👀 Views": "23286", "🔥 Reactions": "22463", "👥 Members": "22386"}
    service_id = service_map[message.text]

    active_users[user_id] = {"service_id": service_id}
    bot.send_message(user_id, "Send the link and quantity (Example: https://instagram.com/p/example 1000)", reply_markup=cancel_menu())

@bot.message_handler(func=lambda message: message.text == "📋 Show Users")
def handle_show_users(message):
    if message.chat.id != ADMIN_CHAT_ID:
        bot.send_message(message.chat.id, "❌ This function is for admin only.")
        return

    users_info = show_all_users()
    bot.send_message(message.chat.id, f"📋 **All Users & Balances:**\n\n{users_info}", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in active_users)
def process_order(message):
    user_id = message.chat.id
    text = message.text.strip()

    if text == "❌ Cancel Order":
        active_users.pop(user_id)
        bot.send_message(user_id, "❌ Order cancelled.", reply_markup=main_menu())
        return

    # Ensure the user has selected a service before proceeding
    if user_id not in active_users or "service_id" not in active_users[user_id]:
        bot.send_message(user_id, "❌ You haven't selected a service. Please start your order again.", reply_markup=main_menu())
        return

    try:
        parts = text.split()
        if len(parts) != 2:
            raise ValueError

        link, quantity = parts[0], int(parts[1])

        if quantity < 500:
            bot.send_message(user_id, "❌ Minimum order quantity is 500.", reply_markup=main_menu())
            return

        service_id = active_users[user_id]["service_id"]

        if not link.startswith("http"):
            bot.send_message(user_id, "❌ Invalid link! Order cancelled.", reply_markup=main_menu())
            active_users.pop(user_id)
            return

        user_balance = get_balance(user_id)
        order_cost = (quantity / 1000) * SERVICE_PRICES[service_id]

        if user_balance < order_cost:
            bot.send_message(user_id, "❌ Insufficient balance!", reply_markup=main_menu())
            active_users.pop(user_id)
            return

        response = place_order(service_id, link, quantity)

        if response.get("status") == "success":
            order_id = response.get("order_id")
            new_balance = user_balance - order_cost
            set_balance(user_id, new_balance)

            # Save order ID to file
            with open("orders.txt", "a") as f:
                f.write(f"{user_id},{order_id}\n")

            bot.send_message(user_id, f"✅ Order placed successfully!\n📌 Order ID: `{order_id}`\n💰 Remaining Balance: {new_balance}\n\nUse 'Track Order' to check progress.", parse_mode="Markdown", reply_markup=main_menu())

        else:
            bot.send_message(user_id, f"❌ Order failed: {response.get('error', 'Unknown error')}", reply_markup=main_menu())

        active_users.pop(user_id)

    except ValueError:
        bot.send_message(user_id, "❌ Wrong format! Order cancelled.", reply_markup=main_menu())
        active_users.pop(user_id)

def place_order(service_id, link, quantity):
    try:
        payload = {
            "key": SMM_KOCH_API,
            "action": "add",
            "service": service_id,
            "link": link,
            "quantity": quantity
        }
        response = requests.post(SMM_KOCH_URL, data=payload)

        if response.status_code != 200:
            return {"status": "failed", "error": f"HTTP {response.status_code}"}

        data = response.json()
        if "error" in data:
            return {"status": "failed", "error": data["error"]}

        return {"status": "success", "order_id": data.get("order")}

    except requests.exceptions.RequestException as e:
        return {"status": "failed", "error": str(e)}

@bot.message_handler(func=lambda message: message.text == "🔙 Back to Main Menu")
def back_to_main(message):
    print(f"User {message.chat.id} clicked 'Back to Main Menu'")  # ✅ Debugging

    # ✅ Remove old keyboard to prevent conflicts
    bot.send_message(message.chat.id, "Returning to Main Menu...", reply_markup=telebot.types.ReplyKeyboardRemove())

    # ✅ Send the main menu with a slight delay for better UI experience
    bot.send_message(message.chat.id, "Welcome back! Choose an option:", reply_markup=main_menu())


@bot.message_handler(func=lambda message: message.text == "📦 Track Order")
def track_orders(message):
    user_id = str(message.chat.id)

    if not os.path.exists("orders.txt"):
        bot.send_message(user_id, "❌ No orders found.")
        return

    with open("orders.txt", "r") as f:
        orders = [line.strip().split(",") for line in f.readlines()]

    user_orders = [o[1] for o in orders if o[0] == user_id]  # Extract order IDs for the user

    if not user_orders:
        bot.send_message(user_id, "❌ No orders found.")
        return

    status_messages = []
    for order_id in user_orders:
        status = get_order_status(order_id)
        if status:
            status_messages.append(f"📌 Order `{order_id}` - {status}")

    response_text = "\n\n".join(status_messages) if status_messages else "❌ No order statuses found."
    
    bot.send_message(user_id, response_text, parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.chat.id in active_users and "tracking" in active_users[message.chat.id])
def check_order_status(message):
    user_id = message.chat.id
    order_id = message.text.strip()

    # Check if order ID exists
    with open("orders.txt", "r") as f:
        orders = [line.strip().split(",") for line in f.readlines()]

    matching_order = [o for o in orders if len(o) > 1 and o[1] == order_id]

    if not matching_order:
        bot.send_message(user_id, "❌ Invalid Order ID! Please enter a valid ID.", reply_markup=main_menu())
        return  # ✅ This is now correctly placed inside the function

    # Fetch order status
    status = get_order_status(order_id)

    if status:
        bot.send_message(user_id, f"📦 Order Status for `{order_id}`:\n\n{status}", parse_mode="Markdown", reply_markup=main_menu())
    else:
        bot.send_message(user_id, "❌ Failed to fetch order status. Try again later.", reply_markup=main_menu())


def get_order_status(order_id):
    try:
        response = requests.post(SMM_KOCH_URL, data={
            "key": SMM_KOCH_API,
            "action": "status",
            "order": order_id
        })

        if response.status_code != 200:
            return f"❌ HTTP Error {response.status_code}"

        data = response.json()
        print(f"Order Status API Response: {data}")  # Debugging

        completed = data.get('start_count', 0)
        remaining = data.get('remains', 0)

        if remaining in [None, 0]:  # If "remaining" is None or 0
            return f"✅ Fully Completed"
        else:
            return f"✅ Completed - {completed}, ❌ Remaining - {remaining}"

    except requests.exceptions.RequestException as e:
        return f"❌ Network Error: {str(e)}"


@bot.message_handler(func=lambda message: message.text == "📢 Broadcast")
def ask_for_broadcast_message(message):
    if message.chat.id != ADMIN_CHAT_ID:
        bot.send_message(message.chat.id, "❌ This function is for admin only.")
        return

    admin_states[message.chat.id] = "waiting_for_broadcast"
    bot.send_message(message.chat.id, "📢 Send the message you want to broadcast.")

@bot.message_handler(func=lambda message: message.chat.id in admin_states and admin_states[message.chat.id] == "waiting_for_broadcast")
def send_broadcast(message):
    if message.chat.id != ADMIN_CHAT_ID:
        bot.send_message(message.chat.id, "❌ This function is for admin only.")
        return

    broadcast_message = message.text
    sent_count = 0
    failed_count = 0

    if os.path.exists("users.txt"):
        with open("users.txt", "r") as file:
            user_ids = file.read().splitlines()

        for user_id in user_ids:
            try:
                bot.send_message(int(user_id), broadcast_message)
                sent_count += 1
            except Exception as e:
                failed_count += 1  # User likely blocked the bot

    bot.send_message(ADMIN_CHAT_ID, f"✅ Broadcast sent to {sent_count} users.\n❌ Failed to send to {failed_count} users.")

    admin_states.pop(message.chat.id, None)  # Reset state after sending

bot.polling()