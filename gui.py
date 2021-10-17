import tkinter
import subprocess

main = tkinter.Tk()
main.title('Scripts')
main['bg'] = '#232323'
main.geometry('415x285+800+400')
main.resizable(width=0, height=0)


class RocketButton:
    def __init__(self):
        self.rocket_button = tkinter.Button(
            main, text='Rocket start', command=self.start_rocket,
            bg='#464545', fg='#dadada', bd=0.3, highlightbackground='#3c3b3b', activebackground='#656568')
        self.rocket_button.place(x=15, y=15, width=100, height=65)
        self.process_rocket = None

    def start_rocket(self):
        self.process_rocket = subprocess.Popen(['python3', 'rocket.py'])
        self.rocket_button.configure(text='Rocket stop', command=self.stop_rocket, bg='#4b584b')
        with open('output.txt', 'w') as f:
            print('Rocket started', file=f)

    def stop_rocket(self):
        self.process_rocket.terminate()
        self.rocket_button.configure(text='Rocket start', command=self.start_rocket, bg='#464545')
        open('output.txt', 'w').close()

    def disable_rocket(self):
        self.rocket_button.configure(state=tkinter.DISABLED)

    def enable_rocket(self):
        self.rocket_button.configure(state=tkinter.NORMAL)


class Display:
    def __init__(self):
        self.text_block = tkinter.Label(
            main,
            text=main,
            bg='#1b1b1b',
            fg='#dadada',
            bd=0,
            justify='left',
            padx=10,
            pady=10,
            anchor='nw')
        self.text_block.place(x=140, y=15, width=250, height=250)

    def main(self):
        with open('output.txt', "r") as f:
            self.text_block.config(text=f.read())
        with open('output.txt', "r") as f:
            if len(f.readlines()) >= 14:
                open('output.txt', 'w').close()
        main.after(100, self.main)

    def erase_display(self):
        f = open('output.txt', 'w')
        f.close()


rocket = RocketButton()
Display().main()

main.mainloop()
