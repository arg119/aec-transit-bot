import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def keep_alive():
    """This route is just for the external cron job to hit."""
    return "Bot is awake!", 200

# --- 1. SECURE CREDENTIALS (Pulled from Render Environment Variables) ---
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')
ADMIN_NUMBER = os.getenv('ADMIN_PHONE_NUMBER')  # Format: 91XXXXXXXXXX

# --- IN-MEMORY DATABASE ---
user_states = {} 
grievances_db = [] 

# --- MENUS ---
main_menu_text = (
    "🚌 ✨ *AEC Smart Transit System* ✨ 🚌\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "👇 *Please select an option:*\n\n"
    "🗺️ *1* ➔ To AEC (CF / Ganeshguri)\n"
    "🏙️ *2* ➔ To AEC (Paltan Bazar)\n"
    "🛣️ *3* ➔ Leaving Campus\n"
    "🌴 *4* ➔ Holiday Schedule\n"
    "🛰️ *5* ➔ Live Bus Tracking\n"
    "📝 *6* ➔ Submit a Grievance\n"
    "👋 *7* ➔ Exit"
)

footer = "\n\n━━━━━━━━━━━━━━━━━━━━\n↩️ _Reply *0* for Main Menu_"

# --- HELPER: SEND TEXT MESSAGE ---
def send_whatsapp_message(to_number, message_text):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message_text}
    }
    try:
        requests.post(url, headers=headers, json=payload)
    except Exception as e:
        print(f"Failed to send message: {e}")

# --- HELPER: SEND INTERACTIVE LOCATION MESSAGE ---
def send_interactive_location(to_number, body_text):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {"type": "text", "text": "AEC Live Track 🛰️"},
            "body": {"text": body_text},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {"id": "refresh_loc", "title": "Refresh Location"}
                    }
                ]
            }
        }
    }
    try:
        requests.post(url, headers=headers, json=payload)
    except Exception as e:
        print(f"Failed to send interactive message: {e}")

# --- WEBHOOK ---
@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403

    if request.method == 'POST':
        data = request.get_json()
        try:
            if data.get('object') == 'whatsapp_business_account':
                for entry in data.get('entry', []):
                    for change in entry.get('changes', []):
                        value = change.get('value', {})
                        
                        if 'messages' in value:
                            msg_info = value['messages'][0]
                            sender_number = msg_info['from']
                            
                            # Catch Interactive Button Clicks (The Refresh Button)
                            if msg_info.get('type') == 'interactive':
                                button_id = msg_info['interactive']['button_reply']['id']
                                if button_id == "refresh_loc":
                                    process_logic(sender_number, '5') # Triggers tracking logic again
                            
                            # Catch Standard Text
                            elif msg_info.get('type') == 'text':
                                incoming_msg = msg_info['text']['body'].lower().strip()
                                process_logic(sender_number, incoming_msg)
                                
            return jsonify({"status": "ok"}), 200
            
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return jsonify({"status": "error"}), 500

def process_logic(sender_number, incoming_msg):
    global user_states, grievances_db

    # --- SECRET ADMIN PANEL ---
    if incoming_msg == 'admin99':
        if len(grievances_db) == 0:
            send_whatsapp_message(sender_number, "📂 *Admin Panel*\n\nNo grievances yet." + footer)
        else:
            admin_text = "📂 *Admin Panel - Live Grievances*\n━━━━━━━━━━━━━━━━━━━━\n\n"
            for index, g in enumerate(grievances_db):
                admin_text += f"🗣️ *Student {index + 1}:* {g}\n\n"
            send_whatsapp_message(sender_number, admin_text + footer)
        return

    # --- GRIEVANCE CATCHER LOGIC ---
    if user_states.get(sender_number) == 'waiting_for_grievance':
        if incoming_msg in ['0', 'menu', 'exit']:
            user_states[sender_number] = 'normal'
            send_whatsapp_message(sender_number, main_menu_text)
            return
            
        # Log locally
        grievances_db.append(incoming_msg)
        
        # FORWARD TO ADMIN IMMEDIATELY
        if ADMIN_NUMBER:
            admin_alert = f"📢 *NEW AEC TRANSIT GRIEVANCE*\nFrom: {sender_number}\nIssue: {incoming_msg}"
            send_whatsapp_message(ADMIN_NUMBER, admin_alert)

        user_states[sender_number] = 'normal'
        send_whatsapp_message(
            sender_number,
            "✅ *Grievance Submitted Successfully*\n\nThank you. Your feedback has been securely logged and forwarded to the admins.\n\n👨‍💻 _System built by Arindam Goswami_" + footer
        )
        return

    # --- MENU ROUTING ---
    if incoming_msg == '1':
        send_whatsapp_message(sender_number, "🗺️ *To AEC (from CF / Ganeshguri)*\n_Regular Weekday Schedule_\n\n📍 *Via Ganeshguri ➔ Zoo Road:*\n  • 7:00 AM | • 8:00 AM\n\n📍 *Via Ganeshguri ➔ Highway:*\n  • 7:00 AM | • 8:10 AM\n\n📍 *Direct from Church Field:*\n  • 11:40 AM | • 4:20 PM\n  • 5:30 PM  | • 7:20 PM\n  • 7:45 PM  | • 8:15 PM\n\n🌟 *Special Route (9:40 AM)*\n_(CF ➔ Paltan ➔ Ganesh ➔ Highway)_" + footer)
        
    elif incoming_msg == '2':
        send_whatsapp_message(sender_number, "🏙️ *To AEC (from Paltan Bazar)*\n_Regular Weekday Schedule_\n\n⚠️ *NOTE:* Starts from Pan Bazar Stop.\n\n⏰ *Timings:*\n  • 9:30 AM | • 11:20 AM\n  • 1:45 PM | • 2:30 PM\n  • 3:00 PM | • 3:30 PM\n  • 6:00 PM" + footer)
        
    elif incoming_msg == '3':
        send_whatsapp_message(sender_number, "🛣️ *Leaving AEC (To City)*\n_Regular Weekday Schedule_\n\n🌅 *Morning:*\n  • 7:50 AM | • 8:30 AM\n  • 9:50 AM | • 10:15 AM\n\n☀️ *Afternoon:*\n  • 12:10 PM | • 12:20 PM (H)\n  • 1:10 PM (GC) | • 1:20 PM (H)\n  • 3:00 PM | • 4:05 PM (H)\n  • 4:15 PM\n\n🌙 *Evening:*\n  • 5:00 PM | • 6:00 PM\n  • 6:50 PM | • 7:10 PM\n  • 8:30 PM | • 8:50 PM\n  • 9:00 PM" + footer)

    elif incoming_msg == '4':
        send_whatsapp_message(sender_number, "🌴 *Holiday Schedule*\n⬇️ *Towards AEC:*\n  • 7:30 AM (P) | • 10:40 AM (P)\n  • 2:30 PM (P) | • 5:10 PM (CF)\n  • 8:00 PM (CF)\n\n⬆️ *Leaving AEC:*\n  • 9:15 AM | • 12:15 PM (H)\n  • 3:45 PM | • 6:40 PM\n  • 9:00 PM" + footer)

    elif incoming_msg == '5':
        try:
            TRACKING_URL = "http://track4.millitrack.com/api/users/166837/userDevicesState?pieChartOnly=false" 
            headers = {
                "Cookie": "JSESSIONID=node0w0migg3gdmzh16kva25lphqf52493027.node0",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json"
            }
            response = requests.get(TRACKING_URL, headers=headers)
            data = response.json()
            bus_list = data.get("deviceCumPositionList", [])
            
            if bus_list and len(bus_list) > 0:
                ist_timezone = timezone(timedelta(hours=5, minutes=30))
                timestamp = datetime.now(ist_timezone).strftime("%I:%M %p")
                body_text = f"Last Checked: {timestamp}\n━━━━━━━━━━━━━━━━━━━━\n\n"
                
                for index, bus in enumerate(bus_list):
                    bus_num = index + 1
                    position = bus.get("position", {})
                    real_lat = position.get("latitude")
                    real_lng = position.get("longitude")
                    if real_lat and real_lng:
                        map_url = f"https://www.google.com/maps/search/?api=1&query={real_lat},{real_lng}"
                        body_text += f"🟢 *Bus {bus_num}:* Online\n📍 *Map:* {map_url}\n\n"
                    else:
                        body_text += f"🔴 *Bus {bus_num}:* Offline/Parked\n\n"
                
                # Send the compiled data WITH the interactive refresh button
                send_interactive_location(sender_number, body_text)
            else:
                send_whatsapp_message(sender_number, "⚠️ *AEC Live Track*\n\nNo buses currently active." + footer)
        except Exception as e:
            send_whatsapp_message(sender_number, "🛠️ *System Notice*\n\nAPI Bridge refreshing. Use Options 1-4 for now." + footer)

    elif incoming_msg == '6':
        user_states[sender_number] = 'waiting_for_grievance'
        send_whatsapp_message(sender_number, "📝 *Submit a Grievance*\n\nType your issue or suggestion below and press send.\n\n_(To cancel, reply *0*)_")

    elif incoming_msg in ['7', 'exit', 'quit', 'bye']:
        send_whatsapp_message(sender_number, "👋 *Thanks for using AEC Smart Transit!*\n\nI built this system from scratch because our campus deserves better technical infrastructure. I hope it makes your commute easier.\n\n👨‍💻 _Tech by Arindam Goswami (4th Sem CSE)_\n\nType *0* to return anytime.")

    elif incoming_msg == '0' or incoming_msg == 'menu':
        user_states[sender_number] = 'normal'
        send_whatsapp_message(sender_number, main_menu_text)
        
    else:
        send_whatsapp_message(sender_number, main_menu_text)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
