# -*- coding: utf-8 -*-
"""
Created on Mon May 10 21:36:53 2021

@author: Ahmed EL-brawany
"""

from tkinter import Tk, Checkbutton, IntVar, Toplevel, Label, Entry, Listbox, messagebox, Button, END, ANCHOR
from PIL import Image , ImageTk
from tkinter import ttk
from tkinter import filedialog
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from skimage.util import random_noise
import skimage.exposure as exposure
import os
import io
import math

process_constants = []
processed_images = []
to_do_list =[]
run = 1
save_path = "path"

def display_in_oneImage ():
    """
    this function is used to produce an image which contains all processed images 
    including the original image in on image.
    """
    rows_columns = math.ceil(len(processed_images)**.5)
    to_do_list.insert(0, "Original Image")
    fig = plt.figure(figsize=(10,10))
    if len(to_do_list) == len(processed_images):
        for i in range(len(processed_images)):
            plt.subplot(rows_columns, rows_columns, i+1)
            if len(processed_images[i].shape) < 3:    
                processed_images[i] = cv.cvtColor(processed_images[i], cv.COLOR_BGR2RGB)
            plt.imshow(processed_images[i])
            plt.title(f'{to_do_list[i]}')
            plt.xticks()
            plt.yticks()
        
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        img2 = np.frombuffer(buf.getvalue(), dtype=np.uint8)
        buf.close()
        img2 = cv.imdecode(img2, 1)
        img2 = cv.cvtColor(img2, cv.COLOR_BGR2RGB)
        
        ImageTk.PhotoImage(image=Image.fromarray(img2))
        run_in_another_window(img2, "All images")
        if not stop:
            processed_images.append(img2)
            to_do_list.append('all images')

def cvtoimage(cv_img):
    """
    this function is used to convert image read by opencv format to photoImage
    format to be suitable for tkinter widgets
    """
    img = cv_img.copy()
    if cv_img.shape[0]> 250 or cv_img.shape[1]>250:
        img = cv.resize(cv_img, (250,250), interpolation = cv.INTER_AREA)
    if not len(cv_img.shape)<3:
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(img)
    return img

def entry_wText(entry, text): #this function is used to write the image path and save as path in thier entries  
    entry.delete(0, END)
    entry.insert(0, text)

def button1_clicked(): # image path browse button function to get the path
    path = filedialog.askopenfilename(initialdir='/', title='Select Image',  filetypes=(('image files', '.png'), ('image files', '.jpg'))) # these two lines is to get the selected file location by user
    entry_wText(img_path, path)



def button2_clicked(): #save as browse button function to get the path
    path = filedialog.askdirectory()
    entry_wText(modified_img_path, path)
    
def process_constants_button_clicked(sub_root, process, constant):
    """
    this function is triggered when the Enter button in the get process constants window
    is activated. and is used to add the process constants to the process_constants list
    Inputs:
        sub_root: the small window (topLevel()) made in the add_process_constants function
        process: type of process processed
        constant: constants entered by user in the sub_root window
    
    """
    if process == "Brightness Adjustment" or process == "Rotation":
        try:
            process_constants.append(int(constant.get()))
            sub_root.destroy()
        except:
            messagebox.showerror("Error", "The value must be an integer number.", parent= sub_root)
            
    elif process == "Contrast Adjustment":
        try:
            process_constants.append(float(constant.get()))
            sub_root.destroy()
        except:
            messagebox.showerror("Error", "Contrast constant must be a float number.", parent= sub_root)
   
        
    elif process == "Translation":
        try:
            process_constants.append((int(constant[0].get()), int(constant[1].get())))
            sub_root.destroy()
        except:
            messagebox.showerror("Error", "Translation in x or y must be an integer number.", parent= sub_root)
   
    elif process == "Scaling":
        try:
            process_constants.append((float(constant[0].get()), float(constant[1].get())))
            sub_root.destroy()
        except:
            messagebox.showerror("Error", "Scaling in x or y must be a float number.", parent= sub_root)
    
    elif process == "Salt" or process == "Pepper":
        try:
            if float(constant.get())>1 or float(constant.get())<0:
                raise Exception('Error')
            process_constants.append(float(constant.get()))
            sub_root.destroy()
        except:
            messagebox.showerror("Error", "Amount value must be between 0 and 1.", parent= sub_root)
    
    elif process == "Salt & Pepper":
        try:
            amt =float(constant[0].get())
            sp = float(constant[1].get())
            if amt > 1 or amt < 0 or sp > 1 or sp <0:
                raise Exception('Error')
            process_constants.append((amt, sp))
            sub_root.destroy()
        except:
            messagebox.showerror("Error", "Amount and salt vs pepper\n values must be between 0 and 1.", parent= sub_root)
    
    elif process == "Gaussian" or process == "Speckle":
        try:
            process_constants.append((float(constant[0].get()), float(constant[1].get())))
            sub_root.destroy()
        except:
            messagebox.showerror("Error", "Mean and Variance values\n must be float numbers.", parent= sub_root)

    elif process == "Average" or process == "Median":
        try:
            if int(constant.get()) <= 0 :
                raise Exception("Error")
            process_constants.append(int(constant.get()))
            sub_root.destroy()
        except:
            messagebox.showerror("Error", "kernel size must be an integer value grater than 0", parent = sub_root) 

    elif process == "Gaussian_blur" or process =="LoG":
        try:
            if int(constant[0].get()) <= 0 or int(constant[0].get()) % 2 == 0 or float(constant[1].get()) < 0:
                raise Exception("Errot")
            process_constants.append((int(constant[0].get()), float(constant[1].get())))
            sub_root.destroy()
        except:
            messagebox.showerror("Error", "kernel size must be an integer odd value grater than 0\nSigma vlaue must be a non-negative float value ", parent = sub_root)

    elif process == "Canny":
        try:
            if int(constant[0].get()) > int(constant[1].get()):
                raise Exception('Error')
            process_constants.append((int(constant[0].get()), int(constant[1].get())))
            sub_root.destroy()
        except:
            messagebox.showerror("Error", "threshold 1 must be less than threshold 2\n and both values must be integer values", parent = sub_root)
            
    elif process == "Hough Transform line detection":
        try:
            if int(constant[0].get()) < 0 or int(constant[1].get()) < 0:
                raise Exception('Error')
            process_constants.append((int(constant[0].get()), int(constant[1].get())))
            sub_root.destroy()
        except:
            messagebox.showerror("Error", "the values must be non negative integers", parent= sub_root)
              
    elif process == "Hough Transform circle detection":
        try:
            if int(constant[0].get()) < 0 or int(constant[1].get()) < 0:
                raise Exception('Error')
            process_constants.append((int(constant[0].get()), int(constant[1].get())))
            sub_root.destroy()
        except:
            messagebox.showerror("Error", "the values must be non negative integers", parent= sub_root)
                
    elif process == "Dilation" or process == "Erosion" or process == "Close" or process == "Open":
        try:
            if int(constant[0].get()) < 0 or int(constant[1].get()) < 0:
                raise Exception('Error')
            process_constants.append((int(constant[0].get()), int(constant[1].get())))
            sub_root.destroy()
        except:
            messagebox.showerror("Error", "the values must be non negative integers", parent= sub_root)

def run_in_another_window(img, title):
    """
    this function is used to create a window to display outputs in another window
    """
    img2 = img.copy()
    run_window = Toplevel(root)
    run_window.title(title)
    run_window.geometry("1350x700+0+0")
    run_window.config(bg= "#444444")
    
    img2 = cv.resize(img2, (img2.shape[0], img2.shape[1]), interpolation = cv.INTER_AREA)
    
    if not len(img2.shape)<3:
        img2 = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    img2 = Image.fromarray(img2)
    img2 = ImageTk.PhotoImage(img2)
    
    run_window_label = Label(run_window, image=img2, width=1350, height= 600, bg="#444444", anchor='nw')
    run_window_label.place(x=0, y=0)
    
    next_step_btn2 = Button(run_window, text="Next Step >", font=("times new roman", 10, "bold"),bg="#2069e0", fg="white", bd=0,command = lambda: var5.set(1))
    next_step_btn2.place(x=1250, y=620)

    run_window.protocol("WM_DELETE_WINDOW", lambda: save_window_closed(None))

    next_step_btn2.wait_variable(var5)
    try:
        run_window.destroy()
    except:
        pass
            
def add_process_constants(process):
    """
    this function is used to make a small window (sub_root) to get the user constants
    Inputs:
        process: the type of process processed, based on the process it will display 
                 a certain shape of the sub_root window
    """
    not_needed_processes = set(["Histogram Equalization", "Histogram", "Poisson", "Bilateral",
                                "Sobel_x", "Sobel_y", "Sobel", "Prewitt_x", "Prewitt_y",
                                "Prewitt", "Scharr", "Laplacian", "To binary image", "Skeleton"])
    sub_root = Toplevel(root)
    sub_root.title("Get Process Constants")
    sub_root.geometry("400x200+500+200")
    sub_root.config(bg='#444444')
    label1 = Label(sub_root, font=("times new roman", 10), bg='#444444', fg="white" )
    label2 = Label(sub_root, font=("times new roman", 10), bg='#444444', fg="white" )
    constant1 = Entry(sub_root, font=("times new roman", 10, "bold"), justify="center")
    constant2 = Entry(sub_root, font=("times new roman", 10, "bold"), justify="center")
    enter_btn=Button(sub_root, text ="Enter", font = ("times new roman", 10, "bold"), bg ="#2069e0", fg='white', width = 13, height=1, bd=0 )
    
    if process == "Brightness Adjustment":
        label1.config(text="Brightness Constant: ")
        label1.place(x=30, y=50)
        constant1.place(x=160, y=54)
        enter_btn.place(x=200, y=100)
        enter_btn.config(command = lambda: process_constants_button_clicked(sub_root, process, constant1))
    
    elif process == "Contrast Adjustment":
        label1.config(text="Contrast Constant")
        label1.place(x=30, y=50)
        constant1.place(x=160, y=54)
        enter_btn.place(x=200, y=100)
        enter_btn.config(command = lambda: process_constants_button_clicked(sub_root, process, constant1))
    
    elif process in not_needed_processes :
        #process_constants_button_clicked(sub_root, process, constant1)
       # process_constants.append(0)
        sub_root_closed(sub_root, process)
    
    elif process == "Translation" or process =="Scaling":
        label1.config(text="x: ")
        label1.place(x=30, y=50)
        label2.config(text="y: ")
        label2.place(x=30, y=70)
        constant1.place(x=160, y=54)
        constant2.place(x=160, y=74)
        enter_btn.place(x=200, y=100)
        enter_btn.config(command = lambda: process_constants_button_clicked(sub_root, process, (constant1, constant2)))
    
    elif process == "Rotation":
        label1.config(text="Rotate by: ")
        label1.place(x=30, y=50)
        constant1.place(x=160, y=54)
        enter_btn.place(x=200, y=100)
        enter_btn.config(command = lambda: process_constants_button_clicked(sub_root, process, constant1))
    
    
    elif process == "Salt" or process == "Pepper":
        label1.config(text="Amount: ")
        label1.place(x=30, y=50)
        constant1.place(x=160, y=54)
        enter_btn.place(x=200, y=100)
        label2.config(text = "*Amount is the Proportion of image pixels to replace with noise. \nvalue must be between 0 and 1 (default value .05)*")
        label2.place(x=20, y=130)
        enter_btn.config(command = lambda: process_constants_button_clicked(sub_root, process, constant1))
    
    elif process == "Salt & Pepper":
        label1.config(text="Amount: ")
        label1.place(x=30, y=50)
        label2.config(text="salt vs pepper: ")
        label2.place(x=30, y=70)
        constant1.place(x=160, y=54)
        constant2.place(x=160, y=74)
        enter_btn.place(x=200, y=100)
        enter_btn.config(command = lambda: process_constants_button_clicked(sub_root, process, (constant1, constant2)))
        Label(sub_root, text ="*Amount: the Proportion of image pixels to replace with noise. \n value must be between 0 and 1 (default value .05)\n salt vs pepper: Proportion of salt vs. pepper noise\n value must be between 0 and 1 (default value .5)*", font=("times new roman", 10), bg='#444444', fg="white", justify="left").place(x=20, y=130)
    
    elif process == "Gaussian" or process == "Speckle":
        label1.config(text="Mean: ")
        label1.place(x=30, y=50)
        label2.config(text="Variance: ")
        label2.place(x=30, y=70)
        constant1.place(x=160, y=54)
        constant2.place(x=160, y=74)
        enter_btn.place(x=200, y=100)
        enter_btn.config(command = lambda: process_constants_button_clicked(sub_root, process, (constant1, constant2)))
        Label(sub_root, text ="*Mean: Mean of random distribution. (default value 0)\n Variance: Variance of random distribution\n (default value .01)*", font=("times new roman", 10), bg='#444444', fg="white", justify="left").place(x=20, y=130)
    
    elif process == "Average" or process == "Median":
        label1.config(text="Kernel size (m x m): ")
        label1.place(x=30, y=50)
        constant1.place(x=160, y=54)
        enter_btn.place(x=200, y=100)
        label2.config(text = "*kernel size value must be only one value m\nand the dimensions of the kernel will be m x m*")
        label2.place(x=20, y=130)
        enter_btn.config(command = lambda: process_constants_button_clicked(sub_root, process, constant1))
    
    elif process == "Gaussian_blur" or process == "LoG":
        label1.config(text="Kernel size (mxm): ")
        label1.place(x=30, y=50)
        label2.config(text="Sigma: ")
        label2.place(x=30, y=70)
        constant1.place(x=160, y=54)
        constant2.place(x=160, y=74)
        enter_btn.place(x=200, y=100)
        enter_btn.config(command = lambda: process_constants_button_clicked(sub_root, process, (constant1, constant2)))
        Label(sub_root, text ="*kernel size value must be only one odd value m\nand the dimensions of the kernel will be m x m*", font=("times new roman", 10), bg='#444444', fg="white", justify="left").place(x=20, y=130)
         
    elif process == "Canny":
        label1.config(text="Threshold 1: ")
        label1.place(x=30, y=50)
        label2.config(text="Threshold 2: ")
        label2.place(x=30, y=70)
        constant1.place(x=160, y=54)
        constant2.place(x=160, y=74)
        enter_btn.place(x=200, y=100)
        enter_btn.config(command = lambda: process_constants_button_clicked(sub_root, process, (constant1, constant2)))
        Label(sub_root, text ="*threshold 2 must be greater than threshold 1*", font=("times new roman", 10), bg='#444444', fg="white", justify="left").place(x=20, y=130)
    
    elif process == "Hough Transform line detection":
        label1.config(text="minLineLength: ")
        label1.place(x=30, y=50)
        label2.config(text="maxLineGap: ")
        label2.place(x=30, y=70)
        constant1.place(x=160, y=54)
        constant2.place(x=160, y=74)
        enter_btn.place(x=200, y=100)
        enter_btn.config(command = lambda: process_constants_button_clicked(sub_root, process, (constant1, constant2)))
        Label(sub_root, text ="*minLineLength: Minimum line length. Line segments shorter than that are rejected*\n*maxLineGap: Maximum allowed gap between points on the same line to link them*", font=("times new roman", 10), bg='#444444', fg="white", justify="left").place(x=20, y=130)
   
    elif process == "Hough Transform circle detection":
        label1.config(text="minRadius: ")
        label1.place(x=30, y=50)
        label2.config(text="maxRadius: ")
        label2.place(x=30, y=70)
        constant1.place(x=160, y=54)
        constant2.place(x=160, y=74)
        enter_btn.place(x=200, y=100)
        enter_btn.config(command = lambda: process_constants_button_clicked(sub_root, process, (constant1, constant2)))
        Label(sub_root, text ="*minRadius: Minimum circle radius*\n*maxRadius: Maximum circle radius* ", font=("times new roman", 10), bg='#444444', fg="white", justify="left").place(x=20, y=130)

    elif process == "Dilation" or process == "Erosion" or process == "Close" or process == "Open":
        label1.config(text="Kernel size (mxm): ")
        label1.place(x=30, y=50)
        label2.config(text="Iterations: ")
        label2.place(x=30, y=70)
        constant1.place(x=160, y=54)
        constant2.place(x=160, y=74)
        enter_btn.place(x=200, y=100)
        enter_btn.config(command = lambda: process_constants_button_clicked(sub_root, process, (constant1, constant2)))
        Label(sub_root, text ="*iterations: number of times \nthe kernel will be iterated on the image*", font=("times new roman", 10), bg='#444444', fg="white", justify="left").place(x=20, y=130)

    
    try:
        sub_root.grab_set()
        sub_root.protocol("WM_DELETE_WINDOW", lambda: sub_root_closed(sub_root, process))
    except:
        pass
    
def save_window():
    """
    this function is used to create the save window to ask the useer wheather 
    he/she wants to save the ouput images or not
    """
    stop_btn['state']= 'disabled'
    sub_root = Toplevel(root)
    sub_root.title("Save")
    sub_root.grab_set()
    sub_root.config(bg="#444444")
    sub_root.geometry("400x200+500+200")
    label = Label(sub_root, text="Do you want to save the images?", font=("times new roman", 13, "bold"), bg="#444444", fg="white", bd=0)
    label.place(x=70, y=30)
    yes = Button(sub_root, text ="yes", font = ("times new roman", 10, "bold"), bg ="#2069e0", fg='white', width = 13, height=1, bd=0 )
    yes.place(x=30, y=100)
    yes.config(command = lambda: save(sub_root))
    no = Button(sub_root, text ="no", font = ("times new roman", 10, "bold"), bg ="#2069e0", fg='white', width = 13, height=1, bd=0 )
    no.place(x=270, y=100)
    no.config(command = lambda: save_window_closed(sub_root))
    sub_root.protocol("WM_DELETE_WINDOW", lambda: save_window_closed(sub_root))


def save (sub_root) :
    """
    this function is used for the save operation in case the user clicked yes
    in the save window
    """
    global save_path
    try:
        
        if not os.path.isdir(save_path):
            raise Exception('Error')
        abbriviations = {"Brightness Adjustment": "BA", "Contrast Adjustment": "CA",
                         "Histogram": "Hist", "Histogram Equalization": "HE",
                         "Translation": "Trans", "Scaling": "Scale", "Rotation": "Rotation", "Salt": "salt",
                         "Pepper": 'pepper', "Salt & Pepper": "s&p", "Gaussian": "gauss_noise",
                         "Poisson": 'poisson', "Speckle": 'speckle', "Average": "avg",
                         "Median": 'median', 'Gaussian_blur': 'gaussian_blur', 'Bilateral': 'bilateral', "Sobel_x": 'sobel_x', "Sobel_y": "sobel_y", 
                         "Sobel": 'sobel', "Prewitt_x": 'prewitt_x', "Prewitt_y": 'prewitt_y',
                         "Prewitt": 'prewitt', 'Scharr': 'scharr', 'Laplacian': 'laplacian', 'LoG': 'log', 
                         "Canny": 'canny', "Hough Transform line detection":"HTLD", "Hough Transform circle detection": "HTCD",
                         "To binary image": "binary image", "Dilation": "dilated image", "Erosion": "eroded image", "Open": "open", "Close": "close", "Skeleton": "skeleton", "all images": "all images"}

        for process in range(len(to_do_list)-1):
            cv.imwrite(save_path+f"/{process+1}- {abbriviations[to_do_list[process+1]]} ({run}).jpg", processed_images[process +1])
           
        save_window_closed(sub_root)
    except :
        save_window_closed(sub_root)        
        messagebox.showerror("Error", "save path doesn't exist please check the path again.", parent = root)
                
        
        
def save_window_closed(sub_root):
    """
    this function is used to reset all variables after finishing the Run operation 
    (process_btn_clicked) and also used in case of stop button is clicked
    """
    global run
    global stop
    process_btn['state']= 'normal'
    stop_btn['state']='disabled'
    next_step_btn.place_forget()
    var5.set(1)
    stop = 1
    try:
        sub_root.destroy()
    except:
        pass
    remove_all_btn_clicked()
    processed_images.clear()
    to_do_list.clear()
    processed_img_label.configure(image='')
    processed_img_label.image = ''
    current_process_label.place_forget()
    run += 1
def sub_root_closed(sub_root, process):
    """
    this function is used to set default constants if the user closed the sub_root window
    without setting any values.
    Inputs:
        sub_root: the small window (topLevel()) made in the add_process_constants function
        process: type of process processed 
    """
    
    if process == "Brightness Adjustment":
        process_constants.append(100)
    
    elif process == "Contrast Adjustment":
        process_constants.append(.5)
    
    elif process == "Translation":
        process_constants.append((10,10))
    
    elif process == "Scaling":
        process_constants.append((.5,.5))
        
    elif process == "Rotation":
        process_constants.append(30)
    
    elif process == "Salt" or  process =="Pepper":
        process_constants.append(.05)
        
    elif process == "Salt & Pepper":
        process_constants.append((.05, .5))
        
    elif process == "Gaussian":
        process_constants.append((0, .01))
        
    elif process == "Speckle":
        process_constants.append((0,.01))
        
    elif process == "Average":
        process_constants.append(3)
        
    elif process == "Gaussian_blur":
        process_constants.append((5,0))
        
    elif process == "Median":
        process_constants.append(3)
        
    elif process == "LoG":
        process_constants.append((5,0))
        
    elif process == "Canny":
        process_constants.append((100,200))
        
    elif process == "Hough Transform line detection":
        process_constants.append((200, 25))
    
    elif process == "Hough Transform circle detection":
        process_constants.append((5, 30)) 
        
    elif process == "Dilation" or process == "Erosion" or process == "Close" or process == "Open":
        process_constants.append((5, 1))
        
   
    
    else:    
        process_constants.append(0)
            
    sub_root.destroy()
        
def add_btn_clicked(listboxes):
    """
    this function is activated when the add button is clicked and is used to add
    the operation to the to_do_list and display it to the chosen operations list
    then call the add_process_constants function to make a small window to get 
    the process constants or parameters from the user.
    """
    listbox = None
    if not listboxes:
        return
    for box in listboxes:
        if len(box.curselection())>0:
            listbox = box
    if not listbox:
        return
    
    to_do_list.append(listbox.get(ANCHOR))
    operations_to_do.insert(len(to_do_list), to_do_list[-1])  
    add_process_constants(to_do_list[-1])
    
def remove_btn_clicked():
    """
    this function is activated when the user click on the remove button to remove 
    a certain operation from the chosen operations list.
    """
    if operations_to_do.curselection():
        to_do_list.pop(operations_to_do.curselection()[0])
        process_constants.pop(operations_to_do.curselection()[0])
        operations_to_do.delete(operations_to_do.curselection())
        
def remove_all_btn_clicked():
    """
    this function is activated when the user click on the remove all button to remove
    all chosen operations from the chosen operations list.
    """
    to_do_list.clear()
    process_constants.clear()
    operations_to_do.delete(0,'end')  
    

def process_btn_clicked():
    """
    this function is activated when the user click on the run button to start processing 
    the chosen operations on the image chosen in the image path. 
    """
    process_btn['state'] = "disabled"
    stop_btn['state'] = 'normal'
    global run
    global save_path
    global processed_images 
    global stop
    
    stop = 0
    processed_images= []
    run_where = var2.get()
    

    try:
        hist_imgs_list = []
        imgPath = img_path.get()
        if imgPath == '':
            imgPath = 'lena_std2.jpg'
        img =cv.imread(imgPath)
        processed_img_label.configure(image = '')
        processed_img_label.image =' '
        
        if var1.get() and len(img.shape) > 2:
            img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            
        processed_images.append(img)
        save_path = modified_img_path.get()
        if save_path == '':
            save_path= 'output images'
        if run_where:
            original_img_label_img = cvtoimage(img)
            original_img_label.config(image= original_img_label_img)
            original_img_label.image = original_img_label_img
            if to_do_list:
                next_step_btn.place(x=900, y=630)
        
        pointTransform = set(["Brightness Adjustment", "Contrast Adjustment", "Translation", "Scaling", "Rotation"])
        localTransform = set(["Average", "Bilateral",  "Median", "Gaussian_blur", "Sobel_x", "Sobel_y", "Sobel", "Prewitt_x", "Prewitt_y", "Prewitt", "Scharr", "Laplacian", "LoG", "Canny"])
        globalTransform = set(["Hough Transform line detection", "Hough Transform circle detection"])
        noises = set(["Salt", "Pepper", "Salt & Pepper", "Gaussian", "Poisson", "Speckle"])
        morphological = set(["Dilation", "Erosion", "Close", "Open", "Skeleton"])
        
       
        for process in range(len(to_do_list)):
            
            if  to_do_list == [] or var4.get() or stop:
                return
            
            if run_where:
                next_step_btn.wait_variable(var3)
                current_process_label.config(text=to_do_list[process])
                current_process_label.place(x=1050, y=390)
         
                
            if to_do_list[process] in pointTransform:
                processed_images.append(point_transform(processed_images[-1], process_constants[process], to_do_list[process]))
                if run_where:
                    processed_img_label_img = cvtoimage(processed_images[-1])
                    processed_img_label.config(image = processed_img_label_img)
                    processed_img_label.image = processed_img_label_img
                else:
                    run_in_another_window(processed_images[-1], to_do_list[process])
           
                
            elif to_do_list[process] == "Histogram":
                hist_imgs_list.append((process, get_hist_img(processed_images[-1])))
                if run_where:
                    processed_img_label_img = cvtoimage(hist_imgs_list[-1][1])
                    processed_img_label.config(image = processed_img_label_img)
                    processed_img_label.image = processed_img_label_img
                else:
                    run_in_another_window(hist_imgs_list[-1][1], to_do_list[process])

                
            elif to_do_list[process] == "Histogram Equalization":
                if len(processed_images[-1].shape) < 3:
                    processed_images.append(cv.equalizeHist(processed_images[-1]))
                else:
                    processed_images.append(equalize_BGR_hist(processed_images[-1]))
                    
                if run_where:
                    processed_img_label_img = cvtoimage(processed_images[-1])
                    processed_img_label.config(image = processed_img_label_img)
                    processed_img_label.image = processed_img_label_img
                else:
                    run_in_another_window(processed_images[-1], to_do_list[process])

                
            elif to_do_list[process] in noises:
                processed_images.append(add_noise(processed_images[-1], process_constants[process], to_do_list[process]))
                if run_where:
                    processed_img_label_img = cvtoimage(processed_images[-1])
                    processed_img_label.config(image = processed_img_label_img)
                    processed_img_label.image = processed_img_label_img
                else:
                    run_in_another_window(processed_images[-1], to_do_list[process])
             
            
            elif to_do_list[process] in localTransform:
                processed_images.append(local_transform(processed_images[-1], process_constants[process], to_do_list[process]))
                if run_where:
                    processed_img_label_img = cvtoimage(processed_images[-1])
                    processed_img_label.config(image = processed_img_label_img)
                    processed_img_label.image = processed_img_label_img
                else:
                    run_in_another_window(processed_images[-1], to_do_list[process])
                
                    
            elif to_do_list[process] in globalTransform:
                processed_images.append(global_transform(processed_images[-1], process_constants[process], to_do_list[process]))
                if run_where:
                    processed_img_label_img = cvtoimage(processed_images[-1])
                    processed_img_label.config(image = processed_img_label_img)
                    processed_img_label.image = processed_img_label_img 
                    
                else:
                    run_in_another_window(processed_images[-1], to_do_list[process])
                    
            elif to_do_list[process] == "To binary image":
                if len(processed_images[-1].shape) > 2:
                    gray_img = cv.cvtColor(processed_images[-1], cv.COLOR_BGR2GRAY)
                else:
                    gray_img = processed_images[-1]
                processed_images.append(cv.threshold(gray_img, 127, 255, cv.THRESH_BINARY)[1])
                
                if run_where:
                    processed_img_label_img = cvtoimage(processed_images[-1])
                    processed_img_label.config(image = processed_img_label_img)
                    processed_img_label.image = processed_img_label_img 
                    
                else:
                    run_in_another_window(processed_images[-1], to_do_list[process])
                    
            elif to_do_list[process] in morphological:
                processed_images.append(Morphological_operations(processed_images[-1], process_constants[process], to_do_list[process]))
                
                if run_where:
                    processed_img_label_img = cvtoimage(processed_images[-1])
                    processed_img_label.config(image = processed_img_label_img)
                    processed_img_label.image = processed_img_label_img 
                    
                else:
                    run_in_another_window(processed_images[-1], to_do_list[process])
            

       
        for i in hist_imgs_list:
            processed_images.insert(i[0]+1, i[1])
        
        if run_where:
            next_step_btn.wait_variable(var3)
            
        if  to_do_list == [] or var4.get() or stop:
            return
        try: 
            next_step_btn.place_forget()  
            current_process_label.place_forget()
            display_in_oneImage() 
            if not stop:
                save_window()
            else:
                return
        except:
            pass
        
    except AttributeError:
        process_btn['state'] = 'normal'
        messagebox.showerror("Error", "Image not found in the specified path.", parent = root)  
        stop_btn['state']='disabled'
        

def get_hist_img(img):
    """
    this function is resposible for creating a Histogram image suitable for using it in 
    the GUI
    """
    img2= img.copy()
    fig = plt.figure()
    if len(img2.shape) < 3:
        img2 = cv.cvtColor(img2, cv.COLOR_BGR2RGB)
        plt.hist(img2.ravel(),256,[0,256])
      
    else:
        color = ('b','g','r')
        for channel,col in enumerate(color):
            histr = cv.calcHist([img2],[channel],None,[256],[0,256])
            plt.plot(histr,color = col)
            plt.xlim([0,256])
            
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img2 = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    buf.close()
    img2 = cv.imdecode(img2, 1)
    img2 = cv.cvtColor(img2, cv.COLOR_BGR2RGB)
    ImageTk.PhotoImage(Image.fromarray(img2))
     
    return img2  

def equalize_BGR_hist(img):
    """
    this function is used to do the hisotgram equalization in case the image
    is RGB image, by converting it into YCrCb and equalizing the Cb componenet
    then converting it back to RGB image.
    """
    img2= img.copy()
    img2 = cv.cvtColor(img2,cv.COLOR_BGR2YCrCb)
    img2[:,:,0] = cv.equalizeHist(img2[:,:,0])
    img2 = cv.cvtColor(img2, cv.COLOR_YCrCb2BGR)
    return img2

def add_noise(img, constants, process):
    """
    this function is responsible for all of the adding noise operations
    """
    img2 = img.copy()
    if process == "Salt":
        img2 = random_noise(img2, mode='salt', amount = constants)
        img2 = np.array(255*img2, dtype = 'uint8')
        
    elif process == "Pepper":
        img2 = random_noise(img2, mode='pepper', amount = constants)
        img2 = np.array(255*img2, dtype = 'uint8')
    
    elif process == "Salt & Pepper":
        img2 = random_noise(img2, mode='s&p', amount = constants[0], salt_vs_pepper= constants[1])
        img2 = np.array(255*img2, dtype = 'uint8')
        
    elif process == "Gaussian":
        img2 = random_noise(img2, mode='gaussian', mean = constants[0], var= constants[1])
        img2 = np.array(255*img2, dtype = 'uint8')
    
    elif process == "Poisson":
        img2 = random_noise(img2, mode='poisson')
        img2 = np.array(255*img2, dtype = 'uint8')
        
    elif process == "Speckle":
        img2 = random_noise(img2, mode='gaussian', mean = constants[0], var= constants[1])
        img2 = np.array(255*img2, dtype = 'uint8')
        
    
    return img2

def point_transform(img, constants, process):
    """
    this function is responsible for all the point transform operations except for
    the histogram, and histogram equalization
    """
    img2 = img.copy()
    
    if process == "Brightness Adjustment":
        if constants >= 0:
            img2[img2 > 255-constants] = 255
            img2[img2 <= 255-constants] += constants
        else:
            img2[img2 < -1*constants]=0
            img2[img2 >= -1*constants] -= -1*constants
            
    elif process == "Contrast Adjustment":
        if constants > 1:
            img2[img2 > 255/constants] = 255
            np.multiply(img2[img2 <= 255/constants], constants, out=img2[img2 <= 255/constants], casting='unsafe')
        
        elif constants < 1:
            np.multiply(img2, constants, out=img2, casting='unsafe')
        
    elif process == "Translation":
        rows, cols= img2.shape[:2]
        Tm = np.float32([[1,0,constants[0]], [0,1, constants[1]]])
        img2 = cv.warpAffine(img2, Tm, (cols, rows))
            
    elif process == "Scaling":
        img2 = cv.resize(img2,None,fx=constants[0], fy=constants[1], interpolation = cv.INTER_CUBIC)

    elif process == "Rotation":
        row, col = img2.shape[:2]
        center = tuple(np.array([row, col])//2)
        rotate_by = cv.getRotationMatrix2D(center, constants, 1.0)
        img2 = cv.warpAffine(img2, rotate_by, (col, row))
    return img2
    

def local_transform(img, constants, process):
    """
    this function is responsible for all of the local transform operations
    """
    img2 = img.copy()
    if process == "Average":
        img2 = cv.blur(img2, (constants, constants))
    
    elif process == "Gaussian_blur":
        img2 = cv.GaussianBlur(img2, (constants[0], constants[0]), constants[1])
    
    elif process == "Bilateral":
        img2 = cv.bilateralFilter(img2, 15, 75, 75)
    
    elif process == "Median":
        img2 = cv.medianBlur(img2, constants)
    
    else:
        if len(img2.shape) > 2:
            img2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)
        
        if process == "Sobel_x":
            img2 = cv.Sobel(img2, cv.CV_64F, 1, 0, ksize = 3)
            img2 = cv.convertScaleAbs(img2)
          
        elif process == "Sobel_y":
            img2 = cv.Sobel(img2, cv.CV_64F, 0, 1, ksize = 3)
            img2 = cv.convertScaleAbs(img2)
            
        elif process == "Sobel":
            sobel_x = cv.Sobel(img2, cv.CV_64F, 1, 0, ksize = 3)
            sobel_x = cv.convertScaleAbs(sobel_x)
            
            sobel_y = cv.Sobel(img2, cv.CV_64F, 0, 1, ksize = 3)
            sobel_y = cv.convertScaleAbs(sobel_y)
            
            img2 =cv.addWeighted(sobel_x, 0.5, sobel_y, 0.5, 0)
    
        elif process == "Prewitt_x":
            x = np.array([[1,1,1],[0,0,0],[-1,-1,-1]])
            img2 = cv.filter2D(img2, -1, x)
       
        elif process == "Prewitt_y":
            y = np.array([[-1,0,1],[-1,0,1],[-1,0,1]])
            img2 = cv.filter2D(img2, -1, y)
        
        elif process == "Prewitt":
            x = np.array([[1,1,1],[0,0,0],[-1,-1,-1]])
            perwitt_x = cv.filter2D(img2, -1, x)
            
            y = np.array([[-1,0,1],[-1,0,1],[-1,0,1]])
            perwitt_y = cv.filter2D(img2, -1, y)
            
            img2 = cv.addWeighted(perwitt_x, .5, perwitt_y, .5, 0)
       
        elif process == "Scharr":
            scharr_x = cv.Scharr(img2, cv.CV_64F, 1, 0)
            scharr_x = cv.convertScaleAbs(scharr_x)
            
            scharr_y = cv.Scharr(img2, cv.CV_64F, 0, 1)
            scharr_y = cv.convertScaleAbs(scharr_y)
            

            img2 =cv.addWeighted(scharr_x, 0.5, scharr_y, 0.5, 0)
    
        elif process == "Laplacian":
            img2 = cv.Laplacian(img2, cv.CV_64F)
            img2 = cv.convertScaleAbs(img2)

        elif process == "LoG":
            img2 = cv.GaussianBlur(img2, (constants[0], constants[0]), constants[1])
            img2 = cv.Laplacian(img2, cv.CV_8U)
      
        elif process == "Canny":
            img2 = cv.Canny(img2, constants[0], constants[1])
            
       
    return img2

def global_transform (img, constants, process):
    """
    this function is responsible for all the global transform operations
    """
    img2 = img.copy()
    if len(img2.shape)>2:
        img2= cv.cvtColor(img2, cv.COLOR_BGR2GRAY)
        
    if process == "Hough Transform line detection":
        img2 = cv.Canny(img2, 50, 200)
        lines = cv.HoughLinesP(img2, 1, np.pi/180, 50, minLineLength=constants[0], maxLineGap=constants[1])
        img2 = img.copy()
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv.line(img2, (x1, y1), (x2, y2), (0,0,255), 3)
            
    elif process == "Hough Transform circle detection":
        img2 = img.copy()
        if len(img2.shape)>2:
            img2= cv.cvtColor(img2, cv.COLOR_BGR2GRAY)
            
        img2 = cv.medianBlur(img2, 5)
        
        circles = cv.HoughCircles(img2, cv.HOUGH_GRADIENT, 1, 20, param1=100, param2=30, minRadius=constants[0], maxRadius=constants[1])
    
        if circles is not None:
            circles = np.uint16(np.around(circles))
            img2 =img.copy()
            for i in circles[0, :]:
                # Draw outer circle
                cv.circle(img2, (i[0], i[1]), i[2], (0, 0, 255), 2)
                # Draw inner circle
                cv.circle(img2, (i[0], i[1]), 2, (0, 255, 255), 3)
        
    return img2

def Morphological_operations(img, constants, process):
    """
    this function is responsibel for all the morphological oeprations
    """
    img2 = img.copy()
    try:
        kernel = np.ones((constants[0], constants[0]), np.uint8)
    except:
        pass
    
    if process == "Dilation":
        img2 = cv.dilate(img2, kernel, iterations = constants[1])
        
    elif process == "Erosion":
        img2 = cv.erode(img2, kernel, iterations = constants[1])
        
    elif process == "Close":
        img2 =  cv.morphologyEx(img2, cv.MORPH_OPEN, kernel, iterations = constants[1])
        
    elif process == "Open":
        img2 = cv.morphologyEx(img2, cv.MORPH_CLOSE, kernel, iterations= constants[1])
        
    elif process == "Skeleton":
        if len(img2.shape) > 2:
            img2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)
        size = np.size(img2)
        skel = np.zeros(img2.shape,np.uint8)
         
        ret,img2 = cv.threshold(img2,127,255,0)
        element = cv.getStructuringElement(cv.MORPH_CROSS,(3,3))
        done = False
         
        while( not done):
            eroded = cv.erode(img2,element)
            temp = cv.dilate(eroded,element)
            temp = cv.subtract(img2,temp)
            skel = cv.bitwise_or(skel,temp)
            img2 = eroded.copy()
         
            zeros = size - cv.countNonZero(img2)
            if zeros==size:
                done = True
        img2 = skel
    return img2

def Exit(): 
    """
    this function is used to exit the whole program.
    """
    global stop
    var4.set(1)
    var3.set(var3.get())
    var5.set(var5.get())
    stop = 1
    root.quit()
    root.destroy()

def add_to_operations_listboxes(listbox, operations): 
    """
    this function is used to add the operations to all listboxes (operations menus)
    """
    for operation in range(len(operations)):
        listbox.insert(operation+1, operations[operation])
    
root = Tk()
root.title("Image Processing")
root.geometry("1360x700+0+0")
root.config(bg='#444444' )

title = Label(root, text= "Image Processing", font=("times new roman", 20, "bold"), fg='#2069e0', bg='#444444')
title.place(x=500, y=20)

choose_img = Label(root, text ="Image Path:", font=("times new roman", 15, "bold"), bg='#444444', fg="white")
choose_img.place(x=220, y=70)

img_path = Entry(root, text="Test", font=("times new roman", 12), width = 70)
img_path.place(x=340, y=74)

browse_btn = Button(root, text ="Browse", font = ("times new roman", 10, "bold"), bg ="#2069e0", fg='white', width = 13, height=1, bd=0, command= button1_clicked)
browse_btn.place(x=940, y=73)



choose_modified_img_location = Label(root, text ="Save as:", font=("times new roman", 15, "bold"), bg='#444444', fg="white")
choose_modified_img_location.place(x=220, y=120)

modified_img_path = Entry(root, font=("times new roman", 12), width = 70)
modified_img_path.place(x=340, y=124)

browse_btn2 = Button(root, text ="Browse", font = ("times new roman", 10, "bold"), bg ="#2069e0", fg='white', width = 13, height=1, bd=0, command= button2_clicked)
browse_btn2.place(x=940, y=123)

operations= Listbox(root, font=("times new roman", 10), width = 30, bg ="#2069e0", fg="white")
operations.place(x=50, y=210)
operations_label = Label(root, text="Point Transform op's", font=("times new roman", 15, "bold"), bg="#444444", fg="white")
operations_label.place(x=50, y=180)

add_operations_list = ["Brightness Adjustment", "Contrast Adjustment", "Histogram", "Histogram Equalization", "Translation", "Scaling", "Rotation"]
add_to_operations_listboxes(operations, add_operations_list)

operations2= Listbox(root, font=("times new roman", 10), width = 30, bg ="#2069e0", fg="white")
operations2.place(x=250, y=210)
operations2_label = Label(root, text="Add Noise op's", font=("times new roman", 15, "bold"), bg="#444444", fg="white")
operations2_label.place(x=280, y=180)


add_operations_list =["Salt", "Pepper", "Salt & Pepper", "Gaussian", "Poisson", "Speckle"]
add_to_operations_listboxes(operations2, add_operations_list)



operations3= Listbox(root, font=("times new roman", 10), width = 30, bg ="#2069e0", fg="white")
operations3.place(x=450, y=210)
operations3_label = Label(root, text="Local Transform op's", font=("times new roman", 15, "bold"), bg="#444444", fg="white")
operations3_label.place(x=450, y=180)


add_operations_list =["Average", "Bilateral",  "Median", "Gaussian_blur", "Sobel_x", "Sobel_y", "Sobel", "Prewitt_x", "Prewitt_y", "Prewitt", "Scharr", "Laplacian", "LoG", "Canny"]
add_to_operations_listboxes(operations3, add_operations_list)


operations4= Listbox(root, font=("times new roman", 10), width = 30, bg ="#2069e0", fg="white")
operations4.place(x=650, y=210)
operations4_label = Label(root, text="Global Transform op's", font=("times new roman", 15, "bold"), bg="#444444", fg="white")
operations4_label.place(x=645, y=180)


add_operations_list = ["Hough Transform line detection", "Hough Transform circle detection"]
add_to_operations_listboxes(operations4, add_operations_list)

operations5= Listbox(root, font=("times new roman", 10), width = 30, bg ="#2069e0", fg="white")
operations5.place(x=850, y=210)
operations5_label = Label(root, text="Morphological op's", font=("times new roman", 15, "bold"), bg="#444444", fg="white")
operations5_label.place(x=860, y=180)

add_operations_list = ["To binary image","Dilation", "Erosion", "Close", "Open", "Skeleton"]
add_to_operations_listboxes(operations5, add_operations_list)

operations_listboxes_list = [operations, operations2, operations3, operations4, operations5]

operations_to_do_label = Label(root, text="Selected Operations", font=("times new roman", 15, "bold"), bg="#444444", fg="white")
operations_to_do_label.place(x=50, y= 380)
operations_to_do = Listbox(root, font=("times new roman", 10), bg='#2069e0', fg="white", width=50)
operations_to_do.place(x=50, y=420)



add_btn = Button(root, text="Add", width=13, height=1, font=("times new roman", 10), fg="white", bg ="#3ba843", bd=0, command= lambda: add_btn_clicked(operations_listboxes_list))
add_btn.place(x=250, y=385)

remove_btn = Button(root, text="Remove", width=13, height=1, font=("times new roman", 10), fg="white", bg ="#ad0000", bd=0, command= remove_btn_clicked)
remove_btn.place(x=400, y=450)

remove_all_btn = Button(root, text="Remove All", width=13, height=1, font=("times new roman",10), fg="white", bg="#FF0000", bd=0, command= remove_all_btn_clicked)
remove_all_btn.place(x=400, y=510)

process_btn = Button(root, text="RUN", width=16, height=2, font=("times new roman",10), fg="white", bg="#00a200", bd=0, command= process_btn_clicked)
process_btn.place(x=900, y=450)

stop = 0
stop_btn = Button(root, text="STOP", width=16, height=2, font=("times new roman", 10), fg="white", bg="red", bd=0, state='disabled',command = lambda : save_window_closed(None))
stop_btn.place(x=900, y=510)

var1 = IntVar()
gray_img = Checkbutton(root, text="Process as gray image.", font=("times new roman", 10, "bold"), variable = var1, bg="#444444", fg="white", selectcolor="#2069e0")
gray_img.place(x=600, y =450)

var2 = IntVar()
where_to_run = Checkbutton(root, text="Run in the same window.", font=("times new roman", 10, "bold"), variable = var2, bg="#444444", fg="white", selectcolor="#2069e0")
where_to_run.place(x=600, y =500)

var3 = IntVar()
next_step_btn = Button(root, text="Next Step >", font=("times new roman", 10, "bold"),bg="#2069e0", fg="white", bd=0, command = lambda: var3.set(1))


original_img_label = Label(root, bg='#2069e0', width=250, height = 250, anchor = 'nw')
original_img_label.place(x=1050, y = 120)

current_process_label = Label(root, font=("times new roman",10),bg='#444444', fg='red')
#current_process_label.place(x=1050, y=390)

processed_img_label = Label(root,bg='#2069e0', width=250, height = 250)
processed_img_label.place(x=1050, y = 410)

var4 = IntVar()
var5 = IntVar()

logo_img = ImageTk.PhotoImage(file='FEE logo2.png')
logo = Label(root, image=logo_img, bg='#444444', bd=0)
logo.place(x=50, y=60)

author = Label(root, text="Designed and implemented by: Ahmed Mohamed El-Brawany.\nAll rights are reserved.", font=("times new roman", 12, "italic"), bg='#444444', fg="yellow", justify="left")
author.place(x=0, y=650)

root.protocol("WM_DELETE_WINDOW", Exit)

root.mainloop()

