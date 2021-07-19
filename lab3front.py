#Name: Christopher Bryan
#Purpose: Lab 3 - Front-end
import tkinter as tk
import tkinter.messagebox as tkmb
import sqlite3
import webbrowser

class displayWin(tk.Toplevel):
    def __init__(self, master, *args):
        '''constructor for display window, displays the information'''
        super().__init__(master)
        self.geometry("300x240")
        self.resizable(False, False)
        scroll = tk.Scrollbar(self)
        LB = tk.Listbox(self, height=12, width=50, selectmode="single", yscrollcommand=scroll.set)
        scroll.config(command=LB.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        for info in args:
            LB.insert(tk.END, "Movie: " + info[0])
            LB.insert(tk.END, "Director: " + info[3])
            LB.insert(tk.END, "Starring: ")
            for actor in info[4:]:
                if actor:
                    LB.insert(tk.END, actor)
            LB.insert(tk.END, "")
        LB.pack()

class dialogWin(tk.Toplevel):
    def __init__(self, master, val, *args):
        '''constructor  for dialog window, displays listbox of information'''
        super().__init__(master)
        self.geometry("300x240")
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()
        self.transient(master)
        self.choice = None
        scroll = tk.Scrollbar(self)
        self.lbox = tk.Listbox(self, height=12, width=50, selectmode="single", yscrollcommand=scroll.set)
        scroll.config(command=self.lbox.yview)
        label = tk.Label(self)
        label.pack()

        if val == 1:
            label['text'] = "Click on a movie to select"
        elif val == 2:
            label['text'] = "Click on an actor to select"
        else:
            label['text'] = "Click on a month to select"

        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.lbox.insert(tk.END, *args)
        self.lbox.bind('<<ListboxSelect>>', self.setChoice)
        self.lbox.pack()

    def setChoice(self, event):
        '''setter for user choice'''
        self.choice = self.lbox.curselection()[0]
        self.destroy()

    def getChoice(self):
        '''getter for user choice'''
        return self.choice

class mainWin(tk.Tk):
    
    def __init__(self):
        '''constructor for main window'''
        super().__init__()
        self.title("Movies")
        self.geometry("300x100")
        self.resizable(False, False)
        self.conn = sqlite3.connect("movies.db")
        self.cur = self.conn.cursor()
        F1 = tk.Frame(self)
        tk.Label(self, text="2021 Most Anticipated Movies", fg="red", font=("Arial", 14)).pack()
        tk.Label(F1, text="Search:").grid()
        tk.Button(F1, text="Webpage", fg="blue", command=self.movieDialog).grid(row=0, column=1, padx=10)
        tk.Button(F1, text="Main Actor", fg="blue", command=self.actorDialog).grid(row=0, column=2, padx=10)
        tk.Button(F1, text="Month", fg="blue", command=self.monthDialog).grid(row=0, column=3, padx=10)
        F1.pack()

        self.protocol("WM_DELETE_WINDOW", self.enterX)

    def movieDialog(self):
        '''shows list of movies, if clicked will open a browser unless there is no url'''
        self.cur.execute("SELECT name FROM Movies")
        names = sorted([name[0] for name in self.cur.fetchall()], key=lambda name : name.title())
        dialog = dialogWin(self, 1, *names)
        self.wait_window(dialog)
        choice = dialog.getChoice()
        if choice != None:
            self.cur.execute("SELECT url FROM Movies WHERE name=?", (names[choice],))
            url = self.cur.fetchone()[0]
            if url: #ask if there is no url, should i just go back to main window
                webbrowser.open(url)
            else:
                tkmb.showinfo("No URL", "The movie has no url, now going back to main window!", parent=self)

    def actorDialog(self):
        '''shows list of movies and then shows movie information if clicked'''
        self.cur.execute("SELECT DISTINCT actor0 FROM Movies ORDER BY actor0 ASC")
        firstActor = [actor[0] for actor in self.cur.fetchall()]
        dialog = dialogWin(self, 2, *firstActor)
        self.wait_window(dialog)
        choice = dialog.getChoice()
        if choice != None:
            self.cur.execute("SELECT * FROM Movies WHERE actor0=?", (firstActor[choice],))
            movie = self.cur.fetchall()
            displayWin(self, *movie)


    def monthDialog(self):
        '''shows list of months and then shows movie information if clicked'''
        self.cur.execute("SELECT month FROM Months LIMIT 12")
        months = [month[0] for month in self.cur.fetchall()]
        dialog = dialogWin(self, 3, *months)
        self.wait_window(dialog)
        choice = dialog.getChoice()
        if choice != None:
            self.cur.execute("SELECT * FROM Movies where month=?", (choice+1,))
            movie = self.cur.fetchall()
            displayWin(self, *movie)


    def enterX(self):
        '''exit function when clicking X'''
        self.conn.close()
        self.quit()

win = mainWin()
win.mainloop()