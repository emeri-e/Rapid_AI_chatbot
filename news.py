import os
import uuid
from newsapi import NewsApiClient
import requests
from telegram import Update



newsapi = NewsApiClient(api_key='d2c3a4bbbb804c29b3c948c66351e833')

async def get_headlines(catg,update: Update,country='ng'):
    top_headlines = newsapi.get_top_headlines(q='',
                                            sources=None,
                                            category=catg,
                                            language='en',
                                            country=country)

    for news in top_headlines['articles'][:3]:
        source = news['source']['name']
        description = news['description']
        url = news['url']
        img_url = news['urlToImage']
        time = news['publishedAt']

        image_dir = os.path.join(os.curdir, 'news_images')
        image_name = f"{uuid.uuid4()}.png"
        image_filepath = os.path.join(image_dir, image_name)
        image = requests.get(img_url).content 

        with open(image_filepath, "wb") as image_file:
            image_file.write(image) 

        text = f'source: {source}\ntime: {time}\nDescription: {description}\n url: {url}\n'
        await update.message.reply_photo(image_filepath, caption=text, reply_to_message_id=update.message.message_id)
        os.remove(image_filepath)
