import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import yaml

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

COLORS = ['red', 'blue', 'olive', 'teal', 'cyan', 'green', 'black', 'purple', 'orange', 'brown','crimson','yellow']

class App(ctk.CTk):
    def __init__(self, image_path,config_file_path):
        super().__init__()

        # configure window
        self.title("Labling Bounding box")
        self.geometry(f"{1400}x{600}")
        #loading image
        self.load_image(image_path)
        
        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # bounding box initialization
        self.rectangles = []
        self.selected_rectangle = None
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.config=self.load_config(config_file_path)
        self.class_dict=self.config['names']
        self.class_name = list(self.config['names'].values())
        
        
        # create sidebar frame with widgets
        ##=================left side bar frame andbutton=========================##
        self.sidebar_frame = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.selection_mode = False
        self.sidebar_button_2 = ctk.CTkButton(self.sidebar_frame, command=self.save_coordinates, text="Save Coordinates")
        self.sidebar_button_2.grid(row=3, column=0, padx=20, pady=10)
        self.clear_all_button = ctk.CTkButton(self.sidebar_frame, command=self.clear_all_rectangles, text="Clear All Rectangles")
        self.clear_all_button.grid(row=4, column=0, padx=20, pady=10)
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.appearance_mode_optionemenu.set("Light")


        ##==============right side sidebar==================##
        self.rsidebar_frame =ctk.CTkFrame(self,width=40,corner_radius=1)
        self.rsidebar_frame.grid(row=0, column=3, rowspan=2, sticky="nsew")

        # ========create textbox==============#
        self.textbox = tk.Listbox(self.rsidebar_frame, width=31, height=50 ,yscroll=True, xscroll=True)
        self.textbox.grid(row=2, column=3, sticky = 'nsew')

        ###================class dropdown button==============###
        self.class_menu = ctk.CTkOptionMenu(self.rsidebar_frame, values=self.class_name,command=self.selected_class,width=200)
        self.class_menu.grid(row=0, column=3, padx=20, pady=(10, 10))
        self.class_menu.set(self.class_dict[0])
        self.selected_class_key = 0


    def selected_class(self,uselected_class:str):
        self.selected_class_key = next(key for key, value in self.class_dict.items() if value == uselected_class)

    #####===================Changing the mode Light and Dark mode=============############
    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    # toggle the selection button
    
    ####=============Image loading in canvas================#########
    def load_image(self,image_path):
        self.image_path = image_path
        self.image = Image.open(image_path)
        self.photo = ImageTk.PhotoImage(self.image,master=self)
        if self.image is None:
            print(f"Error: Unable to load image from {image_path}")
            return

        # create a scrollable frame
        self.frame = ctk.CTkFrame(self,width=self.photo.width(),height=self.photo.height())
        self.frame.grid(row=1, column=1,padx=(1, 0), pady=(1, 0), sticky="w"+"n")
        # print(self.frame.winfo_width(), self.frame.winfo_height())

        #creating scrollbar
        hsbar= tk.Scrollbar(self.frame, orient="horizontal")
        vsbar= tk.Scrollbar(self.frame, orient="vertical")

        self.canvas = ctk.CTkCanvas(self.frame,width=self.photo.width(),height=self.photo.height(),
                                    scrollregion=(0,0,self.photo.width(),self.photo.height()),
                                    xscrollcommand=hsbar.set, yscrollcommand=vsbar.set)
        

        hsbar.pack(side="bottom", fill='x')
        vsbar.pack(side="right", fill="y")

        self.canvas.pack(side="left",expand="yes",fill="both")


        hsbar.configure(command=self.canvas.xview)
        vsbar.configure(command=self.canvas.yview)
       
        # Load image onto canvas
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        
        #button function on canvas
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<ButtonPress-3>",self.delete_selected_rectangle)

        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        
    def on_mousewheel(self, event):
        if event.state & 0x1:
            if event.delta < 0:  
                self.canvas.xview_scroll(1 , "units")     
            else:
                self.canvas.xview_scroll(-1 , "units")
        else:
            print(event.delta)
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

        
    ####===================Deleting all rectangel at once================#########
    def clear_all_rectangles(self):
        for rect_data in self.rectangles:
            rect = rect_data[0] 
            self.canvas.delete(rect)
        self.rectangles = [] 
        self.selected_rectangle = None
        self.update_text_box()  

    def on_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)  
        self.start_y = self.canvas.canvasy(event.y)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline=COLORS[self.selected_class_key], width=5)

    def on_drag(self, event):
        if self.selected_rectangle==1:
            pass
        else:
            self.end_x = min(max(self.canvas.canvasx(event.x), 0), self.photo.width())
            self.end_y = min(max(self.canvas.canvasy(event.y), 0), self.photo.height())

            if self.end_y+35 > self.frame.winfo_height():
                self.canvas.yview_scroll(1, "units")
            else:
                self.canvas.yview_scroll(-1,"units")

            if self.end_x+35 > self.frame.winfo_width():
                self.canvas.xview_scroll(1, "units")
            else:
                self.canvas.xview_scroll(-1, "units")

            # if self.end_y+35 < self.frame.winfo_height():
            #     self.canvas.yview_scroll(1 , "units")
            # if self.end_x+35<self.frame.winfo_width():
            #     print(self.end_x)
            #     self.canvas.xview_scroll(1, "units")
            self.canvas.coords(self.rect, self.start_x, self.start_y, self.end_x, self.end_y)
    
                    
    def on_release(self, event):
            if self.end_x < self.start_x:
                self.end_x,self.start_x=self.start_x,self.end_x
            if  self.end_y < self.start_y:
                self.end_y,self.start_y=self.start_y,self.end_y
            coordinates = (self.rect,int(self.start_x), int(self.start_y), int(self.end_x), int(self.end_y),self.selected_class_key)
            self.rectangles.append(coordinates)
            self.selected_rectangle = coordinates[0]
            self.update_text_box()
       

    def update_text_box(self):  
        self.textbox.delete(0,tk.END)
        font = ("Arial", 12)  # Change the font family and size as desired
        self.textbox.configure(font=font)
        for i, rectangle in enumerate(self.rectangles):
            self.textbox.insert(tk.END, f"Rectangle{i+1}: {rectangle}\n")
            self.textbox.itemconfig(tk.END,fg=COLORS[int(rectangle[-1])])


    #####=============Deleting only the selected rectangel================########
    def delete_selected_rectangle(self,event):
        print("hello")
        x = self.canvas.canvasx(event.x)  # Adjust for scroll position
        y = self.canvas.canvasy(event.y)
        print(x,y)

        self.selected_rectangle=None
        for rect in self.rectangles:
            lx,ly,rx,ry = rect[1],rect[2],rect[3],rect[4]
            if lx <= x <= rx and ly <= y <= ry:
                    self.selected_rectangle = rect[0]
                    break
    
        if self.selected_rectangle==1:
            pass
        else:
            if self.selected_rectangle:
                self.canvas.delete(self.selected_rectangle)
                for rect in self.rectangles:
                    if rect[0] == self.selected_rectangle:
                        self.rectangles.remove(rect)
                        self.selected_rectangle = None
                        break
                self.update_text_box()

    ####===========saving the bounding box coordinate=============##########
    def save_coordinates(self):
        with open("rectangle_coordinates.txt", "w") as f:
            for rectangle in self.rectangles:
                f.write(f"{rectangle[-1]},{rectangle[1]},{rectangle[2]},{rectangle[3]},{rectangle[4]}\n")
        print("Coordinates saved to rectangle_coordinates.txt")

    ####===========loading config file==================########
    def load_config(self,file_path):  
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
            return config  
        

if __name__ == "__main__":
    image_path = "C:/Users/shres/OneDrive/Desktop/Office/det/OCR_training/bounding box software/IMG1.bmp"
    conf="C:/Users/shres/OneDrive/Desktop/Office/det/OCR_training/bounding box software/data.yaml"
    app = App(image_path,conf)
    app.mainloop()
