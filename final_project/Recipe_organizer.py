import mysql.connector
from tkinter import * 
from PIL import ImageTk, Image
import tkinter as tk
import tkinter.ttk as ttk

logo_photo = None

def connect_to_db():
    global db
    try:
        db = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "Hour@2023",
            database = "recipe"
        )
        # status_label.config(text = "Connected to database successfully!", fg = "green")
    except mysql.connector.Error as err:
        status_label.config(text = f"Error connecting to database: {str(err)}", fg = "red")

def create_window_with_logo_frame(window, title, width, height, previous_window= None):
    top_frame = Frame(window, bg='black', width=width, height=70)
    top_frame.pack()

    global logo_photo
    if not logo_photo:
        logo = Image.open(r"D:\blck_logo.jpg")
        logo = logo.resize((100,50))
        logo_photo = ImageTk.PhotoImage(logo)
    logo_label = Label(window, image=logo_photo, bd=0)
    logo_label.place(x=470, y=10)

    window.title(title) 
    window.geometry(f'{width}x{height}')

    if previous_window:
        back_button = Canvas(window, width=40, height=40, bg='black', highlightthickness=0)
        back_button.place(x=10, y=10)

        # Draw a circle
        back_button.create_oval(5, 5, 35, 35, fill='white', outline='black')

        # Draw an arrow symbol inside the circle
        back_button.create_line(30, 20, 13, 20, width=2, arrow=tk.LAST, fill='black')

        # Bind the button to go back
        back_button.bind("<Button-1>", lambda event: go_back(window, previous_window))

def go_back(current_window, previous_window):
    current_window.withdraw()
    previous_window.deiconify()

def create_status_label(window, text, fg):
    status_label = Label(window, text=text, bg="gray", fg=fg)
    status_label.pack()
    return status_label

def update_recipe_count_label():
    global recipe_count_label
    try:
        if not db:
            connect_to_db()
        
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM recipe")
        count = cursor.fetchone()[0]
        recipe_count_label.config(text=f"Total Recipes: {count}")
    
    except mysql.connector.Error as err:
        print(f"Error fetching recipe count: {str(err)}")

def add_recipe():
    try:
        name = name_entry.get()
        ingredients = ingredients_entry.get()
        direction = direction_entry.get()

        if not name or not ingredients or not direction:
            raise ValueError("Please fill in all required fields. ")

        if not db:
            connect_to_db()

        cursor = db.cursor()
        sql = """ 
            INSERT INTO recipe (name, ingredients, direction)
            VALUES (%s, %s, %s)
        """
        cursor.execute(sql, (name, ingredients, direction))
        db.commit()
        update_recipe_count_label()

        status_label_add = create_status_label(root, 'Add recipe successfully', 'green')

        name_entry.delete(0, END)
        ingredients_entry.delete(0, END)
        direction_entry.delete(0, END)


    except (mysql.connector.Error, ValueError) as err:
        status_label_add = create_status_label(root, f"Error: {str(err)}", 'red')
    
def list_recipe():
    try:
        if not db:
            connect_to_db()
        
        cursor = db.cursor()
        cursor.execute("SELECT name FROM recipe")
        recipes = cursor.fetchall()

        # Create a new window to display all recipe names
        list_window = Toplevel(root)
        create_window_with_logo_frame(list_window, "Recipes", 600, 400, root)

        update_recipe_count_label()
        recipe_count_label_list = Label(list_window, text="", bg="#f8f4f4", font=("Times New Roman", 12))
        recipe_count_label_list.pack(pady=10) # Adjust the position as needed
        recipe_count_label_list.config(text=recipe_count_label.cget("text"))

        list_text = Text(list_window, bg='white', relief=FLAT)
        list_text.pack(expand=True, fill=BOTH)

        # Insert recipe names into the text widget
        for recipe in recipes:
            list_text.insert(END, recipe[0] + "\n", 'center')

        list_text.tag_configure('center', justify='center')

    
    except mysql.connector.Error as err:
        status_label_list = create_status_label(list_window, f"Error: {str(err)}", 'red')

name_label = None
ingredients_label = None
direction_label = None

def update_recipe():
    try:
        if not db:
            connect_to_db()

        cursor = db.cursor()

        update_window = Toplevel(root)
        create_window_with_logo_frame(update_window, "Update recipe", 600, 400, root)
        update_window.config(bg='gray')
       
        #label update recipe
        Label(update_window, text='Recipe name', bg='gray', font=('Time new Roman', 12)).place(x=30, y=130)
        name_entry_update = Entry(update_window)
        name_entry_update.place(x=150, y=130)

        Label(update_window, text='Field to update', bg='gray', font=('Time new Roman', 12)).place(x=30, y=180)
        field_box = ttk.Combobox(update_window, values=['name', 'ingredients', 'direction'])
        field_box.place(x=150, y=180)
        field_box.set("")

        Label(update_window, text='New Value', bg='gray', font=('Time new Roman', 12)).place(x=30, y=230)
        new_value_entry = Entry(update_window)
        new_value_entry.place(x=150, y=230)

        def perform_search():
            global name_label, ingredients_label, direction_label
            
            cursor = db.cursor()
            search = name_entry_update.get()
            sql = "SELECT * FROM recipe WHERE name = %s"
            cursor.execute(sql, (search,))
            result = cursor.fetchone()   

            if result:
                name, ingredients, direction = result

                name_label = Label(update_window, text=f"Name: {name}", bg='gray', font=('Time new Roman', 10), wraplength=225)
                name_label.place(x=350, y=130)
                
                ingredients_label = Label(update_window, text=f"Ingredients: {ingredients}", bg='gray', font=('Time new Roman', 10), wraplength=225, anchor='nw', justify='left')
                ingredients_label.place(x=350, y=180)
                
                direction_label = Label(update_window, text=f"Direction: {direction}", bg='gray', font=('Time new Roman', 10), wraplength=225, anchor='nw', justify='left')
                direction_label.place(x=350, y=230)
            else:
                status_label_perform = create_status_label(update_window, 'recipe not found', 'red')


        #button
        search_button = Button(update_window, text="Search", command=perform_search)
        search_button.place(x=300, y=130)
    
        def update():
            global name_label, ingredients_label, direction_label
            # Retrieve user input
            recipe_name = name_entry_update.get()
            field = field_box.get()
            new_value = new_value_entry.get()

            # Validate user input
            if not recipe_name or not field or not new_value:
                error_label = create_status_label(update_window, 'recipe not found', 'red')
                return error_label

            # Construct SQL query
            sql = f"UPDATE recipe SET {field} = %s WHERE name = %s"
            cursor.execute(sql, (new_value, recipe_name))
            db.commit()
            update_recipe_count_label()


            status_label_update = create_status_label(update_window, "recipe updated successfully!", "green")
            name_entry_update.delete(0,END)
            new_value_entry.delete(0,END)
            
            #hide search results
            if name_label:
                name_label.destroy()
            if ingredients_label:
                ingredients_label.destroy()
            if direction_label:
                direction_label.destroy()

        #update button
        update_button = Button(update_window, text="Update Recipe", font=("Times New Roman", 10), command=update)
        update_button.place(x=250, y=280)

    except (mysql.connector.Error, ValueError) as err:
        status_label_update_recipe = create_status_label(update_window, f"Error: {str(err)}", "red")

#search recipe
def search_recipe():
    try:
        if not db:
            connect_to_db()
        
        # Create a new window for user to search recipe they store
        search_window = Toplevel(root)
        search_window.config(bg='gray')
        create_window_with_logo_frame(search_window, 'search recipe', 600, 200, root)
        
        # Label for search recipe
        Label(search_window, text="Search Recipe", bg='gray').pack(pady=10)
        # Entry field for search
        search_entry = Entry(search_window)
        search_entry.pack(pady=10) 

        # Function to perform search
        def display_recipe():
            cursor = db.cursor()
            search_name = search_entry.get()
            sql = "SELECT * FROM recipe WHERE name = %s"
            cursor.execute(sql, (search_name,))
            result = cursor.fetchone()
            if result:
                name, ingredients, direction = result
                # Create a new window to display recipe details
                recipe_window = Toplevel(root)
                create_window_with_logo_frame(recipe_window, "Recipe Details", 600, 400, search_window) 
                Label(recipe_window, text=f"Name: {name}").place(x=50, y=150)
                Label(recipe_window, text=f"Ingredients: {ingredients}", wraplength=500, anchor='nw', justify='left').place(x=50, y=200)
                Label(recipe_window, text=f"Direction: {direction}", wraplength=500, anchor='nw', justify='left').place(x=50, y=270)
            else:
                status_label_search = create_status_label(search_window, "Recipe not found!", "red")

        # Button to trigger search
        search_button = Button(search_window, text="Search", command=display_recipe)
        search_button.pack(pady=10)

    except mysql.connector.Error as err:
        status_label_search = create_status_label(search_window, f"Error: {str(err)}", "red")

root = Tk()
root.geometry("600x400")
create_window_with_logo_frame(root, "Recipe Organizer", 600, 400)

#bg color
root.config(bg="gray")

def show_cookie_message():
    cookie_window = Toplevel(root)
    cookie_window.geometry("400x250")
    cookie_window.title("Cookie Consent")

    cookie_image = Image.open(r"D:\cookie.gif")
    cookie_image = cookie_image.resize((100, 90), Image.LANCZOS)
    cookie_photo = ImageTk.PhotoImage(cookie_image)
    
    # Label to display the cookie image
    cookie_label = Label(cookie_window, image=cookie_photo)
    cookie_label.image = cookie_photo  # keep a reference
    cookie_label.pack(pady=20)

    message_label = Label(cookie_window, text="This application uses cookies. Do you accept?", font=("Time New Romen", 12))
    message_label.pack(pady=20)

    accept_button = Button(cookie_window, text="Accept", command=lambda: accept_cookie(cookie_window))
    accept_button.pack(side=LEFT, padx=20)

    reject_button = Button(cookie_window, text="Reject", command=lambda: reject_cookie(cookie_window))
    reject_button.pack(side=RIGHT, padx=20)

def accept_cookie(cookie_window):
    cookie_window.destroy()
    root.state('normal')  # Revert the main window to normal state

def reject_cookie(cookie_window):
    cookie_window.destroy()
    root.destroy()  # Close the main window

# Schedule the cookie message to be shown after 3 seconds
root.after(3000, show_cookie_message)

# Load and resize the image to display on the left side
image1 = Image.open(r"D:\image1.jpg")
image1 = image1.resize((200, 275))
image1_photo = ImageTk.PhotoImage(image1)
# Create a label to display the image
image_label = Label(root, image=image1_photo)
image_label.place(x=50, y=90)

text_label = Label(root, text="Welcome to Recipe Organizer!",bg="gray", font=("Times New Roman", 16))
text_label.place(x=270, y=90)

# Label and entry fields for recipe details
Label(root, text="Name: ", bg="gray", font=("Times New Roman", 12)).place(x=300, y=130)
name_entry = Entry(root)
name_entry.place(x=400, y=130)

Label(root, text="Ingredients: ", bg="gray", font=("Times New Roman", 12)).place(x=300, y=160)
ingredients_entry = Entry(root)
ingredients_entry.place(x=400, y=160)

Label(root, text="Direction: ", bg="gray", font=("Times New Roman", 12)).place(x=300, y=190)
direction_entry = Entry(root)
direction_entry.place(x=400, y=190)

# Add button
add_button = Button(root, text="Add Recipe", font=("Times New Roman", 10), command=add_recipe)
add_button.place(x=355, y=230)

# List button
list_button = Button(root, text="List All Recipe", font=("Times New Roman", 10), command=list_recipe)
list_button.place(x=350, y=260)

#search recipe button
search_button = Button(root, text = "Search", font=("Times New Roman", 10), command = search_recipe)
search_button.place(x=369, y=290)

# Add button to update student record
update_button = Button(root, text="Update Recipe",font=("Times New Roman", 10), command=update_recipe)
update_button.place(x=350, y=320)

# amount of the recipes
recipe_count_label = Label(root, text="", bg="gray", font=("Times New Roman", 12))
recipe_count_label.place(x=50, y=370)

connect_to_db()
update_recipe_count_label()
root.mainloop()