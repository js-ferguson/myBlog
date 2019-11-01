import os
import cloudinary as Cloud
import cloudinary.uploader
import cloudinary.api


Cloud.config.update = ({
    'cloud_name':os.environ.get('NOFOLIO_CLOUDINARY_CLOUD_NAME'),
    'api_key': os.environ.get('NOFOLIO_CLOUDINARY_API_KEY'),
    'api_secret': os.environ.get('NOFOLIO_CLOUDINARY_API_SECRET'),
    'upload_preset': os.environ.get('NOFOLIO_CLOUDINARY_UPLOAD_PRESET')
})

