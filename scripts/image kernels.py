""" This module forms an application that can load and save images and apply kernel filters to it"""

import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk


class Action:
    def __init__(self, kernel, name=""):
        self.kernel = kernel
        self.name = name


class Application:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Filter Application")
        self.window.geometry("900x800")
        self.window.resizable(False, False)

        self.window.config(menu=self.init_menu())
        self.actions = list()

        self.imageframe = tk.Frame(self.window)
        self.imageframe.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.undoframe = tk.Frame(self.window)
        self.undoframe.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # place a label containing the final image
        self.label_image = tk.Label(self.imageframe)
        self.label_image.pack(fill=tk.BOTH, expand=True)

        self.input = tk.Entry(self.imageframe, font=("Calibri 16"))
        self.input.pack(fill=tk.BOTH, expand=True)
        self.input.insert(0, "(1,1,1) (1,1,1) (1,1,1)")

        self.inputframe = tk.Frame(self.imageframe)
        self.inputframe.pack(fill=tk.BOTH, expand=True)

        # gui buttons
        self.submit_btn = tk.Button(self.inputframe, text="Submit",
                                    command=self.submit, padx=2, pady=2)
        self.submit_btn.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.reset_btn = tk.Button(self.inputframe, text="Reset",
                                   command=self.reset, padx=2, pady=2)
        self.reset_btn.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.undobox = tk.Listbox(self.undoframe, height=40, width=40)
        self.undobox.pack(fill=tk.BOTH, expand=True)

        self.undo_btn = tk.Button(self.undoframe, text="Undo",
                                  command=self.undo, padx=2, pady=2)
        self.undo_btn.pack(fill=tk.BOTH, expand=True)

        self.del_button = tk.Button(self.undoframe, text="Delete",
                                    command=self.del_action, padx=2, pady=2)
        self.del_button.pack(fill=tk.BOTH, expand=True)

        # load image
        self.main_img = self.load_image("lena.jpg")
        self.original = self.main_img.copy()

        self.tkpi = None
        self.display(self.main_img)

    # updates the image to display
    def display(self, cv_img):
        thumbnail = cv2.resize(cv_img, (700,700))
        image = Image.fromarray(thumbnail)
        self.tkpi = ImageTk.PhotoImage(image=image)
        self.label_image.configure(image=self.tkpi)

    def init_menu(self):
        menubar = tk.Menu(self.window)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open image", command=self.open_image)
        filemenu.add_command(label="Save image", command=self.save_image)
        menubar.add_cascade(label="File", menu=filemenu)

        # add pre defined edge detection filters
        # Source: https://en.wikipedia.org/wiki/Kernel_(image_processing)
        filtermenu = tk.Menu(menubar, tearoff=0)
        def edge_detect_1(): return self.do_filter("(1, 0, -1) (0, 0, 0) (-1, 0, 1)")
        filtermenu.add_command(label="Edge Detection 1", command=edge_detect_1)
        def edge_detect_2(): return self.do_filter("(0, 1, 0) (1, -4, 1) (0, 1, 0)")
        filtermenu.add_command(label="Edge Detection 2", command=edge_detect_2)
        def edge_detect_3(): return self.do_filter("(-1, -1, -1) (-1, 8, -1) (-1, -1, -1)")
        filtermenu.add_command(label="Edge Detection 3", command=edge_detect_3)
        filtermenu.add_separator()
        def sharpen(): return self.do_filter("(0, -1, 0) (-1, 5, -1) (0, -1, 0)")
        filtermenu.add_command(label="Sharpen", command=sharpen)
        filtermenu.add_separator()
        def box_blur(): return self.do_filter("(1, 1, 1) (1, 1, 1) (1, 1, 1)")
        filtermenu.add_command(label="Box blur", command=box_blur)
        def gaussian_blur_1(): return self.do_filter("(1, 2, 1) (2, 4, 2) (1, 2, 1)")
        filtermenu.add_command(label="Gaussian blur 1", command=gaussian_blur_1)
        def gaussian_blur_2(): return self.do_filter("(1,4,6,4,1) (4, 16, 24, 16, 4) (6, 24, 36, 24, 6) (4, 16, 24, 16, 4) (1, 4, 6, 4, 1)")
        filtermenu.add_command(label="Gaussian blur 2", command=gaussian_blur_2)
        filtermenu.add_separator()
        def unsharp_mask(): return self.do_filter("(1, 4, 6, 4, 1) (4, 16, 24, 16, 4) (6, 24, -476, 24, 6) (4, 16, 24, 16, 4) (1, 4, 6, 4, 1)")
        filtermenu.add_command(label="Unsharp mask", command=unsharp_mask)
        menubar.add_cascade(label="Filter", menu=filtermenu)
        # return the constructed menu bar
        return menubar

    def do_filter(self, kernel_string):
        self.input.delete(0, tk.END)
        self.input.insert(0, kernel_string)
        self.submit()

    def save_image(self):
        path = tk.filedialog.asksaveasfilename(defaultextension=".png")
        if not path:
            return
        b, g, r = cv2.split(self.main_img)
        output = cv2.merge((r, g, b))
        cv2.imwrite(path, output)

    def load_image(self, path):
        image = cv2.imread(path)
        b, g, r = cv2.split(image)
        image = cv2.merge((r, g, b))
        return image

    def open_image(self):
        path = tk.filedialog.askopenfile().name
        if not path:
            return
        self.main_img = self.load_image(path)
        self.original = self.main_img
        self.display(self.main_img)

    def run(self):
        self.window.mainloop()

    def reset(self):
        self.main_img = self.original.copy()
        self.display(self.main_img)
        self.undobox.delete(0, tk.END)
        self.actions.clear()

    def submit(self):
        # read the kernel string
        text = self.input.get()
        # convert it to an array
        try:
            kernel = self.string_to_kernel(text)
        except:
            tk.messagebox.showwarning("Warning", "Unable to parse kernel.")
            return
        # filter the image using the kernel
        self.main_img = cv2.filter2D(self.main_img, -1, kernel)
        # display the result
        self.display(self.main_img)
        # add it to the action recordings for undo
        self.actions.append(Action(kernel, text))
        self.undobox.insert(tk.END, text)

    def string_to_kernel(self, text):
        kernel = text.replace(" ", "").split(")(")
        # removes the starting '(' and ending ')'
        kernel[0], kernel[-1] = kernel[0][1:], kernel[-1][:-1]
        # converts the row strings to integer lists
        kernel = [[float(number) for number in row.split(',')] for row in kernel]
        # create the kernel as numpy array and divide it by the kernel's sum
        # the if statement is so we don't accidentally divide by 0
        if sum(map(sum, kernel)):
            kernel = np.array(kernel, np.float32) / sum(map(sum, kernel))
        else:
            kernel = np.array(kernel, np.float32)
        return kernel

    def executeActions(self):
        self.main_img = self.original.copy()
        for action in self.actions:
            self.main_img = cv2.filter2D(self.main_img, -1, action.kernel)
        self.display(self.main_img)

    def undo(self):
        if not self.actions:
            return

        self.input.delete(0, tk.END)
        self.input.insert(0, self.actions[-1].name)

        self.actions.pop()
        self.undobox.delete(tk.END, tk.END)

        self.main_img = self.original.copy()
        self.executeActions()

    def del_action(self):
        if not self.undobox.curselection():
            return
        index = int(self.undobox.curselection()[0])
        self.input.delete(0, tk.END)
        self.input.insert(0, self.actions[index].name)
        self.actions.pop(index)
        self.undobox.delete(index)
        self.executeActions()


def main():
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
