import telebot
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
import platform
import locale
from secrets import TOKEN, chat_id

#set location
locale.setlocale(locale.LC_ALL, 'de_DE')

#configure Telegram bot

tb = telebot.TeleBot(TOKEN, parse_mode="HTML")


#get date and time from parsed HTML from RSS
def get_datetime_from_html(html) -> datetime:
    parsed_html = BeautifulSoup(html, features="html.parser")
    datum = datetime.strptime(parsed_html.find('time')["datetime"], "%Y-%m-%dT%H:%M:%SZ")
    return datum

#get event title from parsed HTML from RSS
def get_title_from_html(html):
    parsed_html = BeautifulSoup(html, features="html.parser")
    title = parsed_html.find('span').text
    return title

#get event subtitle from parsed HTML from RSS
def get_subtitle_from_html(html):
    parsed_html = BeautifulSoup(html, features="html.parser")
    subtitle = parsed_html.find('div', class_='field--name-field-shortdesc')
    if subtitle:
        return subtitle.text
    return ""

#summarize all information and fixing encoding error on Windows 
def get_infos(pointer):
        html = pointer.summary
        current = get_datetime_from_html(html)
        title = get_title_from_html(html)
        subtitle = get_subtitle_from_html(html)
        Datum_f = current.strftime("%A, %d. %B %H:%M")
        link = pointer.link
        if platform.system() == "Windows":
            title = (title.encode(encoding="utf-8"))
        return current, title, subtitle, Datum_f, link

#generating strings for one event 
def event_string (Datum_f, title, subtitle, link):
    event = ""
    if subtitle:
        event = f"""<code>{Datum_f}</code>
<b>{title}</b>
<i>{subtitle}</i>
{link}

"""
    else:
        event = f"""<code>{Datum_f}</code>
<b>{title}</b>
{link}

"""
    return event

#get the "id" of the event (last part of the link)
def get_event_id (pointer):
    link = pointer.link
    event_id = link.replace("http://tacker.fr/node/","")
    return event_id


#seting Feed URLs
feed_urls = ['http://tacker.fr/index.php/taxonomy/term/53/feed', 'https://tacker.fr/taxonomy/term/52/feed', 'https://tacker.fr/taxonomy/term/65']

#List of all events and aditional message
events = ["<b><u>Demo(s)/Aktion(en)/Kundgebung(en) Morgen:</u></b>","\n"]
event_ids = []
#loop through all events from the feed
for feed_url in feed_urls:
    Feed = feedparser.parse(feed_url)
    for pointer in Feed.entries:
        current, title, subtitle, Datum_f, link = get_infos(pointer) 
        event_id = get_event_id(pointer)
        if event_id not in event_ids:
            
            #events on the next day
            if current.date == date.today() + timedelta(days=1):
                events.append(event_string(Datum_f, title, subtitle, link))
                event_ids.append(event_id)

            #Events in the next week (on Sunday)
            if current.weekday == 6:
                events = ["<b><u>Demo(s) diese Woche:</u></b>","\n"]
                if current.date <= date.today() + timedelta(days=7) and current < datetime.now():
                    events.append(event_string(Datum_f, title, subtitle, link))
                    event_ids.append(event_id)
                else:
                    events.append("Keine Demos/Aktionen/Kundgebungen diese Woche :(")

#Telegram Message if there are Events           
if len(events) >= 3:
    text = "".join(events)
    print(text)
    tb.send_message(chat_id, text)
else:
    print("Keine events!")
        
