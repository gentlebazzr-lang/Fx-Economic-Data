import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime, timedelta, timezone
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

    today = datetime.now(timezone.utc)
    days_to_monday = 1 if today.weekday() == 6 else - today.weekday()
    monday_dt = (today + timedelta(days=days_to_monday)).replace(hour=0, minute=0, second=0, microsecond=0)

    week_timestamp = {}
    for i in range(5):
        day_dt =  monday_dt + timedelta(days=i)
        week_timestamp[i] = int(day_dt.timestamp()) * 1000

    # categorize the weeks events
    news_days = set()
    holidays_days = set()



    for item in filtered_events:
        try:
            dt = datetime.strptime(item ['date'], "%m-%d-%Y")
            weekday = dt.weekday()


            if weekday > 4:
                continue  # ignores weekend data

           # categorize as Holiday or High impact news
            if 'Holiday' in item['impact'] or 'Holiday' in item['title']:
                holidays_days.add(weekday)
            elif item['impact'] == 'High':
                news_days.add(weekday)
    
        except Exception:
             continue
             
    # convert sets to sorted lists for exact pattern matching
    n_days = sorted(list(news_days))
    h_days = sorted(list(holidays_days))

    # Exact rule set
    daily_schedule = {} # format -> {day_index : color_category }

   # starting with holidays
    if 4 in h_days and 3 in n_days:   #  Holiday Friday, News Thursday
       daily_schedule = {0: 'high', 1: 'med', 3: 'peak'}
    elif 4 in h_days:                 # Holiday Fri
       daily_schedule = {1: 'high', 2: 'med', 3: 'high'}
    elif 3 in h_days:
        daily_schedule = {1: 'high', 2: 'med', 4: 'high'}
    elif 2 in h_days:
        daily_schedule = {1: 'high', 4: 'med'}

    # High-Impact News Rule
    elif n_days == [0, 1, 2]:    # First three days
        daily_schedule = {1: 'high', 2: 'med', 4: 'med'}
    elif n_days == [2, 3, 4]:   # Last three days   [Mon=0, Tues=1, Wed=2, Thurs= 3, Fri= 4]
        daily_schedule = {0: 'high', 2: 'med', 3: 'high', 4: 'low' }
    elif len(n_days) >= 3:
        daily_schedule = {1: 'high', 2: 'med', 3: 'med'}
    elif n_days == [0, 1]:      # Mon and Tuesday
        daily_schedule = {1: 'high', 2: 'med', 4: 'neutral'}
    elif n_days == [1, 2]:      # Tues and Wednes
        daily_schedule = {1: 'high', 2: 'high', 3: 'neutral' , 4: 'neutral'}
    elif n_days == [2, 3]:      # Wednesday and Thursday
        daily_schedule = {0: 'high', 2: 'med', 3: 'high'}
    elif n_days == [3, 4]:      # Thursday and Friday
        daily_schedule = {0: 'high', 2: 'high', 4: 'high'}
    elif n_days == [0]:         # Monday only
        daily_schedule = {1: 'high', 2: 'med', 3: 'med', 4: 'low'}
    elif n_days == [1]:         # Tuesdays Only
        daily_schedule = {1: 'high', 2: 'med', 3: 'med', 4: 'low'}
    elif n_days == [2]:         # Wednesday Only
        daily_schedule = {0: 'high', 2: 'high', 3: 'med', 4: 'low'}
    elif n_days == [3]:         # Thursday Only
        daily_schedule = {0: 'high', 1: 'med', 3: 'high', 4: 'low'}
    elif n_days == [4]:
        daily_schedule = {0: 'high', 1: 'med', 4: 'high'}
    else:
        # Ethical failsafe
        print ("Neutral week")
        daily_schedule = {0: 'neutral', 1: 'neutral', 2: 'neutral', 3: 'neutral', 4: 'neutral'}

    # Construct the payload array
    payload = {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "blue_peak_zones": [],
        "green_high_zones": [],
        "orange_medium_zones": [],
        "red_low_zones": [],
        "grey_neutral_zones": []
    }

    # Map the categorized days to their actual UNIX timestamps
    for day_idx, category in daily_schedule.items():
        ts = week_timestamp[day_idx]
        if category == 'peak': payload["blue_peak_zones"].append(ts)
        elif category == 'high': payload["green_high_zones"].append(ts)
        elif category == 'med': payload["orange_medium_zones"].append(ts)
        elif category == 'low': payload["red_low_zones"].append(ts)
        elif category == 'neutral': payload["grey_neutral_zones"].append(ts)

    # Save the data payload to repository workspace
    with open("news_data.json", "w") as json_file:
        json.dump(payload, json_file, indent=4)

    print("Successfully routed matrix and generated news_data.json!")


 

if __name__ == "__main__":
    fetch_economic_data ()

                                                 
                                                                                   
    
