import flask
from flask import Response
import requests
from logger import logger
from get.getRequest import getRequest
import os
from helper.media import mediaType, create_video_thumbnail
from helper.jwt import token_required

# TODO: maybe token not required for preview, but for now we keep it to avoid spam and abuse
@token_required
def preview(reqId):
    # Fetch data from the external API
    req = getRequest(reqId)

    # Set up basic metadata
    title = "Kaouka -- Message"
    description = req["text"]
    media_url = req["media"]
    page_url = f'kaouka://content?id={reqId}'
    fallback_url = "https://kenyhenry.github.io/elaborium_website/#/Kaouka"

    # Determine media type
    # TODO get file instead of link url to create it then transform it into link
    file_extension = os.path.splitext(media_url)[1].lstrip(".")
    media_type = mediaType(file_extension)
    og_media_tag = f'<meta property="og:image" content="{media_url}">'
    if media_type == "video":
        try:
            title = "Kaouka -- vidéo"
            final_url = media_url.replace(file_extension, '_thumbnail.jpg')
            file = media_url.replace('https://elaborium.site/proxy/stream/', '')
            old_file_path = '/opt/files/'+file
            file_path = '/opt/files/'+file.replace(file_extension, '_thumbnail.jpg')
            if not os.path.exists(file_path):
                err = create_video_thumbnail(old_file_path, file_path)
            og_media_tag = f'<meta property="og:image" content="{final_url}">'
        except Exception as e:
            logger.critical("create thundnail error : "+str(e))
    elif media_type == "image":
        title = "Kaouka -- Image"
        og_media_tag = f'<meta property="og:image" content="{media_url}">'
    elif media_type == "audio":
        title = "Kaouka -- Audio"
        og_media_tag = f'<meta property="og:image" content="https://elaborium.site/proxy/stream/default/audio.jpg">'
    
    # HTML response with Open Graph meta tags
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta property="og:type" content="website">
        <meta property="og:title" content="{title}">
        <meta property="og:description" content="{description}">
        {og_media_tag}
        <meta property="og:url" content="{page_url}">
        
        <title>{title}</title>
        <script type="text/javascript">
            function openAppOrFallback() {{
                var start = Date.now();

                // Try to open the app link
                window.location = "{page_url}";

                // After a delay, check if the page is still visible
                setTimeout(function() {{
                    var end = Date.now();
                    // If the page was not hidden (app was not opened), redirect to fallback
                    if (end - start < 3500) {{
                        window.location = "{fallback_url}";
                    }}
                }}, 1000);  // 1 second delay before checking
            }}
        </script>
    </head>
    <body onload="openAppOrFallback()">
    </body>
    </html>
    """
    return Response(html_content, mimetype='text/html')

def previewEntry():
    try:
        request = flask.request
        reqid = request.args.get('reqId')
        return preview(reqid)
    except Exception as e:
        logger.critical("proxy getRequestEntry args error: " + str(e))
        return {}
