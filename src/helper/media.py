import os
import random

import ffmpeg
from PIL import Image, ImageDraw, ImageFilter

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg',
                      'gif', 'mp4', 'mov', 'avi', 'mkv', 'webm'}
FILE_PATH = '/opt/files/'

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def mediaType(ext):
    audio = {'mp3', 'wav', 'aac', 'flac', 'ogg', 'wma', 'm4a', 'aiff',
             'alac', 'opus', 'amr', 'mid', 'midi', 'pcm', 'ra', 'mka'}
    video = {'mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm', 'mpeg',
             'mpg', 'm4v', '3gp', 'rm', 'rmvb', 'vob', 'ts', 'asf', 'f4v', 'divx'}
    image = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'svg', 'webp',
             'heic', 'heif', 'raw', 'psd', 'ai', 'eps', 'ico', 'dds', 'jfif', 'jp2'}
    # TODO add emoji
    if ext in image:
        return "image"
    if ext in audio:
        return "audio"
    if ext in video:
        return "video"
    else:
        return "message"


def get_random_file_in_folder(root_dir):
    folders_with_files = []

    # Iterate through all folders in the root directory
    for folder in os.listdir(root_dir):
        folder_path = os.path.join(root_dir, folder)
        # Check if the folder contains subfolders
        if os.path.isdir(folder_path):
            files = [f for f in os.listdir(folder_path) if os.path.isfile(
                os.path.join(folder_path, f))]
            if files:
                folders_with_files.append((folder, folder_path, files))

    # Choose a random folder from the list
    if folders_with_files:
        folder, folder_path, files = random.choice(folders_with_files)
        random_file = random.choice(files)

        return os.path.join(folder, random_file)
    else:
        return None


def add_play_logo_to_thumbnail(thumbnail_path, output_path, logo_size=50):
    try:
        # Open the thumbnail image and ensure it has an alpha channel
        thumbnail = Image.open(thumbnail_path).convert("RGBA")

        # Create a transparent overlay for drawing
        overlay = Image.new("RGBA", thumbnail.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        # Define the center and dimensions
        center_x, center_y = thumbnail.size[0] // 2, thumbnail.size[1] // 2
        # Outer circle radius slightly larger than the triangle
        circle_radius = logo_size + 5

        # Draw the outer black transparent circle
        draw.ellipse(
            (center_x - circle_radius, center_y - circle_radius,
             center_x + circle_radius, center_y + circle_radius),
            fill=(0, 0, 0, 150)  # Semi-transparent black
        )

        # Create a new image for the triangle to apply rounded edges
        triangle_overlay = Image.new(
            "RGBA", thumbnail.size, (255, 255, 255, 0))
        triangle_draw = ImageDraw.Draw(triangle_overlay)

        # Define triangle coordinates for the play button
        triangle = [
            (center_x - logo_size // 3, center_y - logo_size // 2),  # Top-left
            (center_x - logo_size // 3, center_y + logo_size // 2),  # Bottom-left
            (center_x + logo_size // 2, center_y),                  # Right-center
        ]

        # Draw the triangle with a solid white fill
        triangle_draw.polygon(triangle, fill=(255, 255, 255, 255))

        # Apply blur to smooth the edges of the triangle
        triangle_overlay = triangle_overlay.filter(ImageFilter.GaussianBlur(2))

        # Composite the triangle onto the overlay
        overlay = Image.alpha_composite(overlay, triangle_overlay)

        # Composite the overlay onto the thumbnail
        combined = Image.alpha_composite(thumbnail, overlay)

        # Save the final image
        os.remove(thumbnail_path)
        combined.convert("RGB").save(output_path, "JPEG")
        print(f"Thumbnail with play logo saved to {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


def create_video_thumbnail(video_path, thumbnail_path, time="00:00:01"):
    try:
        (
            ffmpeg
            .input(video_path, ss=time)  # Set the time to capture the frame
            # Resize the frame to a smaller size (optional)
            .filter('scale', 320, -1)
            .output(thumbnail_path, vframes=1)  # Capture only 1 frame
            .run(capture_stdout=True, capture_stderr=True)
        )
        add_play_logo_to_thumbnail(thumbnail_path, thumbnail_path)
        return "Thumbnail saved to " + thumbnail_path
    except ffmpeg.Error as e:
        return "An error occurred: " + str(e.stderr.decode())
