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

#configuring RSS feed parser
Feed = feedparser.parse('http://tacker.fr/index.php/taxonomy/term/53/feed')

#List of all events and aditional message
events = ["<b><u>Demo(s) Morgen:</u></b>","\n"]

#loop through all events from the feed
for pointer in Feed.entries:
    current, title, subtitle, Datum_f, link = get_infos(pointer) 

    #events on the next day
    if current.date == date.today() + timedelta(days=1):
        pass
    else:
        events.append(event_string(Datum_f, title, subtitle, link))

    #Events in the next week on Sunday
    if current.weekday == 6:
        events = ["<b><u>Demo(s) diese Woche:</u></b>","\n"]
        if current.date <= date.today() + timedelta(days=7) and current < datetime.now():
            events.append(event_string(Datum_f, title, subtitle, link))
        else:
            events.append("Keine Demos/Aktionen diese Woche")

#Telegram Message if there are Events           
if len(events) >= 3:
    text = "".join(events)
    print(text)
    tb.send_message(chat_id, text)
else:
    print("Keine Demos!")
        
