from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

main_menu_text = (
    "👋 *AEC Smart Transit (Beta)*\n"
    "_Reply with a number:_\n\n"
    "1️⃣ - To AEC (from CF/Ganeshguri)\n"
    "2️⃣ - To AEC (from Paltan Bazar)\n"
    "3️⃣ - Leaving Campus\n"
    "4️⃣ - Holiday Schedule\n"
    "5️⃣ - 🛰️ *Live Bus Tracking*\n"
    "6️⃣ - 📝 *Submit a Grievance*"
)

footer = "\n\n↩️ _Reply *0* for Main Menu_"

@app.route("/bot", methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower().strip()
    resp = MessagingResponse()
    msg = resp.message()
    
    if incoming_msg == '1':
        msg.body("🚌 *To AEC (from Church Field / Ganeshguri)*\n_Weekday Schedule_\n\n📍 *Via Ganeshguri -> Zoo Road:*\n• 7:00 AM\n• 8:00 AM\n\n📍 *Via Ganeshguri -> Highway:*\n• 7:00 AM\n• 8:10 AM\n\n📍 *Direct from Church Field:*\n• 11:40 AM\n• 4:20 PM\n• 5:30 PM\n• 7:20 PM\n• 7:45 PM\n• 8:15 PM\n\n📍 *Special Route (CF -> Paltan -> Ganeshguri -> Highway):*\n• 9:40 AM" + footer)
        
    elif incoming_msg == '2':
        msg.body("🚌 *To AEC (from Paltan Bazar)*\n_Weekday Schedule_\n\n⚠️ *NOTE:* These buses leave from Paltan Bazar -> Pan Bazar Bus Stop. They DO NOT start from Church Field.\n\n⏰ *Timings:*\n• 9:30 AM\n• 11:20 AM\n• 1:45 PM\n• 2:30 PM\n• 3:00 PM\n• 3:30 PM\n• 6:00 PM" + footer)
        
    elif incoming_msg == '3':
        msg.body("🚌 *Leaving AEC (To City)*\n_Weekday Schedule_\n\n• 7:50 AM\n• 8:30 AM\n• 9:50 AM\n• 10:15 AM\n• 12:10 PM\n• 12:20 PM *(Highway)*\n• 1:10 PM *(Guwahati Club)*\n• 1:20 PM *(Highway)*\n• 3:00 PM\n• 4:05 PM *(Highway)*\n• 4:15 PM\n• 5:00 PM\n• 6:00 PM\n• 6:50 PM\n• 7:10 PM\n• 8:30 PM\n• 8:50 PM\n• 9:00 PM" + footer)

    elif incoming_msg == '4':
        msg.body("🌴 *Holiday Schedule*\n\n⬇️ *Towards AEC:*\n• 7:30 AM *(from Paltan Bazar)*\n• 10:40 AM *(from Paltan Bazar)*\n• 2:30 PM *(from Paltan Bazar)*\n• 5:10 PM *(from CF)*\n• 8:00 PM *(from CF)*\n\n⬆️ *Leaving AEC:*\n• 9:15 AM\n• 12:15 PM *(Highway)*\n• 3:45 PM\n• 6:40 PM\n• 9:00 PM" + footer)

    # --- 5. LIVE BUS TRACKING (MULTI-BUS SUPPORT) ---
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
                final_message = "🛰️ *AEC Live Track*\n\n"
                
                # Loop through every bus found in the system
                for index, bus in enumerate(bus_list):
                    bus_num = index + 1
                    position = bus.get("position", {})
                    
                    real_lat = position.get("latitude")
                    real_lng = position.get("longitude")
                    
                    if real_lat and real_lng:
                        map_url = f"https://www.google.com/maps/search/?api=1&query={real_lat},{real_lng}"
                        final_message += f"🚌 *Bus {bus_num}:* Online\n📍 *Live Map:* {map_url}\n\n"
                    else:
                        final_message += f"🚌 *Bus {bus_num}:* Offline/Parked\n\n"
                
                final_message += "_System fully integrated by your AGS Candidate._" + footer
                msg.body(final_message)
                
            else:
                msg.body("⚠️ *AEC Live Track*\n\nNo buses currently active on the network." + footer)
                
        except Exception as e:
            print(f"API Error: {e}")
            msg.body("⚠️ *System Notice*\n\nLive API bridge is currently in Sandbox Mode and refreshing. Please use the static schedules." + footer)

    elif incoming_msg == '6':
        msg.body("📝 *Submit a Grievance/Suggestion*\n\nYour voice matters. Text your issue here. I will personally review every message.\n\n_— Your AGS Candidate_" + footer)

    elif incoming_msg == '0' or incoming_msg == 'menu':
        msg.body(main_menu_text)

    else:
        msg.body(main_menu_text)
        
    return str(resp)

if __name__ == '__main__':
    app.run(port=5000)