from PyQt5 import QtWidgets, uic, QtGui, QtCore
import cv2
import sys,os,time
# settings
models_data = {'EDSR': [{'x2': 'EDSR_x2.pb'},{'x3': 'EDSR_x3.pb'},{'x4': 'EDSR_x4.pb'}],
'ESPCN' : [{'x2': 'ESPCN_x2.pb'},{'x3': 'ESPCN_x3.pb'},{'x4': 'ESPCN_x4.pb'}],
'FSRCNN' : [{'x2': 'FSRCNN_x2.pb'},{'x3': 'FSRCNN_x3.pb'},{'x4': 'FSRCNN_x4.pb'}],
'FSRCNN-small' : [{'x2': 'FSRCNN-small_x2.pb'},{'x3': 'FSRCNN-small_x3.pb'},{'x4': 'FSRCNN-small_x4.pb'}],
'LapSRN' : [{'x2': 'LapSRN_x2.pb'},{'x3': 'LapSRN_x3.pb'},{'x4': 'LapSRN_x4.pb'},{'x8': 'LapSRN_x8.pb'}]}

        

        




class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.setFixedSize(640, 480)
        #load resources file

        self.show()
        

        self.progressBars = []
        self.files = []
        # add elements to comboBox from models_data keys
        for key in models_data.keys():
            self.comboBox.addItem(key)
    #when select comboBox item fill comboBox_2
    def on_comboBox_currentIndexChanged(self):
        self.comboBox_2.clear()
        for item in models_data[self.comboBox.currentText()]:
            self.comboBox_2.addItem(list(item.keys())[0])
    # on actionOpen trigger open file dialog and add file names to tableWidget only images
    #tableWidget file names,image thumbnails,progress bar
    @QtCore.pyqtSlot()
    def on_actionOpenFile_triggered(self):
        #open images only  open file dialog and get multiple file names
        #multiple files
        
        fileNames = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open file', '', "Image files (*.jpg *.gif *.png *.jpeg)")[0]

        
        



        
        #add file names to tableWidget
        #clear tableWidget
        self.tableWidget.setRowCount(0)
        #set tableWidget column count and column headers
        self.tableWidget.setColumnCount(3)
        #adjust column width

        self.tableWidget.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        self.tableWidget.setHorizontalHeaderLabels(['File Name','Image path','Progress'])
        #add file names to tableWidget
        for i in range(len(fileNames)):
            self.files.append(fileNames[i])
        for i in range(len(self.files)):

            self.tableWidget.insertRow(i)
            self.tableWidget.setItem(i,0,QtWidgets.QTableWidgetItem(os.path.basename(self.files[i])))
            #image path
            self.tableWidget.setItem(i,1,QtWidgets.QTableWidgetItem(self.files[i]))


            #add progress bar to tableWidget
            self.progressBars.append(QtWidgets.QProgressBar())
            self.progressBars[-1].setValue(0)
            self.tableWidget.setCellWidget(i,2,self.progressBars[-1])


    #when select tableWidget item show image in label
    def on_tableWidget_itemSelectionChanged(self):
        #get selected row
        row = self.tableWidget.currentRow()
        #get image path
        image_path = self.tableWidget.item(row,1).text()
        #set image to label
        self.label.setPixmap(QtGui.QPixmap(image_path))
        self.label.setScaledContents(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
    #on actionRun clicked run function
    @QtCore.pyqtSlot()
    def on_actionRun_triggered(self):
        #if no row selected display message
        if self.tableWidget.currentRow() == -1:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Select image')
            return
        #get selected model
        model = self.comboBox.currentText()
        #get selected scale
        scale = self.comboBox_2.currentText()
        #get selected file
        row = self.tableWidget.currentRow()
        #get image path
        image_path = self.tableWidget.item(row,1).text()
        #get progress bar
        progress = row
        #get save directory path dialog
        save_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Directory', '', QtWidgets.QFileDialog.DontUseNativeDialog)
        #wait for dialog to close

        
        


        #run function       

        self.up_scale(model,scale,image_path,progress,save_path)
        #display message when done processing for selected image
        QtWidgets.QMessageBox.information(self, 'Done', 'Done processing for image '+str(os.path.basename(image_path)))

    #up_scale function
    def up_scale(self,model,scale,image_path,progress,save_path):
        if model == 'Model':
            #display message saying select model
            QtWidgets.QMessageBox.warning(self, 'Error', 'Select model')
            return
        #self.progressBars[progress].setValue(0)
        #set progress bar to processing
        self.progressBars[progress].setFormat('Processing')
        #run model
        image = cv2.imread(image_path)
        sr = cv2.dnn_superres.DnnSuperResImpl_create()
        path = 'models/'+model+'_'+scale+'.pb'
        sr.readModel(path)
        if model.endswith('small'):
            fn =model.split('-')[0].lower()
        else:
            fn = model.lower()
        sr.setModel(fn , int(scale[1]))
        result = sr.upsample(image)
        #display result on label
        result1 = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        #open cv image to PyQt5 image
        height, width, channel = result1.shape
        bytesPerLine = 3 * width
        qImg = QtGui.QImage(result1.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
        self.label.setPixmap(QtGui.QPixmap(qImg))

        self.label.setScaledContents(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        #set progress bar value to 100
        self.progressBars[progress].setValue(100)
        self.progressBars[progress].setFormat('Done')
        #save result
        #save file dialog
        #os path to current directory

        
        
        #save result
        cv2.imwrite(save_path+'/'+model+'_'+scale+'_'+ os.path.basename(image_path) ,result)
    #upscale all function
    @QtCore.pyqtSlot()
    def on_actionRunAll_triggered(self):
        
        #get selected model
        model = self.comboBox.currentText()
        if model == 'Model':
            #display message saying select model
            QtWidgets.QMessageBox.warning(self, 'Error', 'Select model')
            return
        #save 
        


        #get selected scale
        scale = self.comboBox_2.currentText()
        
        #run model
        self.up_scale_all(model,scale)
        #display message saying all images are processed
        QtWidgets.QMessageBox.information(self, 'Done', 'All images are processed')

    def up_scale_all(self,model,scale):
        save_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Directory','',QtWidgets.QFileDialog.DontUseNativeDialog)
        #focus on main window
        self.setFocus()
        
        #get all file names from tableWidget
        for i in range(self.tableWidget.rowCount()):
            #get image path
            image_path = self.tableWidget.item(i,1).text()
            #get progress bar
            progress = i
            #run model
            self.up_scale(model,scale,image_path,progress,save_path)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())