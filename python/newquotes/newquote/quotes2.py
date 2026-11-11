import requests
import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import io

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
    # Update the quote label
    quote_label.config(text=f'"{quote}"')

    # Update the author label
    author_label.config(text=f'- {author}')

    # Clear the previous image if it exists
    if image_label.winfo_exists():
        image_label.config(image='')  # Clear the image

    # If there's an image, display it
    if image_url:
        try:
            img_response = requests.get(image_url)
            img_data = Image.open(io.BytesIO(img_response.content))
            img_resized = img_data.resize((150, 150), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(img_resized)
            image_label.config(image=img)
            image_label.image = img  # Keep a reference to avoid garbage collection

        except Exception as e:
            print(f"Error loading image: {e}")
            image_label.config(text="Image not available")
    else:
        image_label.config(text="No image")


def show_random_quote():
    """Show a random quote from the stored data."""
    if quotes_data:
        # Select a random quote and check for the required fields
        quote_obj = random.choice(quotes_data)
        quote = quote_obj.get('q', 'No quote available')
        author = quote_obj.get('a', 'Unknown author')
        image_url = quote_obj.get('i', None)
        display_quote(quote, author, image_url)
    else:
        messagebox.showerror("Error", "No quotes available. Please reset and fetch new data.")


def reset_data():
    """Reset data by fetching new quotes from the API and appending them."""
    fetch_quotes()
    show_random_quote()


def close_application():
    """Close the application."""
    window.quit()  # Correct way to exit the Tkinter loop
    window.destroy()  # Close the window completely


# Initialize the Tkinter window
window = tk.Tk()
window.title("ZenQuotes - Inspirational Quotes")
window.geometry("500x500")

# Create placeholders for the sections
image_label = tk.Label(window, text="Image will appear here", padx=10, pady=10)
image_label.pack()

quote_label = tk.Label(window, text="Quote will appear here", wraplength=400, font=('Arial', 14), pady=10)
quote_label.pack()

author_label = tk.Label(window, text="Author will appear here", font=('Arial', 12), pady=5)
author_label.pack()

# Add buttons at the bottom
button_frame = tk.Frame(window)
button_frame.pack(side=tk.BOTTOM, pady=20)

next_button = tk.Button(button_frame, text="Next", command=show_random_quote)
next_button.grid(row=0, column=0, padx=10)

reset_button = tk.Button(button_frame, text="Reset", command=reset_data)
reset_button.grid(row=0, column=1, padx=10)

cancel_button = tk.Button(button_frame, text="Cancel", command=close_application)
cancel_button.grid(row=0, column=2, padx=10)

# Initial data fetch and display the first quote
fetch_quotes()
show_random_quote()

# Run the Tkinter main loop
window.mainloop()