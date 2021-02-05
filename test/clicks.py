import tkinter as tk          # GUI package
from time import sleep, time
#from keyboard import is_pressed
#from pynput.keyboard import Listener
#from pynput import mouse
import math
import random

PI_CAMERA = False

#camera function
def get_file_name():  
    return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]+".h264"

IS_PC = True    # debug in pc
if not IS_PC:
    import RPi.GPIO as GPIO

if PI_CAMERA:
    import picamera # pi camera
    cam = picamera.PiCamera()
    fileName = get_file_name()  

STEP =  4                 # SELECT THE STEP 1 to 4
TIME_LED_ON = 0.2         # Time led on 

#default configuration
square_max_iter     = 3   # max number of iterations
max_timer_click     = 5   # max timer to click image
timer_click_mode    = False # set timer mode, False indicate click mode
right_click_mode    = True # if is True, the box change only with right click inside the box (timer_click_mode MUST be False to use this mode)
square_size         = 200 # square width
click_error         = 0   # click error
random_pos          = True #random position    
random_color        = True # square random color picked from color_options
square_color        = [255,0,0] #RGB color if random color is False
colors_options      = [[255,0,0],[255,255,0],[0,0,255]] #option of colors, only work if random_color is True

# STEP 1: RED square 500x500 pixels in the center of screen
if STEP== 1:
    square_max_iter     = 1   # max number of iterations
    max_timer_click     = 5   # max timer to click image
    square_size         = 500 # square width
    click_error         = 0   # click error
    random_pos          = False #random position
    random_color        = False # square random color picked from color_options
    square_color        = [255,0,0] #RGB color if random color is False
    colors_options      = [[255,0,0],[255,255,0],[0,0,255]] #option of colors, only work if random_color is True

# STEP 2: Random color square 500x500 pixels in the center of screen
if STEP== 2:
    square_max_iter     = 1   # max number of iterations
    max_timer_click     = 5   # max timer to click image
    square_size         = 500 # square width
    click_error         = 0   # click error
    random_pos          = False #random position
    random_color        = True # square random color picked from color_options
    square_color        = [255,0,0] #RGB color if random color is False
    colors_options      = [[255,0,0],[255,255,0],[0,0,255]] #option of colors, only work if random_color is True

# STEP 3: Random color square 200x200 pixels in the center of screen
if STEP== 3:
    square_max_iter     = 1   # max number of iterations
    max_timer_click     = 5   # max timer to click image
    square_size         = 200 # square width pixels
    click_error         = 0   # click error
    random_pos          = False #random position
    random_color        = True # square random color picked from color_options
    square_color        = [255,0,0] #RGB color if random color is False
    colors_options      = [[255,0,0],[255,255,0],[0,0,255]] #option of colors, only work if random_color is True

# STEP 4: Random color square 200x200 pixels in the random position of screen
if STEP== 4:
    square_max_iter     = 3   # max number of iterations
    max_timer_click     = 5   # max timer to click image
    square_size         = 200 # square width
    click_error         = 0   # click error
    random_pos          = True #random position    
    random_color        = True # square random color picked from color_options
    square_color        = [255,0,0] #RGB color if random color is False
    colors_options      = [[255,0,0],[255,255,0],[0,0,255]] #option of colors, only work if random_color is True



#Configure GPIO control  
SUCCESS_LED = 17
FAIL_LED =27

#Function that indicates if the box was pressed or not. The time of the led on
# is added to the time between the appearence of squares.
def turn_on_led(status):
    if not IS_PC:
        GPIO.setmode(GPIO.BCM) #set mode to GPIO control
        GPIO.setup(SUCCESS_LED, GPIO.OUT) # set GPIO 17 as output SUCCESS LED
        GPIO.setup(FAIL_LED, GPIO.OUT) # set GPIO 27 as output FAIL LED

        if status == "SUCCESS":
            GPIO.output(SUCCESS_LED, True) ## turn on SUCCESS LED
            sleep(TIME_LED_ON)
            GPIO.output(SUCCESS_LED, False) ## turn off SUCCESS LED

        elif status == "FAIL":
            GPIO.output(FAIL_LED, True) ## Enciendo FAIL LED
            sleep(TIME_LED_ON)
            GPIO.output(FAIL_LED, False) ## turn off FAIL LED
        GPIO.cleanup() # clear GPIOs

def led_success():
    turn_on_led("SUCCESS")

def led_failed():
    turn_on_led("FAIL")


class ClickApplication:
    def __init__(self, master):
        self.master = master
        self.master.title("Click Tracker v0.1")
        #internals variables
        # variables to control program
        self.square_show = False  #indicates if the square is on screen
        self.square_timer = 0     #used to control time
        self.square_iter = 0      #used to count program iterations
        self.square_pos_x = None     #stores x square's position
        self.square_pos_y = None     #stores y square's coordenate
        self.clicked = False         #indicates if left click is pressed
        self.isRunning = True        #indicates if program is running
        self.changeRightClick = False #indicate right click inside box
        self.score = 0   # score used to return right clicks

        self.w = master.winfo_screenwidth()
        self.h = master.winfo_screenheight()
        #self.master.attributes("-fullscreen", True)
        self.master.configure(background='black')
        self.master.geometry("{}x{}+{}+{}".format(self.w,self.h,-10,-5)) #sets size of windows
        #self.startMouseListener()
        self.createCanvas()
        self.canvas.bind("<Button-1>", self.onclicktkinter)
        self.createColorBox()

        
        #loop of program
        while True:    
            if self.square_iter>square_max_iter:   #checks if program reach max iterations
                break

            if self.square_show == False: #checks if square is on screen, if not, create one
                if self.square_iter >= square_max_iter:
                    break
                print("--------------------------------------\n[+] Square {} created!".format(self.square_iter))
                self.createColorBox() #create square
                print("Square position: {},{}".format(self.square_pos_x,self.square_pos_y))
            
            if timer_click_mode:
                if time()- self.square_timer > max_timer_click or self.clicked: # checks time of square on screen or left button of mouse was clicked
                    self.canvas.delete("all")    #delete all objects in canvas
                    self.square_show = False  #set false to create a new square
                    self.clicked = False         #set false to init click state
                    self.square_timer = time()    #restart timer
            elif self.clicked:
                if self.changeRightClick and right_click_mode:
                    self.canvas.delete("all")    #delete all objects in canvas
                    self.square_show = False  #set false to create a new square
                    self.clicked = False         #set false to init click state
                    self.square_timer = time()    #restart timer
                    self.changeRightClick = False
                elif not right_click_mode:
                    self.canvas.delete("all")    #delete all objects in canvas
                    self.square_show = False  #set false to create a new square
                    self.clicked = False         #set false to init click state
                    self.square_timer = time()    #restart timer
            

            
            
            if self.isRunning == False:  #end program
                break
            
            sleep(0.1)
            self.master.update() #function mandatory to update tkinter gui

        #self.finishMouseLister()   #stop listener when program was ended
        self.master.destroy()        #destroy windows of tkinter

        #finish camera video
        if PI_CAMERA:
            cam.stop_preview()
            cam.stop_recording()
        print("--------------------------------------\n[!] YOUR SCORE IS {} OF {}".format(self.score, square_max_iter))
        print("--------------------------------------\n")
        

    def quitApp(self):
        self.master.quit()

    def startMouseListener(self):
        self.mouse_listener = mouse.Listener(on_click=self.on_click)     #sets mouse listener passing function prior defined
        self.mouse_listener.start()                                 #starts mouse listener

    def finishMouseLister(self):
        self.mouse_listener.stop()   

    def createCanvas(self):
        self.canvas = tk.Canvas(self.master, width=self.w, height=self.h)
        self.canvas.configure(background='black')    #set background color
        self.canvas.pack()

    def createColorBox(self):
        if self.square_show == False: # checks if square is on screen, if not, create it
            if random_pos:
                self.square_pos_x = random.randint(0+square_size,self.w-square_size) #random x position on screen
                self.square_pos_y = random.randint(0+square_size,self.h-square_size) #random y position on screen
            else:
                self.square_pos_x = (self.w-square_size)/2
                self.square_pos_y = (self.w-square_size)/2
            if random_color:
                rcol = random.choice(colors_options)
            else:    
                rcol =  square_color
            colorval = "#%02x%02x%02x" % (rcol[0], rcol[1], rcol[2]) # rgb to hexadecimal format
            self.canvas.create_rectangle(self.square_pos_x, self.square_pos_y, self.square_pos_x + square_size, self.square_pos_y + square_size, fill=colorval) #create blue square
            self.square_show = True   # set true to indicates that square is on screen
            self.square_iter = self.square_iter + 1 # add 1 to program iteration
            self.square_timer = time()    # restart timer
    
    def on_click(self, x, y, button, pressed):
        """ DEPRECATED """
        if pressed:
            print("Mouse clicked at ({0}, {1}) with {2}".format(x*1.25,y*1.25,button))
        if button == mouse.Button.left and pressed==True:       #check if left button is clicked, pressed=Trye indicates pressed, False indicates release
            print("Click position: {},{}".format(x,y))              #debug: show cursor position on console
            if  x>= self.square_pos_x-click_error and x<= self.square_pos_x+square_size+click_error and y>= self.square_pos_y-click_error and y<= self.square_pos_y+square_size+click_error : #check if click is inside square+error area.
                self.score=self.score+1                                   #add 1 to score if is a right click, inside a square+error area.
                print(">> CLICK INSIDE TARGET!")
                led_success()
                self.changeRightClick=True
            else:
                print(">> CLICK FAILED!")
                led_failed()
            self.clicked = True

        if button == mouse.Button.right and pressed ==True: #check if right click is pressed
            print("Right click: {},{}".format(x,y))
    
    def onclicktkinter(self, event):
        x = event.x
        y = event.y
        print("Click position: {},{}".format(x,y))              #debug: show cursor position on console
        if  x>= self.square_pos_x-click_error and x<= self.square_pos_x+square_size+click_error and y>= self.square_pos_y-click_error and y<= self.square_pos_y+square_size+click_error : #check if click is inside square+error area.
            self.score=self.score+1                                   #add 1 to score if is a right click, inside a square+error area.
            print(">> CLICK INSIDE TARGET!")
            led_success()
            self.changeRightClick=True
        else:
            print(">> CLICK FAILED!")
            led_failed()
        self.clicked = True

    
    

def main():
    root = tk.Tk()
    app = ClickApplication(root)
    #root.mainloop()


if __name__ == '__main__':
    main()
