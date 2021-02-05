from pynput.keyboard import Listener
from pynput import mouse

def on_click(self, x, y, button, pressed):
    if pressed:
        print("Mouse clicked at ({0}, {1}) with {2}".format(x*1.25,y*1.25,button))


mouse_listener = mouse.Listener(on_click=self.on_click)     #sets mouse listener passing function prior defined
mouse_listener.start()        
sleep(40)
mouse_listener.stop()