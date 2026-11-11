import tkinter as tk

def close_application():
    """Close the application."""
    window.quit()  # Exit the main loop
    window.destroy()  # Properly destroy the window

# Initialize the Tkinter window
window = tk.Tk()
window.title("Hello World App")
window.geometry("300x150")  # Set the size of the window

# Create a label to display the "Hello World" message
hello_label = tk.Label(window, text="Hello World", font=('Arial', 16))
hello_label.pack(pady=20)  # Add padding for space

# Create the Cancel button to close the application
cancel_button = tk.Button(window, text="Cancel", command=close_application)
cancel_button.pack(pady=10)

# Run the Tkinter main loop
window.mainloop()