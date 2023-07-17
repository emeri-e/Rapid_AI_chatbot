# imports
import openai  # OpenAI Python library to make API calls
import requests  # used to download images
import os  # used to access filepaths
from PIL import Image  # used to print and edit images

openai.api_key = ''

def generate_img(prompt, message,size = '256x256'):
    image_dir_name = "generated_images"
    image_dir = os.path.join(os.curdir, image_dir_name)


    generation_response = openai.Image.create(
        prompt=prompt,
        n=1,
        size=size
    )


    generated_image_name = f"{message.message_id}.png"
    generated_image_filepath = os.path.join(image_dir, generated_image_name)
    generated_image_url = generation_response["data"][0]["url"]  
    generated_image = requests.get(generated_image_url).content 

    with open(generated_image_filepath, "wb") as image_file:
        image_file.write(generated_image) 

    return generated_image_filepath
