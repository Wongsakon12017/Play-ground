from tkinter.simpledialog import askfloat
from tkinter import *
top = Tk()

top.geometry("300x300")

L1 = Label(top, text ="sdd")


text=""
number = 0
short_number = ""
hand_list = []

def cal(char_):
    global text,number,short_number,hand_list
    
    if not isinstance(char_,int):
        if text[-1] in ['0','1','2','3','4','5','6','7','8','9',]:
            hand_list.append(int(short_number))
            short_number = ""
            if char_ != '=':
                print('not equal')
                text += char_    
                hand_list.append(char_)            
            else: #text equal
                text =""
                if hand_list[-1] in ['+','-','x','/']:
                    hand_list = hand_list[:-1] 
                #cakculate
                                
    else:
        text += str(char_)
        short_number += str(char_)
    print(hand_list)     
    L1.config(text=text)

B1 = Button(top, text ="1", command = lambda: cal(1))
B2 = Button(top, text ="2", command = lambda: cal(2))
B3 = Button(top, text ="3", command = lambda: cal(3))
B4 = Button(top, text ="+", command = lambda: cal('+'))
B5 = Button(top, text ="=", command = lambda: cal('='))

L1.place(x=50,y=0)
B1.place(x=50,y=50)
B2.place(x=100,y=50)
B3.place(x=150,y=50)
B4.place(x=200,y=50)
B5.place(x=250,y=50)

top.mainloop()