import requests
import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import io
import os

# API URL and key
API_URL = "https://zenquotes.io/api/quotes"
API_KEY = "[your_key]"  # Replace with your actual key

# Global data store for quotes
quotes_data = []


def fetch_quotes():
    """Fetch quotes from the ZenQuotes API."""
    global quotes_data
    try:
        response = requests.get(f"{API_URL}/{API_KEY}")
        response.raise_for_status()
        new_data = response.json()
        quotes_data.extend(new_data)
        print("Data retrieved successfully")
        print(f"Total quotes retrieved: {len(quotes_data)}")  # Debugging: Ensure quotes are fetched
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        messagebox.showerror("Error", f"Failed to fetch data: {e}")


def display_quote(quote, author, image_url):
    """Display the quote in the GUI."""
    # Clear previous quote
    for widget in window.winfo_children():
        widget.destroy()

    # Ensure quote and author are available
    if not quote or not author:
        messagebox.showerror("Error", "Incomplete quote data. Try resetting the app.")
        return

    # Display the quote text
    quote_label = tk.Label(window, text=f'"{quote}"', wraplength=400, font=('Arial', 14), pady=10)
    quote_label.pack()

    # Display the author name
    author_label = tk.Label(window, text=f'- {author}', font=('Arial', 12), pady=5)
    author_label.pack()

    # Add buttons at the bottom again
    button_frame = tk.Frame(window)
    button_frame.pack(side=tk.BOTTOM, pady=20)

    next_button = tk.Button(button_frame, text="Next", command=show_random_quote)
    next_button.grid(row=0, column=0, padx=10)

    reset_button = tk.Button(button_frame, text="Reset", command=reset_data)
    reset_button.grid(row=0, column=1, padx=10)

    image_button = tk.Button(button_frame, text="Image", command=lambda: generate_image_with_quote(quote, author))
    image_button.grid(row=0, column=2, padx=10)

    cancel_button = tk.Button(button_frame, text="Cancel", command=close_application)
    cancel_button.grid(row=0, column=3, padx=10)


def show_random_quote():
    """Show a random quote from the stored data."""
    if quotes_data:
        # Select a random quote and check for the required fields
        quote_obj = random.choice(quotes_data)
        quote = quote_obj.get('q', 'No quote available')
        author = quote_obj.get('a', 'Unknown author')
        display_quote(quote, author, None)
    else:
        messagebox.showerror("Error", "No quotes available. Please reset and fetch new data.")


def reset_data():
    """Reset data by fetching new quotes from the API and appending them."""
    fetch_quotes()
    show_random_quote()


def close_application():
    """Close the application."""
    window.destroy()


# New Functions for Image Generation
def get_nature_image():
    """Fetch a nature image from the local 'nature-image' directory."""
    try:
        image_path = os.path.join('nature-image', 'nature.jpg')  # Replace 'nature.jpg' with the actual image name
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"No image found at {image_path}")
        img = Image.open(image_path)
        return img
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load image from local directory: {e}")
        return None


def add_quote_to_image(image, quote, author):
    """Add a quote with author to the image."""
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()

    text = f'"{quote}" - {author}'

    # Get the bounding box for the text
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Calculate the position to center the text
    width, height = image.size
    position = ((width - text_width) // 2, height - text_height - 50)

    # Add shadow for better visibility
    draw.text((position[0] - 1, position[1] - 1), text, font=font, fill="black")
    draw.text((position[0] + 1, position[1] - 1), text, font=font, fill="black")
    draw.text((position[0] - 1, position[1] + 1), text, font=font, fill="black")
    draw.text((position[0] + 1, position[1] + 1), text, font=font, fill="black")
    draw.text(position, text, font=font, fill="white")

    return image


def save_image(image):
    """Save the image to the 'images' directory."""
    if not os.path.exists('quote-image'):
        os.makedirs('quote-image')

    file_path = os.path.join('quote-image', 'quote_image.png')
    image.save(file_path)
    return file_path


def generate_image_with_quote(quote, author):
    """Generate and save an image with a quote."""
    image = get_nature_image()
    if image:
        image_with_quote = add_quote_to_image(image, quote, author)
        file_path = save_image(image_with_quote)
        messagebox.showinfo("Success", f"Image saved at {file_path}")


# Initialize the Tkinter window
window = tk.Tk()
window.title("ZenQuotes - Inspirational Quotes")
window.geometry("500x400")

# Initial data fetch and display the first quote
fetch_quotes()
show_random_quote()

# Run the Tkinter main loop
window.mainloop()