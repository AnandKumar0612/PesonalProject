from tkinter import *
main = Tk()
main.geometry("400x250")
main.title("New tutorial!")
m = Button(main, text="Stop", width=25, command=main.destroy)
m.pack()
main.mainloop()