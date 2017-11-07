from PyQt5 import QtGui, QtWidgets # Import the PyQt5 module we'll need
from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication, QUrl
import sys # We need sys so that we can pass argv to QApplication
import os
import pyqtgraph
from scipy.fftpack import fft, rfft, fftfreq, fftshift, rfftfreq, ifft
from scipy import signal
from scipy.io import wavfile # get the api
import design 
import csv
import matplotlib.pyplot as plt
import numpy as np
import warnings
import PyQt5.QtMultimedia as M
import time




class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file

        #set of variables
        self.fName=''
        self.sampleRateSelect=''
        self.fftSizeVal=''
        self.fftWindow=''
        self.inputWav=[]
        self.bulkChecker=0
        self.list=[]
        self.dir=''
        self.xAxs=[]
        self.xAxs1=[]
        self.fftArr=[]
        self.autoArr=[]
        self.ananCheck=0
        self.baseline=0.40
        self.player=M.QMediaPlayer()

        pyqtgraph.setConfigOption('background', 'w')
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined        
        warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)
        #All the GUI activity functions are activated here
        self.fftWndChng.activated[str].connect(self.onFFTActivated)        
        self.sampleRateChng.textChanged[str].connect(self.onSampleChange)
        self.fftSize.textChanged[str].connect(self.onfftSizeChange) 
        self.fileSelectButton.clicked.connect(self.onFileSelected)
        self.runFFT.clicked.connect(self.onRunFFT)
        self.exitButton.clicked.connect(QCoreApplication.instance().quit)
        self.runPowerSpectrum.clicked.connect(self.onRunPowerSpectrum)
        self.inputGraph.plotItem.showGrid(True, True, 0.7)
        self.outputGraph.plotItem.showGrid(True, True, 0.7)        
        self.runAutoCorr.clicked.connect(self.onRunAutoCorr)
        #self.saveRslt.clicked.connect(self.onSaveRslt)
        self.playButton.clicked.connect(self.onWavPlay)
        self.pauseButton.clicked.connect(self.onWavPause)
        self.selectFolder.clicked.connect(self.onFolderSelected)
        self.xLower.textChanged[str].connect(self.onInputXlowerChanged)
        self.xUpper.textChanged[str].connect(self.onInputXUpperChanged)
        self.xOLower.textChanged[str].connect(self.onOutputXlowerChanged)
        self.xOUpper.textChanged[str].connect(self.onOutputXUpperChanged)
        self.batchAnalysis.clicked.connect(self.onBatchAnalysis)
        self.stopButton.clicked.connect(self.onWavStop)
        self.bulkStopper=QMessageBox()
        self.bulkStopper.setIcon(QMessageBox.Information)
        self.bulkStopper.setText('A mass operation will start')
        self.bulkStopper.setInformativeText('To close press Ctrl+C in the terminal')
        self.bulkStopper.setStandardButtons(QMessageBox.Ok)
        
    def onBatchAnalysis(self):
        if(self.inputWav==[]):
            msg=QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText('No file/folder selected')
            msg.setInformativeText('Select a file/folder for operation')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return
        if(self.bulkChecker==0):
            msg=QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText('Batch operation not possible')
            msg.setInformativeText('Batch operation only possible for mass operation')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return
        self.bulkStopper.exec()
        self.onRunFFT()
        self.onRunAutoCorr()
    def onInputXlowerChanged(self,text):
        if(text==''):
            self.xLower.setText('0')
            text=0
        self.inputGraph.plotItem.setXRange(int(text),int(self.xUpper.text()))
    def onInputXUpperChanged(self,text):
        if(text==''):
            self.xUpper.setText('0')
            text=0
        self.inputGraph.plotItem.setXRange(int(self.xLower.text()),int(text))
    def onOutputXlowerChanged(self,text):
        if(text==''):
            self.xOLower.setText('0')
            text=0
        self.outputGraph.plotItem.setXRange(int(text),int(self.xOUpper.text()))
    def onOutputXUpperChanged(self,text):
        if(text==''):
            self.xOUpper.setText('0')
            text=0
        self.outputGraph.plotItem.setXRange(int(self.xOLower.text()),int(text))
    def onFolderSelected(self):        
        self.inputGraph.plotItem.clear()
        self.progressBar.setValue(0)
        a=QFileDialog.getExistingDirectory(caption='Select the wav folder')
        
        if(a):
            self.inputGraph.plotItem.clear()
            self.outputGraph.plotItem.clear()
            self.inputWav=[]
            self.progressBar.setValue(30)
            self.dir=a
            a=os.path.abspath(a)
            self.pathAddress.setText(a)
            lFiles=os.listdir(a)
            self.progressBar.setValue(50)
            for i in range(len(lFiles)):
                if(lFiles[i].rfind('.wav')!=-1):
                    text=a+'\\'+lFiles[i]
                    self.list.append(text)
                    #print(self.list[i])
            self.progressBar.setValue(70)
        for i in range(len(self.list)):
            rate, inpWav = wavfile.read(os.path.abspath(self.list[i]))
            #print(len(self.list))
            self.inputWav.append(inpWav)           
            #self.sampleRateChng.setText(str(rate))
        self.groupBox_4.setStyleSheet('QGroupBox {border:1px solid rgb(255, 0, 0);}')        
        self.bulkChecker=1
        self.progressBar.setValue(100)
        
    def onWavPlay(self):
        if(self.player.state()==M.QMediaPlayer.PausedState) or (self.player.state()==M.QMediaPlayer.StoppedState):
            self.player.play()
#        self.player.stateChanged.connect(lambda: self.player.disconnect())
        
    def onWavPause(self):
        if(self.player.state()==M.QMediaPlayer.PlayingState):
            self.player.pause()
    
    def onWavStop(self):
        if(self.player.state()==M.QMediaPlayer.PlayingState):
            self.player.stop()
        
    def onSaveRslt(self):
        #This function will save the output graph as image file        
        if(self.bulkChecker==0):
            self.progressBar.setValue(0)
            options = QFileDialog.Options()
            self.progressBar.setValue(25)
            options |= QFileDialog.DontUseNativeDialog
##            if(self.fftArr==[]) and (self.autoArr==[]):
##                msg=QMessageBox()
##                msg.setIcon(QMessageBox.Warning)
##                msg.setText('FFT or Autocorrelation ')
            if(self.anaCheck==1):
                fileName,_ = QFileDialog.getSaveFileName(self,'Save FFT analysis','FFToutput.csv','CSV File (*.csv);;All Files (.*)')#choose pathname
                self.progressBar.setValue(50)
                if(fileName):
                    self.progressBar.setValue(75)
                    #exporter.export(os.path.abspath(fileName))            
                    with open(os.path.abspath(fileName),'w') as csvfile:                    
                        writer=csv.DictWriter(csvfile,fieldnames=['Frequency','FFT'])
                        writer.writeheader()
                        for i in range(len(self.xAxs)):
                            writer.writerow({'Frequency':self.xAxs[i],'FFT':self.fftArr[i]})
                            
                    self.progressBar.setValue(100)
                    return
            elif(self.anaCheck==2):
                fileName,_ = QFileDialog.getSaveFileName(self,'Save Autocorrelation analysis','AutocorrelationOutput.csv','CSV File (*.csv);;All Files (.*)')#choose pathname
                fileName1,_ = QFileDialog.getSaveFileName(self,'Save Autocorrelation baseline difference','BaselineAutocorrelationOutput.csv','CSV File (*.csv);;All Files (.*)')#choose pathname
                self.progressBar.setValue(50)
                if(fileName):
                    self.progressBar.setValue(75)
                    #exporter.export(os.path.abspath(fileName))            
                    with open(os.path.abspath(fileName),'w') as csvfile:                    
                        writer=csv.DictWriter(csvfile,fieldnames=['Frequency','Autocorrelation'])
                        writer.writeheader()
                        QApplication.processEvents()
                        for i in range(len(self.xAxs1)):
                            writer.writerow({'Frequency':self.xAxs1[i],'Autocorrelation':self.autoArr[i]})
                    
                if(fileName1):
                    self.progressBar.setValue(80)
                    with open(os.path.abspath(fileName1),'w') as csvfile:                    
                        writer=csv.DictWriter(csvfile,fieldnames=['Frequency','Relative Level','Absolute Level'])
                        relBase=[]
                        QApplication.processEvents()
                        for i in range(len(self.autoArr)):
                            temp=self.autoArr[i]-self.baseline
                            temp=temp*(1/(1-self.baseline))
                            relBase.append(temp)
                        writer.writeheader()
                        QApplication.processEvents()
                        for i in range(len(self.xAxs1)):
                            writer.writerow({'Frequency':self.xAxs1[i],'Relative Level':relBase[i],'Absolute Level':self.autoArr[i]})
        else:            
            if(self.anaCheck==1):
                QApplication.processEvents()
                for j in range(len(self.inputWav)):
                    self.progressBar.setValue(0)
                    saveName=self.list[j]
                    saveName=saveName[saveName.rfind('\\')+1:]
                    saveName=saveName[0:saveName.rfind('.wav')]
                    saveName=saveName+'_FFT'+'.csv'
                    saveName=self.dir+'\\'+saveName
                    saveName=os.path.abspath(saveName)
                    self.progressBar.setValue(20)
                    col1=self.xAxs[j]
                    col2=self.fftArr[j]
                    self.progressBar.setValue(30)
                    with open(os.path.abspath(saveName),'w') as csvfile:
                        self.progressBar.setValue(40)
                        writer=csv.DictWriter(csvfile,fieldnames=['Frequency','FFT'])
                        writer.writeheader()
                        self.progressBar.setValue(50)
                        QApplication.processEvents()
                        for i in range(len(col1)):
                            writer.writerow({'Frequency':col1[i],'FFT':col2[i]})            
                                      
                    self.progressBar.setValue(100)
            elif(self.anaCheck==2):
                QApplication.processEvents()
                for j in range(len(self.inputWav)):
                    self.progressBar.setValue(0)                                
                    saveName=self.list[j]
                    saveName=saveName[saveName.rfind('\\')+1:]
                    saveName=saveName[0:saveName.rfind('.wav')]
                    saveName=saveName+'_Autocorrelation_'+self.xOLower.text()+'_'+self.xOUpper.text()+'.csv'
                    saveName=self.dir+'\\'+saveName
                    saveName=os.path.abspath(saveName)
                    self.progressBar.setValue(60)
                    col3=self.xAxs1[j]
                    col4=self.autoArr[j]                    
                    self.progressBar.setValue(70)
                    with open(os.path.abspath(saveName),'w') as csvfile:
                        self.progressBar.setValue(80)
                        writer=csv.DictWriter(csvfile,fieldnames=['Frequency','Autocorrelation'])
                        writer.writeheader()
                        self.progressBar.setValue(90)
                        for i in range(len(col3)):
                            writer.writerow({'Frequency':col3[i],'Autocorrelation':col4[i]})
                    
                    self.progressBar.setValue(100)
                QApplication.processEvents()
                for j in range(len(self.inputWav)):
                    self.progressBar.setValue(0)                                
                    saveName=self.list[j]
                    saveName=saveName[saveName.rfind('\\')+1:]
                    saveName=saveName[0:saveName.rfind('.wav')]
                    saveName=saveName+'_Autocorrelation_Baseline_'+self.xOLower.text()+'_'+self.xOUpper.text()+'.csv'
                    saveName=self.dir+'\\'+saveName
                    saveName=os.path.abspath(saveName)
                    self.progressBar.setValue(60)
                    col3=self.xAxs1[j]
                    col4=self.autoArr[j]                    
                    self.progressBar.setValue(70)
                    with open(os.path.abspath(saveName),'w') as csvfile:
                        self.progressBar.setValue(80)
                        writer=csv.DictWriter(csvfile,fieldnames=['Frequency','Relative Level','Absolute Level'])
                        relBase=[]
                        QApplication.processEvents()
                        for i in range(len(col4)):
                            temp=col4[i]-self.baseline
                            temp=temp*(1/(1-self.baseline))
                            relBase.append(temp)
                        writer.writeheader()
                        self.progressBar.setValue(90)
                        QApplication.processEvents()
                        for i in range(len(col3)):
                            writer.writerow({'Frequency':col3[i],'Relative Level':relBase[i],'Absolute Level':col4[i]})
                    
                    self.progressBar.setValue(100)
            return
            
    def onFFTActivated(self, text):#Calculate FFT pressed  
        self.fftWindow=text
        
    def onSampleChange(self, text):#Sample rate changed
        self.sampleRateSelect=text
        
    def onfftSizeChange(self, text):
        self.fftSizeVal=text              

    def onFileSelected(self): #On file selection the WAV file will be plotted        
        self.progressBar.setValue(0)
        options = QFileDialog.Options()
        self.progressBar.setValue(25)
        options |= QFileDialog.DontUseNativeDialog
        fileName,_= QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","WAV Files (*.wav)")
        self.progressBar.setValue(50)
        if (fileName):
            self.inputWav=[]
            self.inputGraph.plotItem.clear()
            self.outputGraph.plotItem.clear()
            self.fName=os.path.abspath(fileName)
            self.dir=self.fName[0:self.fName.rfind('\\')]
            self.pathAddress.setText(self.fName)
            self.progressBar.setValue(75)
            rate, inpWav = wavfile.read(os.path.abspath(self.fName))
            self.inputWav=inpWav            
            self.sampleRateChng.setText(str(rate))
            self.progressBar.setValue(100)
            self.progressBar.setValue(0)        
            inpW=self.inputWav
            pcmMax=np.max(np.abs(inpW))
            self.progressBar.setValue(30)
            self.inputGraph.plotItem.setRange(yRange=[-pcmMax-300, pcmMax+300])
            self.progressBar.setValue(60)
            self.inputGraph.plotItem.setMouseEnabled(x=True, y=False)
            self.inputGraph.plotItem.setLimits(minXRange=5)#setting minimum panning range
            self.inputGraph.plotItem.setXRange(int(self.xLower.text()),int(self.xUpper.text()))
            self.progressBar.setValue(75)
            pen=pyqtgraph.mkPen(color='g')        
            curve=self.inputGraph.plot(inpW, pen=pen)
            self.bulkChecker=0
            url=QUrl.fromLocalFile(os.path.abspath(self.pathAddress.text()))                
            content=M.QMediaContent(url)
            self.groupBox_4.setStyleSheet('QGroupBox {border:4px solid rgb(0, 163, 0);}')               
            self.player.setMedia(content)
            self.progressBar.setValue(100)        
        
    def onRunFFT(self): #FFT spectrum
        self.xAxs=[]
        self.fftArr=[]
        if(self.inputWav==[]):
            msg=QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText('No file/folder selected')
            msg.setInformativeText('Select a file/folder for operation')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return
        if(self.bulkChecker==0):
            self.progressBar.setValue(0)
            inpW=self.inputWav
            self.outputGraph.plotItem.clear()
            self.outputGraph.plotItem.enableAutoRange() #enabling autorange
            pen=pyqtgraph.mkPen(color='r')
            self.progressBar.setValue(10)
            x=np.linspace(0,len(inpW)/44100,len(inpW)) #window size
            y=np.array(inpW)
            dx = np.diff(x)
            self.progressBar.setValue(15)
            uniform = not np.any(np.abs(dx-dx[0]) > (abs(dx[0]) / 1000.)) #uniformity checking
            if not uniform:
                x2 = np.linspace(x[0], x[-1], len(x))
                y = np.interp(x2, x, y)
                self.progressBar.setValue(25)
                x = x2
            self.progressBar.setValue(30)
            f = np.fft.fft(y) / len(y) #Main fft 
            self.progressBar.setValue(60)        
            N=int(len(f)/2) 
            y = abs(f[1:N]) #Taking the real part        
            dt = x[-1] - x[0]        
            x = np.linspace(0, 0.5*len(x)/dt, len(y)) #frequency spacing
            self.progressBar.setValue(80)
            self.outputGraph.plotItem.setMouseEnabled(x=True, y=False) #disabling mouse
            self.outputGraph.plotItem.setXRange(int(self.xOLower.text()),int(self.xOUpper.text()))
            #plotting FFT with a scaling factor
            #2.5 was found on a trial and error basis
            #Change it if you need. It satisfies all the signals you provided
            self.xAxs=x
            #print(len(x))
            self.fftArr=2.5*y
            self.outputGraph.plot(x,2.5*y, pen=pen)       
            self.outputGraph.setLabel('bottom', 'Frequency', units='Hz')  #changing unit here changes scale      
            self.outputGraph.setLabel('left', 'Amplitude', units='V')                
            self.outputGraph.setTitle('FFT Spectrum')            
            saveName=self.fName
            saveName=saveName[saveName.rfind('\\')+1:]
            saveName=saveName[0:saveName.rfind('.wav')]
            saveName=saveName+'_FFT_Range_'+self.xOLower.text()+'-'+self.xOUpper.text()+'.png'
            saveName=self.dir+'\\'+saveName
            saveName=os.path.abspath(saveName)            
            print(saveName)
            plt.plot(x,2.5*y)
            plt.xlim((int(self.xOLower.text()),int(self.xOUpper.text())))
            plt.xlabel('Frequency')
            plt.ylabel('Amplitude')
            plt.title('FFT Spectrum')
            plt.savefig(saveName,format='png')
            plt.clf()
            self.anaCheck=1
            self.onSaveRslt()
            self.progressBar.setValue(100)
        else:
            self.progressBar.setValue(0)
            inpW=self.inputWav
            for i in range(len(inpW)):
                self.outputGraph.plotItem.clear()
                self.outputGraph.plotItem.enableAutoRange() #enabling autorange
                pen=pyqtgraph.mkPen(color='r')
                self.progressBar.setValue(10)
                x=np.linspace(0,len(inpW[i])/44100,len(inpW[i])) #window size
                y=np.array(inpW[i])
                dx = np.diff(x)
                self.progressBar.setValue(15)
                uniform = not np.any(np.abs(dx-dx[0]) > (abs(dx[0]) / 1000.)) #uniformity checking
                if not uniform:
                    x2 = np.linspace(x[0], x[-1], len(x))
                    y = np.interp(x2, x, y)
                    self.progressBar.setValue(25)
                    x = x2
                self.progressBar.setValue(30)
                f = np.fft.fft(y) / len(y) #Main fft 
                self.progressBar.setValue(60)        
                N=int(len(f)/2) 
                y = abs(f[1:N]) #Taking the real part        
                dt = x[-1] - x[0]        
                x = np.linspace(0, 0.5*len(x)/dt, len(y)) #frequency spacing
                self.progressBar.setValue(80)
                self.outputGraph.plotItem.setMouseEnabled(x=True, y=False) #disabling mouse
                self.outputGraph.plotItem.setXRange(int(self.xOLower.text()),int(self.xOUpper.text()))
                #plotting FFT with a scaling factor
                #2.5 was found on a trial and error basis
                #Change it if you need. It satisfies all the signals you provided
                self.xAxs.append(x)
                #print(len(x))
                self.fftArr.append(2.5*y)
                self.outputGraph.plot(x,2.5*y, pen=pen)       
                self.outputGraph.setLabel('bottom', 'Frequency', units='Hz')  #changing unit here changes scale      
                self.outputGraph.setLabel('left', 'Amplitude', units='V')                
                self.outputGraph.setTitle('FFT Spectrum')
                pyqtgraph.QtGui.QApplication.processEvents()
                saveName=self.list[i]
                saveName=saveName[saveName.rfind('\\')+1:]
                saveName=saveName[0:saveName.rfind('.wav')]
                saveName=saveName+'_FFT_Range_'+self.xOLower.text()+'-'+self.xOUpper.text()+'.png'
                saveName=self.dir+'\\'+saveName
                saveName=os.path.abspath(saveName)                
                plt.plot(x,2.5*y)
                plt.xlim((int(self.xOLower.text()),int(self.xOUpper.text())))
                plt.xlabel('Frequency')
                plt.ylabel('Amplitude')
                plt.title('FFT Spectrum')
                plt.savefig(saveName,format='png')
                plt.clf()
                self.progressBar.setValue(100)
                time.sleep(1)
            self.anaCheck=1
            self.onSaveRslt()
                

    def doPSA(self,inpW,flNme):
        if self.fftWindow == "Rectangle": #Window Rectangle
            self.outputGraph.plotItem.clear() #clearing window
            self.outputGraph.plotItem.enableAutoRange() #enabling autorange
            x=inpW
            self.progressBar.setValue(15) 
            window = signal.boxcar(int(self.fftSizeVal)) #boxcar or rectangle window
            x=x[0:int(self.fftSizeVal)]*window
            self.progressBar.setValue(30)
            mags = np.abs(rfft(x)) #real time fourier transform
            mags = 20*np.log10(mags)
            self.progressBar.setValue(60)
            mags -= max(mags)
            pen=pyqtgraph.mkPen(color='r')
            self.outputGraph.plotItem.setMouseEnabled(x=True, y=False) #disabling mouse
            self.outputGraph.plot(mags,pen=pen)
            self.outputGraph.setLabel('bottom', 'Frequency', units='Bin')
            self.outputGraph.setLabel('left', 'Magnitude', units='dB')  
            saveName=flNme
            saveName=saveName[saveName.rfind('\\')+1:]            
            self.outputGraph.setTitle('Power spectrum-Rectangle window of '+saveName)          
            pyqtgraph.QtGui.QApplication.processEvents()
            saveName=saveName[0:saveName.rfind('.wav')]
            saveName=saveName+'_PFS-Rectangle_'+'.png'
            saveName=self.dir+'\\'+saveName
            saveName=os.path.abspath(saveName) 
            plt.plot(mags)
            #plt.xlim((int(self.xOLower.text()),int(self.xOUpper.text())))
            plt.xlabel('Frequency')
            plt.ylabel('Magnitude')
            plt.title('Power spectrum-Rectangle window')
            plt.savefig(saveName,format='png')
            plt.clf()
            self.progressBar.setValue(100)            
        elif self.fftWindow == "Hanning": #calculate hanning window spectrum
            self.outputGraph.plotItem.clear() #clearing window
            self.outputGraph.plotItem.enableAutoRange() #enabling autorange
            x=inpW
            self.progressBar.setValue(15) 
            window = signal.hann(int(self.fftSizeVal))
            x=x[0:int(self.fftSizeVal)]*window
            self.progressBar.setValue(30)
            mags = np.abs(rfft(x)) #real time fourier transform
            mags = 20*np.log10(mags)
            self.progressBar.setValue(60)
            mags -= max(mags)
            pen=pyqtgraph.mkPen(color='r')
            self.outputGraph.plotItem.setMouseEnabled(x=True, y=False) #disabling mouse
            self.outputGraph.plot(mags,pen=pen)
            self.outputGraph.setLabel('bottom', 'Frequency', units='Bin')
            self.outputGraph.setLabel('left', 'Magnitude', units='dB')
            saveName=flNme
            saveName=saveName[saveName.rfind('\\')+1:]            
            self.outputGraph.setTitle('Power spectrum-Hanning window of '+saveName)          
            pyqtgraph.QtGui.QApplication.processEvents()
            saveName=saveName[0:saveName.rfind('.wav')]
            saveName=saveName+'_PFS-Hanning_'+'.png'
            saveName=self.dir+'\\'+saveName
            saveName=os.path.abspath(saveName) 
            plt.plot(mags)
            #plt.xlim((int(self.xOLower.text()),int(self.xOUpper.text())))
            plt.xlabel('Frequency')
            plt.ylabel('Magnitude')
            plt.title('Power spectrum-Hanning window')
            plt.savefig(saveName,format='png')
            plt.clf()
            self.progressBar.setValue(100)
        elif self.fftWindow == "Hamming": #calculate hamming window spectrum
            self.outputGraph.plotItem.clear() #clearing window
            self.outputGraph.plotItem.enableAutoRange() #enabling autorange
            x=inpW
            self.progressBar.setValue(15) 
            window = signal.hamming(int(self.fftSizeVal))
            x=x[0:int(self.fftSizeVal)]*window
            self.progressBar.setValue(30)
            mags = np.abs(rfft(x)) #real time fourier transform
            mags = 20*np.log10(mags)
            self.progressBar.setValue(60)
            mags -= max(mags)
            pen=pyqtgraph.mkPen(color='r')
            self.outputGraph.plotItem.setMouseEnabled(x=True, y=False) #disabling mouse
            self.outputGraph.plot(mags,pen=pen) #plotting graph
            self.outputGraph.setLabel('bottom', 'Frequency', units='Bin')
            self.outputGraph.setLabel('left', 'Magnitude', units='dB')
            saveName=flNme
            saveName=saveName[saveName.rfind('\\')+1:]            
            self.outputGraph.setTitle('Power spectrum-Hamming window of '+saveName)          
            pyqtgraph.QtGui.QApplication.processEvents()
            saveName=saveName[0:saveName.rfind('.wav')]
            saveName=saveName+'_PFS-Hamming_'+'.png'
            saveName=self.dir+'\\'+saveName
            saveName=os.path.abspath(saveName)
            plt.plot(mags)
            #plt.xlim((int(self.xOLower.text()),int(self.xOUpper.text())))
            plt.xlabel('Frequency')
            plt.ylabel('Magnitude')
            plt.title('Power spectrum-Hamming window')
            plt.savefig(saveName,format='png')
            plt.clf()
            self.progressBar.setValue(100)
        elif self.fftWindow == "Kaiser":#calculate kaiser window spectrum
            self.outputGraph.plotItem.clear()#clearing window
            self.outputGraph.plotItem.enableAutoRange() #enabling autorange
            x=inpW
            self.progressBar.setValue(15) 
            window = signal.kaiser(int(self.fftSizeVal), beta=14)
            x=x[0:int(self.fftSizeVal)]*window
            self.progressBar.setValue(30)
            mags = np.abs(rfft(x))
            mags = 20*np.log10(mags)
            self.progressBar.setValue(60)
            mags -= max(mags)
            pen=pyqtgraph.mkPen(color='r')
            self.outputGraph.plotItem.setMouseEnabled(x=True, y=False) #disabling mouse
            self.outputGraph.plot(mags,pen=pen)
            self.outputGraph.setLabel('bottom', 'Frequency', units='Bin')
            self.outputGraph.setLabel('left', 'Magnitude', units='dB')
            saveName=flNme
            saveName=saveName[saveName.rfind('\\')+1:]            
            self.outputGraph.setTitle('Power spectrum-Kaiser window of '+saveName)          
            pyqtgraph.QtGui.QApplication.processEvents()
            saveName=saveName[0:saveName.rfind('.wav')]
            saveName=saveName+'_PFS-Kaiser_'+'.png'
            saveName=self.dir+'\\'+saveName
            saveName=os.path.abspath(saveName)
            plt.plot(mags)
            #plt.xlim((int(self.xOLower.text()),int(self.xOUpper.text())))
            plt.xlabel('Frequency')
            plt.ylabel('Magnitude')
            plt.title('Power spectrum-Kaiser window')
            plt.savefig(saveName,format='png')
            plt.clf()
            self.progressBar.setValue(100)
        elif self.fftWindow == "Nuttall":#calculate nutall window spectrum
            self.outputGraph.plotItem.clear()#clearing window
            self.outputGraph.plotItem.enableAutoRange() #enabling autorange            
            x=inpW
            self.progressBar.setValue(15) 
            window = signal.nuttall(int(self.fftSizeVal))
            x=x[0:int(self.fftSizeVal)]*window
            self.progressBar.setValue(30)
            mags = np.abs(rfft(x))
            mags = 20*np.log10(mags)
            self.progressBar.setValue(60)
            mags -= max(mags)
            pen=pyqtgraph.mkPen(color='r')
            self.outputGraph.plotItem.setMouseEnabled(x=True, y=False) #disabling mouse
            self.outputGraph.plot(mags,pen=pen)
            self.outputGraph.setLabel('bottom', 'Frequency', units='Bin')
            self.outputGraph.setLabel('left', 'Magnitude', units='dB')
            saveName=flNme
            saveName=saveName[saveName.rfind('\\')+1:]            
            self.outputGraph.setTitle('Power spectrum-Nuttall window of '+saveName)          
            pyqtgraph.QtGui.QApplication.processEvents()
            saveName=saveName[0:saveName.rfind('.wav')]
            saveName=saveName+'_PFS-Nuttall_'+'.png'
            saveName=self.dir+'\\'+saveName
            saveName=os.path.abspath(saveName)
            plt.plot(mags)
            #plt.xlim((int(self.xOLower.text()),int(self.xOUpper.text())))
            plt.xlabel('Frequency')
            plt.ylabel('Magnitude')
            plt.title('Power spectrum-Nuttall window')
            plt.savefig(saveName,format='png')
            plt.clf()
            self.progressBar.setValue(100)
        elif self.fftWindow == "Parzen":#calculate parzen window spectrum
            self.outputGraph.plotItem.clear() #clearing window
            self.outputGraph.plotItem.enableAutoRange() #enabling autorange
            x=inpW
            self.progressBar.setValue(15) 
            window = signal.parzen(int(self.fftSizeVal))
            x=x[0:int(self.fftSizeVal)]*window
            self.progressBar.setValue(30)
            mags = np.abs(rfft(x))#real time fourier transform
            mags = 20*np.log10(mags)
            self.progressBar.setValue(60)
            mags -= max(mags)
            pen=pyqtgraph.mkPen(color='r')
            self.outputGraph.plotItem.setMouseEnabled(x=True, y=False) #disabling mouse
            self.outputGraph.plot(mags,pen=pen)
            self.outputGraph.setLabel('bottom', 'Frequency', units='Bin')
            self.outputGraph.setLabel('left', 'Magnitude', units='dB')
            saveName=flNme
            saveName=saveName[saveName.rfind('\\')+1:]            
            self.outputGraph.setTitle('Power spectrum-Parzen window of '+saveName)          
            pyqtgraph.QtGui.QApplication.processEvents()
            saveName=saveName[0:saveName.rfind('.wav')]
            saveName=saveName+'_PFS-Parzen_'+'.png'
            saveName=self.dir+'\\'+saveName
            saveName=os.path.abspath(saveName)
            plt.plot(mags)
            #plt.xlim((int(self.xOLower.text()),int(self.xOUpper.text())))
            plt.xlabel('Frequency')
            plt.ylabel('Magnitude')
            plt.title('Power spectrum-Parzen window')
            plt.savefig(saveName,format='png')
            plt.clf()
            self.progressBar.setValue(100)
        elif self.fftWindow == "Blackman":#calculate blackman window spectrum
            self.outputGraph.plotItem.clear()#clearing window
            self.outputGraph.plotItem.enableAutoRange() #enabling autorange
            x=inpW
            self.progressBar.setValue(15) 
            window = signal.blackman(int(self.fftSizeVal))
            x=x[0:int(self.fftSizeVal)]*window
            self.progressBar.setValue(30) 
            mags = np.abs(rfft(x))#real time fourier transform
            mags = 20*np.log10(mags)
            self.progressBar.setValue(60) 
            mags -= max(mags)
            pen=pyqtgraph.mkPen(color='r')
            self.outputGraph.plotItem.setMouseEnabled(x=True, y=False) #disabling mouse
            self.outputGraph.plot(mags,pen=pen)
            self.outputGraph.setLabel('bottom', 'Frequency', units='Bin')
            self.outputGraph.setLabel('left', 'Magnitude', units='dB')
            saveName=flNme
            saveName=saveName[saveName.rfind('\\')+1:]            
            self.outputGraph.setTitle('Power spectrum-Blackman window of '+saveName)          
            pyqtgraph.QtGui.QApplication.processEvents()
            saveName=saveName[0:saveName.rfind('.wav')]
            saveName=saveName+'_PFS-Blackman_'+'.png'
            saveName=self.dir+'\\'+saveName
            saveName=os.path.abspath(saveName)
            plt.plot(mags)
            #plt.xlim((int(self.xOLower.text()),int(self.xOUpper.text())))
            plt.xlabel('Frequency')
            plt.ylabel('Magnitude')
            plt.title('Power spectrum-Blackman window')
            plt.savefig(saveName,format='png')
            plt.clf()
            self.progressBar.setValue(100) 
        elif self.fftWindow == "Flattop":#calculate flattop window spectrum
            self.outputGraph.plotItem.clear()#clearing window
            self.outputGraph.plotItem.enableAutoRange() #enabling autorange            
            x=inpW
            self.progressBar.setValue(15)            
            window = signal.flattop(int(self.fftSizeVal))
            x=x[0:int(self.fftSizeVal)]*window
            self.progressBar.setValue(30) 
            mags = np.abs(rfft(x))#real time fourier transform
            mags = 20*np.log10(mags)
            self.progressBar.setValue(60) 
            mags -= max(mags)
            pen=pyqtgraph.mkPen(color='r')
            self.outputGraph.plotItem.setMouseEnabled(x=True, y=False) #disabling mouse
            self.outputGraph.plot(mags,pen=pen)
            self.outputGraph.setLabel('bottom', 'Frequency', units='Bin')
            self.outputGraph.setLabel('left', 'Magnitude', units='dB')
            saveName=flNme
            saveName=saveName[saveName.rfind('\\')+1:]            
            self.outputGraph.setTitle('Power spectrum-Flattop window of '+saveName)          
            pyqtgraph.QtGui.QApplication.processEvents()
            saveName=saveName[0:saveName.rfind('.wav')]
            saveName=saveName+'_PFS-Flattop_'+'.png'
            saveName=self.dir+'\\'+saveName
            saveName=os.path.abspath(saveName)
            plt.plot(mags)
            #plt.xlim((int(self.xOLower.text()),int(self.xOUpper.text())))
            plt.xlabel('Frequency')
            plt.ylabel('Magnitude')
            plt.title('Power spectrum-Flattop window')
            plt.savefig(saveName,format='png')
            plt.clf()
            self.progressBar.setValue(100) 
        elif self.fftWindow == "Dolph-Chebyshev":#calculate dolph chebyshev window spectrum
            self.outputGraph.plotItem.clear()#clearing window
            self.outputGraph.plotItem.enableAutoRange() #enabling autorange                               
            x=inpW
            self.progressBar.setValue(15) 
            window = signal.chebwin(int(self.fftSizeVal), at=100)
            x=x[0:int(self.fftSizeVal)]*window
            self.progressBar.setValue(30) 
            mags = np.abs(rfft(x))#real time fourier transform
            mags = 20*np.log10(mags)
            self.progressBar.setValue(60) 
            mags -= max(mags)
            pen=pyqtgraph.mkPen(color='r')
            self.outputGraph.plotItem.setMouseEnabled(x=True, y=False) #disabling mouse
            self.outputGraph.plot(mags,pen=pen)
            self.outputGraph.setLabel('bottom', 'Frequency', units='Bin')
            self.outputGraph.setLabel('left', 'Magnitude', units='dB')
            saveName=flNme
            saveName=saveName[saveName.rfind('\\')+1:]            
            self.outputGraph.setTitle('Power spectrum-Chebyshev window of '+saveName)          
            pyqtgraph.QtGui.QApplication.processEvents()
            saveName=saveName[0:saveName.rfind('.wav')]
            saveName=saveName+'_PFS-Chebyshev_'+'.png'
            saveName=self.dir+'\\'+saveName
            saveName=os.path.abspath(saveName) 
            plt.plot(mags)
            #plt.xlim((int(self.xOLower.text()),int(self.xOUpper.text())))
            plt.xlabel('Frequency')
            plt.ylabel('Magnitude')
            plt.title('Power spectrum-Dolph Chebyshev window')
            plt.savefig(saveName,format='png')
            plt.clf()
            self.progressBar.setValue(100)
            
    def onRunPowerSpectrum(self): #Power spectrum (in dB)        
        if(self.inputWav==[]):
            msg=QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText('No file/folder selected')
            msg.setInformativeText('Select a file/folder for operation')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return
        self.progressBar.setValue(0)
        self.fftSizeVal=self.fftSize.text()
        self.fftWindow=self.fftWndChng.currentText()
        self.sampleRateSelect=self.sampleRateChng.text()
        self.outputGraph.plotItem.clear()
        self.outputGraph.plotItem.enableAutoRange() #enabling autorange
        self.outputGraph.plotItem.showGrid(True, True, 0.7)
        self.progressBar.setValue(10)
        if(self.bulkChecker==0):
            inpW=self.inputWav
            self.doPSA(inpW,self.fName)
        else:
            inpW=self.inputWav
            for i in range(len(inpW)):
                self.doPSA(inpW[i],self.list[i])
                time.sleep(2)

    def onRunAutoCorr(self): #run autocorrelation
        self.autoArr=[]
        self.xAxs1=[]
        if(self.inputWav==[]):
            msg=QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText('No file/folder selected')
            msg.setInformativeText('Select a file/folder for operation')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return
        if(self.bulkChecker==0):
            self.progressBar.setValue(0)
            inpW=self.inputWav        
            self.outputGraph.plotItem.clear()
            self.outputGraph.plotItem.enableAutoRange() #enabling autorange
            self.outputGraph.plotItem.showGrid(True, True, 0.7)
            self.progressBar.setValue(10)
            x=np.linspace(0,len(inpW)/44100,len(inpW))#setting window size
            x=np.arange(len(inpW))
            y=np.array(inpW)
            dx = np.diff(x)
            uniform = not np.any(np.abs(dx-dx[0]) > (abs(dx[0]) / 1000.)) #checking uniformity
            if not uniform:
                x2 = np.linspace(x[0], x[-1], len(x))
                self.progressBar.setValue(15)
                y = np.interp(x2, x, y)
                x = x2
            self.progressBar.setValue(30)
            f = np.fft.fft(y) / len(y) #FFT spectrum
            N=int(len(f)/2) 
            y = abs(f[1:N]) #Taking the real part        
            dt = x[-1] - x[0]               
            x = np.linspace(0, 0.5*len(x)/dt, len(y))            
            self.progressBar.setValue(40)        
            #the main autocorrelation
            #I used fftconvolve with reverse y to find correlation
            #i could not figure out the exact function sigview used
            #so I built one of my own
            autocorr=signal.fftconvolve(y,y[::-1],mode='full')
            autocorr=autocorr[len(autocorr)//2:]            
            self.progressBar.setValue(70)            
            autocorr=autocorr/np.max(autocorr)            
#            val1=0.42
#            val2=1/(1-val1)
#            for i in range(len(autocorr)):
#                autocorr[i]=autocorr[i]-val1
#                autocorr[i]=autocorr[i]*val2
            pen=pyqtgraph.mkPen(color='r')
            self.outputGraph.plotItem.setMouseEnabled(x=True, y=False) #disabling mouse
            self.outputGraph.plotItem.setXRange(int(self.xOLower.text()),int(self.xOUpper.text()))
            #plotting autocorrelation
            # i also added a scaling factor 10.4 so that the peaks are at the same place as sigview
            #it satisfies all the signals you provided
            self.xAxs1=np.arange(0,len(autocorr))/10.4
            self.autoArr=autocorr            
            self.outputGraph.plot(np.arange(0,len(autocorr))/10.4, autocorr,pen=pen)
            self.outputGraph.setLabel('bottom', 'Frequency', units='Hz')
            self.outputGraph.setLabel('left', 's')
            self.outputGraph.setTitle('Autocorrelation')
            self.progressBar.setValue(90)
            saveName=self.fName
            saveName=saveName[saveName.rfind('\\')+1:]
            saveName=saveName[0:saveName.rfind('.wav')]
            saveName=saveName+'_Autocorrelation_Range_'+self.xOLower.text()+'-'+self.xOUpper.text()+'.png'
            saveName=self.dir+'\\'+saveName
            saveName=os.path.abspath(saveName)            
            print(saveName)
            plt.plot(np.arange(0,len(autocorr))/10.4, autocorr)
            plt.xlim((int(self.xOLower.text()),int(self.xOUpper.text())))
            plt.xlabel('Frequency')
            plt.ylabel('s')
            plt.title('Autocorrelation')
            plt.savefig(saveName,format='png')
            plt.clf()
            self.anaCheck=2
            self.onSaveRslt()
            self.progressBar.setValue(100)
        else:
            self.progressBar.setValue(0)
            inpW=self.inputWav
            QApplication.processEvents()
            for i in range(len(inpW)):
                self.outputGraph.plotItem.clear()
                self.outputGraph.plotItem.enableAutoRange() #enabling autorange
                self.outputGraph.plotItem.showGrid(True, True, 0.7)
                self.progressBar.setValue(10)
                x=np.linspace(0,len(inpW[i])/44100,len(inpW[i]))#setting window size
                x=np.arange(len(inpW[i]))
                y=np.array(inpW[i])
                dx = np.diff(x)
                uniform = not np.any(np.abs(dx-dx[0]) > (abs(dx[0]) / 1000.)) #checking uniformity
                if not uniform:
                    x2 = np.linspace(x[0], x[-1], len(x))
                    self.progressBar.setValue(15)
                    y = np.interp(x2, x, y)
                    x = x2
                self.progressBar.setValue(30)
                f = np.fft.fft(y) / len(y) #FFT spectrum
                N=int(len(f)/2) 
                y = abs(f[1:N]) #Taking the real part        
                dt = x[-1] - x[0]               
                x = np.linspace(0, 0.5*len(x)/dt, len(y))            
                self.progressBar.setValue(40)        
                #the main autocorrelation
                #I used fftconvolve with reverse y to find correlation
                #i could not figure out the exact function sigview used
                #so I built one of my own
                autocorr=signal.fftconvolve(y,y[::-1],mode='full')
                autocorr=autocorr[len(autocorr)//2:]            
                self.progressBar.setValue(70)
                autocorr=autocorr/np.max(autocorr)            
#                val1=0.42
#                val2=1/(1-val1)
#                for i in range(len(autocorr)):
#                    autocorr[i]=autocorr[i]-val1
#                    autocorr[i]=autocorr[i]*val2        
                pen=pyqtgraph.mkPen(color='r')
                self.outputGraph.plotItem.setMouseEnabled(x=True, y=False) #disabling mouse
                self.outputGraph.plotItem.setXRange(int(self.xOLower.text()),int(self.xOUpper.text()))
                #plotting autocorrelation
                # i also added a scaling factor 10.4 so that the peaks are at the same place as sigview
                #it satisfies all the signals you provided
                self.xAxs1.append(np.arange(0,len(autocorr))/10.4)
                self.autoArr.append(autocorr)
                self.outputGraph.plot(np.arange(0,len(autocorr))/10.4, autocorr,pen=pen)
                self.outputGraph.setLabel('bottom', 'Frequency', units='Hz')
                self.outputGraph.setLabel('left', 's')
                self.outputGraph.setTitle('Autocorrelation')
                self.progressBar.setValue(90)
                pyqtgraph.QtGui.QApplication.processEvents()
                saveName=self.list[i]
                saveName=saveName[saveName.rfind('\\')+1:]
                saveName=saveName[0:saveName.rfind('.wav')]
                saveName=saveName+'_Autocorrelation_Range_'+self.xOLower.text()+'-'+self.xOUpper.text()+'.png'
                saveName=self.dir+'\\'+saveName
                saveName=os.path.abspath(saveName)                
                plt.plot(np.arange(0,len(autocorr))/10.4, autocorr)
                plt.xlim((int(self.xOLower.text()),int(self.xOUpper.text())))
                plt.xlabel('Frequency')
                plt.ylabel('s')
                plt.title('Autocorrelation')
                plt.savefig(saveName,format='png')
                plt.clf()
                self.progressBar.setValue(100)
                time.sleep(1)
            self.anaCheck=2
            self.onSaveRslt()



        
def main():
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    form = ExampleApp()                 # We set the form to be our ExampleApp (design)
    form.show()                         # Show the form
    app.exec_()                         # and execute the app


if __name__ == '__main__':              # if we're running file directly and not importing it
    main()
