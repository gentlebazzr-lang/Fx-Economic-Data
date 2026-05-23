import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime
import time

def fetch_economic_data():
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print (f"Error fetching data: {e}")
        return
    
    #Defining Filters
    target_currencies = ['EUR', 'JPY', 'USD', 'GBP']
    target_impacts = ['High', 'Holiday']
    
    #Parsing the xml data
    root = ET.fromstring(response.content)
    filtered_events = []
    
    for event in root.findall('event'):
        country = event.find('country').text if event.find('country') is not None else ''
        impact = event.find('impact').text if event.find('impact') is not None else ''

        if country in target_currencies and impact in target_impacts:
            title = event.find('title').text.strip()
            date_str = event.find('date').text
            time_str = event.find('time').text

            filtered_events.append({
                'currency': country,
                'impact': impact, 
                'title': title,
                'date': date_str,
                'time': time_str
            })

    print("--- Forex Factory Filtered Data---")
    pine_timestamps = []
    
    if not filtered_events:
        print("No High Impact News or Holidays for the selected currencies for this week.")
    else:
        for item in filtered_events:
            print(f"[{item['date']} {item['time']}] {item['currency']} ({item['impact']}): {item['title']}") # for readable format

    
            try:
                full_time_str = f"{item['date']} {item['time']}"
                dt = datetime.strptime(full_time_str, "%m-%d-%Y %I: %M%p")
                unix_ms = int(time.mktime(dt.timetuple())) * 1000
                pine_timestamps.append(unix_ms)
            except Exception as e:
                continue 
                
    output_payload = {
        "last_updated": datetime.utcnow().strftime("%Y-%m_%d %H: %M: %S UTC"),
        "high_impact_timestamps": pine_stamps
    }
    with open("news_data.json", "w") as json_file:
        json.dump(output_payload, json_file, indent=4)
    print ("successfully generated news_data.json for public distribution")

            
                                                                                       

if __name__ == "__main__":
    fetch_economic_data ()

                                                 
                                                                                   
    
