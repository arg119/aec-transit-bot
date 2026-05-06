from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

# --- IN-MEMORY DATABASE ---
# This remembers which users are typing a grievance
user_states = {} 
# This stores the actual submitted grievances
grievances_db = [] 

# --- ULTRA CLEAN MAIN MENU ---
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

footer = (
    "\n\n━━━━━━━━━━━━━━━━━━━━\n"
    "↩️ _Reply *0* for Main Menu_"
)

@app.route("/bot", methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower().strip()
    sender_number = request.values.get('From', 'Unknown')
    
    resp = MessagingResponse()
    msg = resp.message()
    
    # --- SECRET ADMIN PANEL ---
    # Type admin99 to see all collected grievances
    if incoming_msg == 'admin99':
        if len(grievances_db) == 0:
            msg.body("📂 *Admin Panel*\n\nNo grievances have been submitted yet." + footer)
        else:
            admin_text = "📂 *Admin Panel - Live Grievances*\n━━━━━━━━━━━━━━━━━━━━\n\n"
            for index, g in enumerate(grievances_db):
                admin_text += f"🗣️ *Student {index + 1}:* {g}\n\n"
            msg.body(admin_text + footer)
        return str(resp)

    # --- GRIEVANCE CATCHER LOGIC ---
    # Check if this user just pressed 6 and is currently typing their grievance
    if user_states.get(sender_number) == 'waiting_for_grievance':
        if incoming_msg in ['0', 'menu', 'exit']:
            # User canceled the grievance submission
            user_states[sender_number] = 'normal'
            msg.body(main_menu_text)
            return str(resp)
            
        # Save their message to the database
        grievances_db.append(incoming_msg)
        
        # Reset their state back to normal
        user_states[sender_number] = 'normal'
        
        msg.body(
            "✅ *Grievance Submitted Successfully*\n\n"
            "Thank you. Your feedback has been securely logged and sent directly to Arnab Anubhav Bora for review.\n\n"
            "👨‍💻 _System built by Arindam Goswami_"
            + footer
        )
        return str(resp)

    # --- 1. TO AEC FROM CHURCH FIELD / GANESHGURI ---
    if incoming_msg == '1':
        msg.body("🗺️ *To AEC (from CF / Ganeshguri)*\n_Regular Weekday Schedule_\n\n📍 *Via Ganeshguri ➔ Zoo Road:*\n  • 7:00 AM | • 8:00 AM\n\n📍 *Via Ganeshguri ➔ Highway:*\n  • 7:00 AM | • 8:10 AM\n\n📍 *Direct from Church Field:*\n  • 11:40 AM | • 4:20 PM\n  • 5:30 PM  | • 7:20 PM\n  • 7:45 PM  | • 8:15 PM\n\n🌟 *Special Route (9:40 AM)*\n_(CF ➔ Paltan ➔ Ganesh ➔ Highway)_" + footer)
        
    # --- 2. TO AEC FROM PALTAN BAZAR ---
    elif incoming_msg == '2':
        msg.body("🏙️ *To AEC (from Paltan Bazar)*\n_Regular Weekday Schedule_\n\n⚠️ *NOTE:* Starts from Pan Bazar Stop.\n\n⏰ *Timings:*\n  • 9:30 AM | • 11:20 AM\n  • 1:45 PM | • 2:30 PM\n  • 3:00 PM | • 3:30 PM\n  • 6:00 PM" + footer)
        
    # --- 3. LEAVING AEC (TO CITY) ---
    elif incoming_msg == '3':
        msg.body("🛣️ *Leaving AEC (To City)*\n_Regular Weekday Schedule_\n\n🌅 *Morning:*\n  • 7:50 AM | • 8:30 AM\n  • 9:50 AM | • 10:15 AM\n\n☀️ *Afternoon:*\n  • 12:10 PM | • 12:20 PM (H)\n  • 1:10 PM (GC) | • 1:20 PM (H)\n  • 3:00 PM | • 4:05 PM (H)\n  • 4:15 PM\n\n🌙 *Evening:*\n  • 5:00 PM | • 6:00 PM\n  • 6:50 PM | • 7:10 PM\n  • 8:30 PM | • 8:50 PM\n  • 9:00 PM" + footer)

    # --- 4. HOLIDAY SCHEDULE ---
    elif incoming_msg == '4':
        msg.body("🌴 *Holiday Schedule*\n⬇️ *Towards AEC:*\n  • 7:30 AM (P) | • 10:40 AM (P)\n  • 2:30 PM (P) | • 5:10 PM (CF)\n  • 8:00 PM (CF)\n\n⬆️ *Leaving AEC:*\n  • 9:15 AM | • 12:15 PM (H)\n  • 3:45 PM | • 6:40 PM\n  • 9:00 PM" + footer)

    # --- 5. LIVE BUS TRACKING ---
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
                final_message = "🛰️ *AEC Live Track* 🛰️\n━━━━━━━━━━━━━━━━━━━━\n\n"
                for index, bus in enumerate(bus_list):
                    bus_num = index + 1
                    position = bus.get("position", {})
                    real_lat = position.get("latitude")
                    real_lng = position.get("longitude")
                    
                    if real_lat and real_lng:
                        map_url = f"https://www.google.com/maps/search/?api=1&query={real_lat},{real_lng}"
                        final_message += f"🟢 *Bus {bus_num}:* Online\n📍 *Map:* {map_url}\n\n"
                    else:
                        final_message += f"🔴 *Bus {bus_num}:* Offline/Parked\n\n"
                final_message += footer
                msg.body(final_message)
            else:
                msg.body("⚠️ *AEC Live Track*\n\nNo buses currently active." + footer)
        except Exception as e:
            msg.body("🛠️ *System Notice*\n\nAPI Bridge refreshing. Use Options 1-4 for now." + footer)

    # --- 6. TRIGGER GRIEVANCE MODE ---
    elif incoming_msg == '6':
        # Put this specific user's phone number into "waiting for grievance" mode
        user_states[sender_number] = 'waiting_for_grievance'
        msg.body(
            "📝 *Submit a Grievance*\n\n"
            "Please type your issue, suggestion, or request below and press send.\n\n"
            "_(To cancel, reply *0*)_"
        )

    # --- 7. EXIT ---
    elif incoming_msg in ['7', 'exit', 'quit', 'bye']:
        msg.body(
            "👋 *Thanks for using AEC Smart Transit!*\n\n"
            "I built this system from scratch because I believe our campus deserves better technical infrastructure.\n\n"
            "If you agree, consider voting for *Arnab Anubhav Bora* for AGS. He is the candidate who supports real, student-led innovation like this.\n\n"
            "👨‍💻 _Tech by Arindam Goswami (4th Sem CSE)_\n\n"
            "Type *0* to return anytime."
        )

    # --- MAIN MENU (0 or unrecognized) ---
    elif incoming_msg == '0' or incoming_msg == 'menu':
        # Ensure we clear their state if they mash 0
        user_states[sender_number] = 'normal'
        msg.body(main_menu_text)
    else:
        msg.body(main_menu_text)
        
    return str(resp)

if __name__ == '__main__':
    app.run(port=5000)
