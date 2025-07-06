"""Image processing utilities."""
import requests
from io import BytesIO
from PIL import Image
import re


def get_image_from_url(url: str) -> Image:
    """Download and return PIL Image from URL."""
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img


def extract_image_url_from_content(content) -> str:
    """Extract image URL from Reddit content."""
    from bot.utils.content_helpers import is_submission, is_image_url
    
    if is_submission(content):
        # Check if submission URL is an image
        url = getattr(content, "url", "")
        if is_image_url(url):
            return url
    else:
        # Check comment body HTML for images
        if hasattr(content, "body_html"):
            m = re.search(r'<img src="(.+?)"', content.body_html)
            if m:
                return m.group(1)
        
        # Check submission URL if comment belongs to image post
        if hasattr(content, "submission"):
            sub_url = getattr(content.submission, "url", "")
            if is_image_url(sub_url):
                return sub_url
    
    return None
