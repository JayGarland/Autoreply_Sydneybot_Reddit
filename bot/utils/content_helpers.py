"""Content utility functions for Reddit posts and comments."""
import praw
import requests
from typing import Optional, List, Dict, Any
import re
from urllib.parse import urlparse


def get_content_text(content) -> str:
    """Extract text content from submission or comment."""
    if is_submission(content):
        return getattr(content, 'selftext', '') or ""
    return getattr(content, 'body', '')


def is_submission(content) -> bool:
    """Check if content is a submission (post) rather than a comment."""
    # Check for PRAW submission type
    if hasattr(content, '__class__') and 'submission' in str(content.__class__).lower():
        return True
    # Check for submission-specific attributes
    return hasattr(content, 'selftext') and hasattr(content, 'url') and hasattr(content, 'permalink')


def is_image_url(url: str) -> bool:
    """Check if URL points to an image."""
    if not url:
        return False
    return url.lower().endswith((".jpg", ".png", ".jpeg", ".gif", ".webp", ".bmp"))


def is_video_url(url: str) -> bool:
    """Check if URL points to a video."""
    if not url:
        return False
    return url.lower().endswith((".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mkv")) or "v.redd.it" in url


def has_media_content(submission) -> bool:
    """Check if submission has any media content (image, video, etc.)."""
    if not hasattr(submission, 'url'):
        return False
    
    url = submission.url
    return (is_image_url(url) or 
            is_video_url(url) or 
            'reddit.com/gallery/' in url or
            hasattr(submission, 'media') and submission.media is not None)


def get_image_from_url(url_or_content, timeout: int = 10) -> Optional[str]:
    """Extract image URL from Reddit content or download image from URL."""
    # If it's a URL string, try to download it
    if isinstance(url_or_content, str):
        if not is_image_url(url_or_content):
            return None
        return url_or_content  # Return URL for consistency
    
    # If it's Reddit content, extract image URL
    content = url_or_content
    if not is_submission(content):
        return None
    
    # Check if URL is direct image
    if hasattr(content, 'url') and is_image_url(content.url):
        return content.url
    
    # Check preview images
    if hasattr(content, 'preview') and content.preview:
        try:
            return content.preview['images'][0]['source']['url']
        except (KeyError, IndexError):
            pass
    
    return None


def download_image_bytes(url: str, timeout: int = 10) -> Optional[bytes]:
    """Download image from URL and return as bytes."""
    if not is_image_url(url):
        return None
    
    try:
        response = requests.get(url, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        return response.content
    except Exception:
        return None


def has_preview_image(content) -> bool:
    """Check if submission has preview image."""
    if not is_submission(content):
        return False
    
    return (hasattr(content, 'preview') and 
            content.preview and 
            'images' in content.preview and 
            len(content.preview['images']) > 0)


def get_content_length(content) -> int:
    """Get character length of content text."""
    text = get_content_text(content)
    return len(text.strip()) if text else 0


def is_content_too_short(content, min_length: int = 10) -> bool:
    """Check if content is too short to be meaningful."""
    return get_content_length(content) < min_length


def is_content_too_long(content, max_length: int = 10000) -> bool:
    """Check if content is too long."""
    return get_content_length(content) > max_length


def extract_urls_from_text(text: str) -> List[str]:
    """Extract all URLs from text."""
    if not text:
        return []
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)


def normalize_text(text: str) -> str:
    """Normalize text by removing extra whitespace and formatting."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove markdown formatting
    text = re.sub(r'[*_`]', '', text)
    # Remove excessive punctuation
    text = re.sub(r'[!.?]{3,}', '...', text)
    # Handle Reddit HTML entities
    text = text.replace("&gt;", ">")
    text = text.replace("&lt;", "<")
    text = text.replace("&amp;", "&")
    
    return text


def get_domain_from_url(url: str) -> Optional[str]:
    """Extract domain from URL."""
    if not url:
        return None
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        return domain if domain else None
    except Exception:
        return None


def is_reddit_media_url(url: str) -> bool:
    """Check if URL is Reddit's own media (i.redd.it, v.redd.it)."""
    if not url:
        return False
    
    domain = get_domain_from_url(url)
    return domain in ['i.redd.it', 'v.redd.it', 'preview.redd.it']


def get_content_url(content) -> Optional[str]:
    """Get URL from submission if available."""
    if is_submission(content):
        return getattr(content, 'url', None)
    return None


def get_content_type(content) -> str:
    """Determine the type of content (text, image, video, link, comment)."""
    if not is_submission(content):
        return "comment"
    
    if hasattr(content, 'url') and content.url:
        if is_image_url(content.url):
            return "image"
        elif is_video_url(content.url):
            return "video"
        elif content.url != f"https://www.reddit.com{content.permalink}":
            return "link"
    
    return "text"


def has_media(content) -> bool:
    """Check if content has any media (image or video) - legacy function."""
    if not is_submission(content):
        return False
    return has_media_content(content)


def get_content_type_summary(content) -> Dict[str, Any]:
    """Get a comprehensive summary of content type and characteristics."""
    summary = {
        'is_submission': is_submission(content),
        'text_length': get_content_length(content),
        'has_text': get_content_length(content) > 0,
        'is_short': is_content_too_short(content),
        'is_long': is_content_too_long(content),
        'has_media': False,
        'has_preview': False,
        'urls': [],
        'media_type': None,
        'content_type': get_content_type(content)
    }
    
    if is_submission(content):
        summary['has_media'] = has_media_content(content)
        summary['has_preview'] = has_preview_image(content)
        
        if hasattr(content, 'url') and content.url:
            if is_image_url(content.url):
                summary['media_type'] = 'image'
            elif is_video_url(content.url):
                summary['media_type'] = 'video'
            elif is_reddit_media_url(content.url):
                summary['media_type'] = 'reddit_media'
    
    text = get_content_text(content)
    summary['urls'] = extract_urls_from_text(text)
    
    return summary


def should_process_content(content, min_length: int = 10, max_length: int = 10000) -> bool:
    """Determine if content should be processed based on various criteria."""
    if is_content_too_short(content, min_length):
        return False
    
    if is_content_too_long(content, max_length):
        return False
    
    # Skip if it's just a media post with no meaningful text
    if is_submission(content) and has_media_content(content):
        text_length = get_content_length(content)
        if text_length < 5:  # Very minimal text with media
            return False
    
    return True


def get_content_preview(content, max_length: int = 100) -> str:
    """Get a preview of content text (first N characters)."""
    text = get_content_text(content)
    normalized = normalize_text(text)
    
    if len(normalized) <= max_length:
        return normalized
    
    return normalized[:max_length].rstrip() + "..."


def clean_content_text(content) -> str:
    """Clean and normalize content text - legacy function, use normalize_text instead."""
    text = get_content_text(content)
    return normalize_text(text)
