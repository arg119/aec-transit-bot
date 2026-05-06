from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

# --- BRANDED MENU & FOOTER ---
main_menu_text = (
    "🚌 ✨ *AEC Smart Transit System* ✨ 🚌\n"
    "_Your Digital Campus Companion_\n"
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

# Standard footer for regular menus
footer = (
    "\n\n━━━━━━━━━━━━━━━━━━━━\n"
    "↩️ _Reply *0* to return to the Main Menu_"
)

@app.route("/bot", methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower().strip()
    resp = MessagingResponse()
    msg = resp.message()
    
    # --- 1. TO AEC FROM CHURCH FIELD / GANESHGURI ---
    if incoming_msg == '1':
        msg.body(
            "🗺️ *To AEC (from Church Field / Ganeshguri)*\n"
            "_Regular Weekday Schedule_\n\n"
            "📍 *Via Ganeshguri ➔ Zoo Road:*\n"
            "  • 7:00 AM\n  • 8:00 AM\n\n"
            "📍 *Via Ganeshguri ➔ Highway:*\n"
            "  • 7:00 AM\n  • 8:10 AM\n\n"
            "📍 *Direct from Church Field:*\n"
            "  • 11:40 AM  |  • 4:20 PM\n"
            "  • 5:30 PM   |  • 7:20 PM\n"
            "  • 7:45 PM   |  • 8:15 PM\n\n"
            "🌟 *Special Route*\n"
            "_(CF ➔ Paltan ➔ Ganeshguri ➔ Highway)_\n"
            "  • 9:40 AM" 
            + footer
        )
        
    # --- 2. TO AEC FROM PALTAN BAZAR ---
    elif incoming_msg == '2':
        msg.body(
            "🏙️ *To AEC (from Paltan Bazar)*\n"
            "_Regular Weekday Schedule_\n\n"
            "⚠️ *NOTE:* Leaves from Paltan Bazar ➔ Pan Bazar Bus Stop. (Does NOT start from CF).\n\n"
            "⏰ *Timings:*\n"
            "  • 9:30 AM   |  • 11:20 AM\n"
            "  • 1:45 PM   |  • 2:30 PM\n"
            "  • 3:00 PM   |  • 3:30 PM\n"
            "  • 6:00 PM" 
            + footer
        )
        
    # --- 3. LEAVING AEC (TO CITY) ---
    elif incoming_msg == '3':
        msg.body(
            "🛣️ *Leaving AEC (To City)*\n"
            "_Regular Weekday Schedule_\n\n"
            "🌅 *Morning:*\n"
            "  • 7:50 AM   |  • 8:30 AM\n"
            "  • 9:50 AM   |  • 10:15 AM\n\n"
            "☀️ *Afternoon:*\n"
            "  • 12:10 PM  |  • 12:20 PM _(Highway)_\n"
            "  • 1:10 PM _(Guwahati Club)_\n"
            "  • 1:20 PM _(Highway)_\n"
            "  • 3:00 PM   |  • 4:05 PM _(Highway)_\n"
            "  • 4:15 PM\n\n"
            "🌙 *Evening:*\n"
            "  • 5:00 PM   |  • 6:00 PM\n"
            "  • 6:50 PM   |  • 7:10 PM\n"
            "  • 8:30 PM   |  • 8:50 PM\n"
            "  • 9:00 PM" 
            + footer
        )

    # --- 4. HOLIDAY SCHEDULE ---
    elif incoming_msg == '4':
        msg.body(
            "🌴 *Holiday Schedule*\n"
            "_For Sundays & Official Holidays_\n\n"
            "⬇️ *Towards AEC:*\n"
            "  • 7:30 AM _(Paltan Bazar)_\n"
            "  • 10:40 AM _(Paltan Bazar)_\n"
            "  • 2:30 PM _(Paltan Bazar)_\n"
            "  • 5:10 PM _(Church Field)_\n"
            "  • 8:00 PM _(Church Field)_\n\n"
            "⬆️ *Leaving AEC:*\n"
            "  • 9:15 AM\n"
            "  • 12:15 PM _(Highway)_\n"
            "  • 3:45 PM\n"
            "  • 6:40 PM\n"
            "  • 9:00 PM" 
            + footer
        )

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
                final_message = "🛰️ *AEC Live Track* 🛰️\n_Real-time GPS Data_\n━━━━━━━━━━━━━━━━━━━━\n\n"
                
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
                
                final_message += "_System built and integrated by your AGS Candidate._" + footer
                msg.body(final_message)
                
            else:
                msg.body("⚠️ *AEC Live Track*\n\nNo buses currently active on the network." + footer)
                
        except Exception as e:
            print(f"API Error: {e}")
            msg.body("🛠️ *System Notice*\n\nLive API bridge is currently refreshing. Please use the static schedules (Options 1-4) in the meantime." + footer)

    # --- 6. GRIEVANCE ---
    elif incoming_msg == '6':
        msg.body(
            "📝 *Submit a Grievance or Suggestion*\n\n"
            "Your voice matters. Please type your issue or suggestion in a single message and hit send.\n\n"
            "👁️ _I will personally review every message to improve our campus._\n\n"
            "— *Your AGS Candidate*" 
            + footer
        )

    # --- 7. EXIT ---
    elif incoming_msg in ['7', 'exit', 'quit', 'bye']:
        msg.body(
            "👋 *Thank you for using AEC Smart Transit!*\n\n"
            "I hope this tool makes your campus life a little bit easier. If you found it helpful, I would be honored to have your support in the upcoming election.\n\n"
            "🗳️ *Vote for Progress. Vote for Tech.*\n\n"
            "_Type *0* anytime to wake me up again!_"
            # Notice there is no footer added here, so the conversation feels naturally closed.
        )

    # --- MAIN MENU (0 or unrecognized input) ---
    elif incoming_msg == '0' or incoming_msg == 'menu':
        msg.body(main_menu_text)

    else:
        msg.body(main_menu_text)
        
    return str(resp)

if __name__ == '__main__':
    app.run(port=5000)
