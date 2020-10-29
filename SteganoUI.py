# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.



from PIL import Image, ImageDraw, ImageFont
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import QFileDialog, QPixmap, QMessageBox, QDialog
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import io
import random
import string
import textwrap
from Crypto.Cipher import AES

class AESStego:
    
# Convert encoding data into 8-bit binary
# form using ASCII value of characters
    def genData(self,data):
    
            # list of binary codes
            # of given data
            newd = []
            for i in data:
                newd.append(format(ord(b'%c' % i ), '08b'))
            return newd
    
    # Pixels are modified according to the
    # 8-bit binary data and finally returned
    def modPix(self,pix, data):
    
        datalist = self.genData(data)
        lendata = len(datalist)
        imdata = iter(pix)
    
        for i in range(lendata):
    
            # Extracting 3 pixels at a time
            pix = [value for value in imdata.__next__()[:3] +
                                    imdata.__next__()[:3] +
                                    imdata.__next__()[:3]]
    
            # Pixel value should be made
            # odd for 1 and even for 0
            for j in range(0, 8):
                if (datalist[i][j] == '0' and pix[j]% 2 != 0):
                    pix[j] -= 1
    
                elif (datalist[i][j] == '1' and pix[j] % 2 == 0):
                    if(pix[j] != 0):
                        pix[j] -= 1
                    else:
                        pix[j] += 1
                    # pix[j] -= 1
    
            # Eighth pixel of every set tells
            # whether to stop ot read further.
            # 0 means keep reading; 1 means thec
            # message is over.
            if (i == lendata - 1):
                if (pix[-1] % 2 == 0):
                    if(pix[-1] != 0):
                        pix[-1] -= 1
                    else:
                        pix[-1] += 1
    
            else:
                if (pix[-1] % 2 != 0):
                    pix[-1] -= 1
    
            pix = tuple(pix)
            yield pix[0:3]
            yield pix[3:6]
            yield pix[6:9]
    
    def encode_enc(self,newimg, data):
        w = newimg.size[0]
        (x, y) = (0, 0)
    
        for pixel in self.modPix(newimg.getdata(), data):
    
            # Putting modified pixels in the new image
            newimg.putpixel((x, y), pixel)
            if (x == w - 1):
                x = 0
                y += 1
            else:
                x += 1
    
    # Encode data into image
    def encode(self,data,datakey,path):
        image = Image.open(path, 'r')
        obj = AES.new(datakey.encode("utf8"), AES.MODE_CFB, 'This is an IV456'.encode("utf8"))
        data = obj.encrypt(data.encode("utf8"))
        if (len(data) == 0):
            raise ValueError('Data is empty')
    
        newimg = image.copy()
        self.encode_enc(newimg, data)
    
        newimg.save("images/aes.png", str("images/aes.png".split(".")[1].upper()))
        return data
    
    # Decode the data in the image
    def decode(self,key,path):
        
        image = Image.open(path, 'r')
    
        data = b'';
        imgdata = iter(image.getdata())
    
        while (True):
            pixels = [value for value in imgdata.__next__()[:3] +
                                    imgdata.__next__()[:3] +
                                    imgdata.__next__()[:3]]
    
            # string of binary data
            binstr = ''
    
            for i in pixels[:8]:
                if (i % 2 == 0):
                    binstr += '0'
                else:
                    binstr += '1'
            
            data = b"".join([data, int(binstr, 2).to_bytes(1, byteorder='big')])
            if (pixels[-1] % 2 != 0):
                
                obj2 = AES.new(key.encode("utf8"), AES.MODE_CFB, 'This is an IV456'.encode("utf8"))
                plaintext = obj2.decrypt(data)
                return plaintext.decode("utf-8")


class Stego:
    original_image = {}
    original_image_width = 0
    original_image_height = 0
    encoded_message_image = {}
    stego_image = {}
    length = 0
    password_characters = ''

    def get_random_string(self,length):
        self.password_characters = string.ascii_letters + string.digits + string.punctuation
        self.key = ''.join(random.choice(self.password_characters) for i in range(length))
        return self.key;
   
    def getOriginalImage(self,path): 
        self.original_image = Image.open(path,'r')
        self.original_image_width = self.original_image.width
        self.original_image_height = self.original_image.height


    def getMsgFromUser(self):
        secret_message = input("Enter secret message \n")
        self.generate_encoded_image_from_text(secret_message)
        
        
        

    def generate_encoded_image_from_text(self,text):
        image_text = Image.new('RGB',(self.original_image_width,self.original_image_height),color=(255,255,255))
        drawer = ImageDraw.Draw(image_text)
        font = ImageFont.truetype("mono.ttf",24)
        margin = offset = 20
        for line in textwrap.wrap(text, width=200):
            drawer.text((margin,offset), line,font=font, align="center",spacing=15,fill=(0,0,0))
            offset += 20
        
        image_text.save('images/hidden.png')
        return image_text

    def hide(self):
        self.stego_image = Image.new('RGB',(self.original_image_width,self.original_image_height))
        for x in range(self.original_image_width):
            for y in range(self.original_image_height):
                coord = x,y
                red = self.original_image.getpixel(coord)[0]
                green = self.original_image.getpixel(coord)[1]
                blue = self.original_image.getpixel(coord)[2]
                
                if self.encoded_message_image.getpixel(coord)[0] == 0:
                    if red == 0:
                        red = red + 1
                        self.stego_image.putpixel(coord,(red,green,blue))
                    else:
                        red = red - 1
                        self.stego_image.putpixel(coord,(red,green,blue))
                else:
                    self.stego_image.putpixel(coord,(red,green,blue))

        self.stego_image.save('images/o1.png')

    
    def unhide(self,originalPath, stegoPath):
       
        
        output_image = Image.open(stegoPath,'r')
        original_image = Image.open(originalPath,'r')
        decoded_msg_image = Image.new('RGB',(original_image.width,original_image.height))
        for x in range(self.original_image_width):
            for y in range(self.original_image_height):
                coord = x,y
                red = output_image.getpixel(coord)[0]
                if red - self.original_image.getpixel(coord)[0] == 1 or self.original_image.getpixel(coord)[0] - red == 1:
                    decoded_msg_image.putpixel(coord,(0,0,0))
                else:
                    decoded_msg_image.putpixel(coord,(255,255,255))

        decoded_msg_image.save('images/message.png')
        
    def image_to_byte_array(self,image:Image):
      imgByteArr = io.BytesIO()
      image.save(imgByteArr, format=image.format)
      imgByteArr = imgByteArr.getvalue()
      return imgByteArr

    
        
   

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
            MainWindow.setObjectName("MainWindow")
            MainWindow.resize(1519, 858)
            self.centralwidget = QtWidgets.QWidget(MainWindow)
            self.centralwidget.setObjectName("centralwidget")
            self.frame = QtWidgets.QFrame(self.centralwidget)
            self.frame.setGeometry(QtCore.QRect(30, 30, 1021, 251))
            self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
            self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
            self.frame.setObjectName("frame")
            self.keyTextBox = QtWidgets.QLineEdit(self.frame)
            self.keyTextBox.setGeometry(QtCore.QRect(140, 150, 221, 31))
            self.keyTextBox.setObjectName("keyTextBox")
            self.keyTextBox.setMaxLength(16)
            self.key = QtWidgets.QLabel(self.frame)
            self.key.setGeometry(QtCore.QRect(10, 140, 101, 31))
            self.key.setObjectName("key")
            self.plainText = QtWidgets.QLabel(self.frame)
            self.plainText.setGeometry(QtCore.QRect(20, 40, 101, 31))
            self.plainText.setObjectName("plainText")
            self.generateKey = QtWidgets.QPushButton(self.frame)
            self.generateKey.setGeometry(QtCore.QRect(390, 150, 141, 31))
            self.generateKey.setObjectName("generateKey")
            self.plainTextEdit = QtWidgets.QPlainTextEdit(self.frame)
            self.plainTextEdit.setGeometry(QtCore.QRect(140, 10, 221, 121))
            self.plainTextEdit.setObjectName("plainTextEdit")
            self.pushButton_2 = QtWidgets.QPushButton(self.frame)
            self.pushButton_2.setGeometry(QtCore.QRect(390, 40, 181, 34))
            self.pushButton_2.setObjectName("pushButton_2")
            self.cipherText = QtWidgets.QLabel(self.frame)
            self.cipherText.setGeometry(QtCore.QRect(620, 40, 101, 31))
            self.cipherText.setObjectName("cipherText")
            self.decrypt = QtWidgets.QPushButton(self.centralwidget)
            self.decrypt.setGeometry(QtCore.QRect(1020, 300, 111, 51))
            icon1 = QtGui.QIcon()
            icon1.addPixmap(QtGui.QPixmap("images/decrypt.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.decrypt.setIcon(icon1)
            self.decrypt.setObjectName("decrypt")
            self.radioButton_2 = QtWidgets.QRadioButton(self.frame)
            self.radioButton_2.setGeometry(QtCore.QRect(390, 210, 119, 23))
            self.radioButton_2.setObjectName("radioButton_2")
            self.radioButton = QtWidgets.QRadioButton(self.frame)
            self.radioButton.setGeometry(QtCore.QRect(220, 210, 119, 23))
            self.radioButton.setObjectName("radioButton")
            self.radioButton.setChecked(True)
            self.encrypt = QtWidgets.QPushButton(self.centralwidget)
            self.encrypt.setGeometry(QtCore.QRect(860, 300, 111, 51))
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("images/encrypt.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.encrypt.setIcon(icon)
            self.encrypt.setObjectName("encrypt")
            self.plainTextEdit_2 = QtWidgets.QPlainTextEdit(self.frame)
            self.plainTextEdit_2.setGeometry(QtCore.QRect(720, 10, 271, 141))
            self.plainTextEdit_2.setObjectName("plainTextEdit_2")
            self.plainTextEdit_2.setReadOnly(True)
            self.key_2 = QtWidgets.QLabel(self.frame)
            self.key_2.setGeometry(QtCore.QRect(10, 200, 131, 31))
            self.key_2.setObjectName("key_2")

            self.progressBar = QtWidgets.QProgressBar(self.frame)
            self.progressBar.setGeometry(QtCore.QRect(630, 170, 331, 34))
            self.progressBar.setObjectName("progressBar")
            self.progressBar.setAlignment(Qt.AlignCenter)

            self.inputImage = QtWidgets.QLabel(self.centralwidget)
            self.inputImage.setGeometry(QtCore.QRect(50, 400, 1431, 391))
            self.inputImage.setText("")
            self.inputImage.setObjectName("inputImage")
            self.widget = QtWidgets.QWidget(self.centralwidget)
            self.widget.setGeometry(QtCore.QRect(30, 260, 811, 131))
            self.widget.setObjectName("widget")
            self.imagepath_2 = QtWidgets.QLineEdit(self.widget)
            self.imagepath_2.setGeometry(QtCore.QRect(20, 20, 441, 31))
            self.imagepath_2.setObjectName("imagepath_2")
            self.imagepath_2.setReadOnly(True)
            self.pushButton = QtWidgets.QPushButton(self.widget)
            self.pushButton.setGeometry(QtCore.QRect(500, 20, 271, 34))
            self.pushButton.setObjectName("pushButton")
            self.pushButton_3 = QtWidgets.QPushButton(self.widget)
            self.pushButton_3.setGeometry(QtCore.QRect(500, 70, 271, 34))
            self.pushButton_3.setObjectName("pushButton_3")
            self.imagepath_3 = QtWidgets.QLineEdit(self.widget)
            self.imagepath_3.setGeometry(QtCore.QRect(20, 70, 441, 31))
            self.imagepath_3.setText("")
            self.imagepath_3.setObjectName("imagepath_3")
            self.imagepath_3.setReadOnly(True)
            self.plainImageSize = QtWidgets.QLabel(self.centralwidget)
            self.plainImageSize.setGeometry(QtCore.QRect(1290, 90, 131, 31))
            self.plainImageSize.setText("")
            self.plainImageSize.setObjectName("plainImageSize")
            self.StegoImageSize = QtWidgets.QLabel(self.centralwidget)
            self.StegoImageSize.setGeometry(QtCore.QRect(1290, 130, 151, 31))
            self.StegoImageSize.setText("")
            self.StegoImageSize.setObjectName("StegoImageSize")
            self.plainText_4 = QtWidgets.QLabel(self.centralwidget)
            self.plainText_4.setGeometry(QtCore.QRect(1290, 170, 141, 31))
            self.plainText_4.setText("")
            self.plainText_4.setObjectName("plainText_4")
            self.plainImageSize_2 = QtWidgets.QLabel(self.centralwidget)
            self.plainImageSize_2.setGeometry(QtCore.QRect(1100, 90, 191, 31))
            self.plainImageSize_2.setObjectName("plainImageSize_2")
            self.StegoImageSize_2 = QtWidgets.QLabel(self.centralwidget)
            self.StegoImageSize_2.setGeometry(QtCore.QRect(1100, 130, 191, 31))
            self.StegoImageSize_2.setObjectName("StegoImageSize_2")
            self.secretMessageSize = QtWidgets.QLabel(self.centralwidget)
            self.secretMessageSize.setGeometry(QtCore.QRect(1100, 170, 181, 31))
            self.secretMessageSize.setObjectName("secretMessageSize")

            MainWindow.setCentralWidget(self.centralwidget)
            self.menubar = QtWidgets.QMenuBar(MainWindow)
            self.menubar.setGeometry(QtCore.QRect(0, 0, 1519, 31))
            self.menubar.setObjectName("menubar")
            MainWindow.setMenuBar(self.menubar)
            self.statusbar = QtWidgets.QStatusBar(MainWindow)
            self.statusbar.setObjectName("statusbar")
            MainWindow.setStatusBar(self.statusbar)


            self.encrypt.clicked.connect(self.encrypt_InputImage)
            self.decrypt.clicked.connect(self.show_OutputImage)
            self.pushButton.clicked.connect(self.originalImagePath)
            self.pushButton_3.clicked.connect(self.stegoImagePath)
            self.generateKey.clicked.connect(self.get_key)
            self.pushButton_2.clicked.connect(self.browse_plainText)

            self.encrypt.setStyleSheet("background-color : lightblue")
            self.decrypt.setStyleSheet("background-color : lightblue")
            self.pushButton.setStyleSheet("background-color : lightblue")
            self.pushButton_3.setStyleSheet("background-color : lightblue")
            self.generateKey.setStyleSheet("background-color : lightblue")
            self.pushButton_2.setStyleSheet("background-color : lightblue")

            self.radioButton_2.clicked.connect(self.enable_disableButton)
            self.radioButton.clicked.connect(self.enable_disableButton)

            self.retranslateUi(MainWindow)
            QtCore.QMetaObject.connectSlotsByName(MainWindow)
    def retranslateUi(self, MainWindow):
            _translate = QtCore.QCoreApplication.translate
            MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
            self.encrypt.setText(_translate("MainWindow", "Encrypt"))
            self.key.setText(_translate("MainWindow", "Key"))
            self.plainText.setText(_translate("MainWindow", "Plain Text"))
            self.generateKey.setText(_translate("MainWindow", "Generate Key"))

            self.cipherText.setText(_translate("MainWindow", "Cipher Text"))
            self.pushButton_2.setText(_translate("MainWindow", "Browse Secret Message"))
            self.decrypt.setText(_translate("MainWindow", "Decrypt"))
            self.key_2.setText(_translate("MainWindow", "Select the Method"))

            self.pushButton.setText(_translate("MainWindow", "Browse OriginalImage"))
            self.pushButton_3.setText(_translate("MainWindow", "Browse StegoImage"))
            self.radioButton.setText(_translate("MainWindow", "AES + LSB"))
            self.radioButton_2.setText(_translate("MainWindow", "New Algo"))
            self.plainImageSize_2.setText(_translate("MainWindow", "Original Image Size : "))
            self.StegoImageSize_2.setText(_translate("MainWindow", "Stego Image Size : " ))
            self.secretMessageSize.setText(_translate("MainWindow", "Secret Image Size : "))

    def encrypt_InputImage(self):
        self.progressBar.setFormat("Loading...")
        self.step = 0
        self.progressBar.setValue(self.step)
        if self.radioButton_2.isChecked():
            if(self.plainTextEdit.toPlainText()==""):
                QMessageBox.about(None, "Title", "Enter Plain Text")
                return
            elif(self.imagepath_2.text()==""):
                QMessageBox.about(None, "Title", "Choose Input Image")
                return

            self.progressBar.setValue(self.step+15)
            s1.encoded_message_image = s1.generate_encoded_image_from_text(self.plainTextEdit.toPlainText())
            self.progressBar.setValue(self.step+30)
            s1.hide()
            self.progressBar.setValue(self.step+55)
            self.inputImage.setPixmap(QtGui.QPixmap('images/o1.png'))
            self.inputImage.adjustSize()
            img = Image.open('images/o1.png')
            width, height = img.size
            self.progressBar.setValue(self.step+75)
            self.StegoImageSize.setText(str(width * height)+" pixels")
            self.StegoImageSize.setStyleSheet("background-color: lightgreen")
            self.progressBar.setValue(self.step+100)

        if self.radioButton.isChecked():
            if(self.plainTextEdit.toPlainText()==""):
                QMessageBox.about(None, "Title", "Enter Plain Text")
                return
            elif(self.imagepath_2.text()==""):
                QMessageBox.about(None, "Title", "Choose Input Image")
                return
            elif(self.keyTextBox.text()==""):
                QMessageBox.about(None, "Title", "Enter the Key")
                return
            self.progressBar.setValue(self.step+5)
            data = s2.encode(self.plainTextEdit.toPlainText(),self.keyTextBox.text(),self.imagepath_2.text())
            self.progressBar.setValue(self.step+20)
            img = Image.open('images/aes.png')
            width, height = img.size
            self.progressBar.setValue(self.step+35)
            self.StegoImageSize.setText(str(width * height)+" pixels")
            self.progressBar.setValue(self.step+50)
            self.StegoImageSize.setStyleSheet("background-color: lightgreen")
            self.plainTextEdit.setPlainText("")
            self.progressBar.setValue(self.step+75)
            self.plainTextEdit_2.setPlainText(str(data))
            self.progressBar.setValue(self.step+100)
        self.progressBar.setFormat("Encrypted")
        QMessageBox.about(None, "Info", "Encryption is successful")
        
    def show_OutputImage(self):
        self.progressBar.setFormat("Loading...")
        self.step = 0
        if self.radioButton_2.isChecked(): 
            if(self.imagepath_2.text()==""):
                QMessageBox.about(None, "Title", "Choose Original Image")
                return
            elif(self.imagepath_3.text()==""):
                QMessageBox.about(None, "Title", "Choose Stego Image")
                return
            self.progressBar.setValue(self.step+20)
            s1.unhide(self.imagepath_2.text(),self.imagepath_3.text())
            self.progressBar.setValue(self.step+50)
            self.inputImage.setPixmap(QtGui.QPixmap('images/message.png'))
            self.progressBar.setValue(self.step+60)
            self.inputImage.adjustSize()
            img = Image.open('images/message.png')
            width, height = img.size
            self.progressBar.setValue(self.step+75)
            self.plainText_4.setText(str(width * height)+" pixels")
            self.plainText_4.setStyleSheet("background-color: lightgreen")
            self.progressBar.setValue(self.step+100)
        if self.radioButton.isChecked():
            if(self.keyTextBox.text()==""):
                QMessageBox.about(None, "Title", "Enter the Key")
                return
            elif(self.imagepath_3.text()==""):
                QMessageBox.about(None, "Title", "Choose Stego Image")
                return
            self.progressBar.setValue(self.step+20)
            #self.pushButton_3.setEnabled(False)
            data = s2.decode(self.keyTextBox.text(),self.imagepath_3.text())
            self.progressBar.setValue(self.step+50)
            self.plainTextEdit.setPlainText(data)
            self.inputImage.setText(data)
            self.progressBar.setValue(self.step+75)
            self.inputImage.setWordWrap(True)
            self.inputImage.adjustSize()
            self.progressBar.setValue(self.step+100)
        self.progressBar.setFormat("Decrypted")
        QMessageBox.about(None, "Info", "Decryption is successful")
        
    def getImage(self):
        fname = QFileDialog.getOpenFileName(None, 'Open file','c:\\', "Image files (*.jpg *.png)")
        if fname != ('', ''):
            return fname[0]
        
    def originalImagePath(self):
        imagepath = self.getImage()
        if imagepath != None:
            s1.getOriginalImage(imagepath)
            self.imagepath_2.setText(imagepath);
            self.inputImage.setPixmap(QtGui.QPixmap(imagepath))
            self.inputImage.adjustSize()
            img = Image.open(imagepath)
            width, height = img.size
            self.plainImageSize.setText(str(width * height)+" pixels")
            self.plainImageSize.setStyleSheet("background-color: lightgreen")
    
    def stegoImagePath(self):
        imagepath = self.getImage()
        if imagepath != None:
            self.imagepath_3.setText(imagepath);
            img = Image.open(imagepath)
            width, height = img.size
            self.StegoImageSize.setText(str(width * height)+" pixels")
            self.StegoImageSize.setStyleSheet("background-color: lightgreen")
    
    def browse_plainText(self):
        fname = QFileDialog.getOpenFileName(None, 'Open file','c:\\', "Image files (*.txt)")
        if fname != ('', ''):
            file1 = open(fname[0],"r")
            plainText = file1.read()
            self.plainTextEdit.setPlainText(plainText)
        
    def get_key(self):
        if self.radioButton.isChecked():
            key = s1.get_random_string(16)
            self.keyTextBox.setText(key)
        
    def enable_disableButton(self):
        if self.radioButton_2.isChecked(): 
            self.keyTextBox.setText("")
            self.plainTextEdit.setPlainText("")
            self.plainTextEdit_2.setPlainText("")
            self.plainImageSize.setText("")
            self.StegoImageSize.setText("")
            self.plainText_4.setText("")
            self.imagepath_2.setText("")
            self.imagepath_3.setText("")
            self.plainImageSize.setStyleSheet("")
            self.StegoImageSize.setStyleSheet("")
            self.plainText_4.setStyleSheet("")
            self.generateKey.setEnabled(False)
            self.keyTextBox.setEnabled(False)
        if self.radioButton.isChecked():
            self.keyTextBox.setText("")
            self.plainTextEdit.setPlainText("")
            self.plainTextEdit_2.setPlainText("")
            self.plainImageSize.setText("")
            self.StegoImageSize.setText("")
            self.imagepath_2.setText("")
            self.imagepath_3.setText("")
            self.plainText_4.setText("")
            self.plainImageSize.setStyleSheet("")
            self.StegoImageSize.setStyleSheet("")
            self.plainText_4.setStyleSheet("")
            self.generateKey.setEnabled(True)
            self.keyTextBox.setEnabled(True)

          
  
          
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    s1 = Stego()
    s2 = AESStego()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
