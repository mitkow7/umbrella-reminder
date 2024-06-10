import schedule
import smtplib
import requests
from bs4 import BeautifulSoup


def get_urls_string(urls):
    result = ''

    for url in urls:
        result += f"{url}\n\n"

    return result


def get_weather_links(data):
    if data.status_code == 200:
        soup = BeautifulSoup(data.content, 'html.parser')
        results = []

        for g in soup.find_all('div', {'class': 'g'}):
            anchors = g.find_all('a')
            if anchors:
                link = anchors[0]['href']
                title = g.find('h3').text

                results.append(f'Title: {title}\nURL: {link}')

        return results
    else:
        return f'Error: {data.status_code}'


def send_email(sky, temperature, humidity, urls):
    smtp_obj = smtplib.SMTP('smtp.gmail.com', 587)

    smtp_obj.starttls()
    smtp_obj.login('Your email', 'Your password')

    subject = 'Umbrella Reminder'
    body = (f'Take an umbrella before leaving the house.\n\nWeather condition for today is {sky}'
            f'\n\nTemperature is {temperature}°C'
            f'\n\nHumidity is {humidity}%.'
            f'\n\n{urls}')

    msg = f'Subject: {subject}\n\n{body}'.encode('utf-8')

    smtp_obj.sendmail("From address", "To address", msg)

    smtp_obj.quit()
    print('Email sent!')


def main():
    city = 'Veliko Tarnovo'  # input()
    url = f"https://www.google.com/search?q=weather+{city}"
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15'}

    data = requests.get(url, headers=header)

    if data.status_code == 200:
        soup = BeautifulSoup(data.text, 'html.parser')

        temperature_in_celsius = soup.find('span', class_='wob_t q8U8x').text
        sky = soup.find('span', id='wob_dc').text
        humidity = soup.find('span', id='wob_hm').text

        humidity_number = int(humidity.split('%')[0])

        if (sky == 'Дъжд' or sky == 'Валежи' or
                sky == 'На места с прегърмявания' or sky == 'Проливен дъжд с гръмотевици' or sky == 'Слаб краткотраен дъжд'):
            links = get_weather_links(data)
            urls = get_urls_string(links)

            send_email(sky, temperature_in_celsius, humidity_number, urls)

        elif humidity_number >= 60:
            links = get_weather_links(data)
            urls = get_urls_string(links)

            send_email(sky, temperature_in_celsius, humidity_number, urls)


schedule.every().day.at("08:00").do(main)

while True:
    schedule.run_pending()
