from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QMenu,
    QDialog,
    QTextEdit,
    QDialogButtonBox,
    QLineEdit,
    QProgressBar
)
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtCore import QThread, QObject, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt6.QtCore import Qt
from latex import build_pdf
import os, platform, subprocess
import sys
from datetime import datetime
import os

temp1 = "\\documentclass[12pt,a4paper]{article}\n\\usepackage[utf8]{inputenc}\n\\usepackage{amsmath}\n\\usepackage{amsfonts}\n\\usepackage{amssymb}\n\\usepackage{graphicx}\n\\usepackage{mhchem} \\RequirePackage{amsmath,amssymb,latexsym}\n\\author{You}\n\\title{Title}\n\\date{\\today}\n\\begin{document}\n\\maketitle\n"
temp2 = "\n\\end{document}"
fname = ''

titleFont = QFont('Helvetica', 32, QFont.Weight.Bold)
subtitleFont = QFont('Helvetica', 20, QFont.Weight.Bold)

ver = '0.0.3-d'
app_name = 'LaTeX Maker'

class BuildWorker(QThread):
    progress = Signal(int)
    finished = Signal(int)

    @Slot(str)
    def run(self, tex):
        try:
            global fname
            self.progress.emit(10)
            allpy = ''
            index = 0
            py_outs = []
            prints = []
            rem = []
            stripped = tex
            while '<py>' in stripped and '</py>' in stripped:
                py = stripped.split('<py>')[1].split('</py>')[0]
                allpy = allpy + py + '\n'
                self.progress.emit(5)
                temp = "<py>" + py + "</py>"
                rem.append(temp)
                stripped = stripped.replace(temp, '')
                prev = 0
                for i in prints:
                    prev += i
                try:
                    p = allpy.count('print(') - prev
                    print(p, prev)
                except:
                    p = allpy.count('print(')
                prints.append(p)
                index += 1
            #print(temp)
            self.progress.emit(10)
            with open('temp.py', 'wt', encoding='UTF-8') as tempy:
                tempy.write(allpy)
            self.progress.emit(20)
            python = ""
            if platform.system() == 'Darwin':       # macOS
                python = "python3"
            elif platform.system() == 'Windows':    # Windows
                python = "python"
            else:               
                python = "python3"                    # linux variants
            self.progress.emit(30)
            temptex = tex
            try:
                #print('try')
                rem1 = rem
                py_code = str(subprocess.check_output([python, 'temp.py'])).split("b'")[1].split("\\n'")[0].replace('\\\\', '\\').replace("\\n", "\n")
                #print(py_code)
                #print(py_outs)
                #print(index, py_code, py_outs, prints)
                if py_code == "'":
                    py_code = ''
                if index != 0:
                    #print(prints)
                    if index > 1:
                        py_outs = py_code.split('\\\\')
                        #print(py_outs)
                        rep = ''
                        for i in range(index):
                            rep = ''
                            for j in range(prints[i]):
                                #print(index, i, j)
                                rep = rep + py_outs[i+j]
                                if prints[i] > 1 and j < prints[i]-1:
                                    rep = rep + ' \\\\\n'
                                #print(rep)
                            temptex = temptex.replace(rem1[i],rep)
                    #elif index > 1:
                    #    py_code.replace(py_outs[0], '')
                    #    py_outs.append(py_code)
                        #print(py_code,py_outs)
                    else: temptex = temptex.replace(rem1[0],py_code)
                    tex = temptex
            except:
                #print('except')
                rem2 = rem
                py_code = str(subprocess.check_output([python, 'temp.py'])).split("b'")[1].split("\\n'")[0].replace('\\\\', '\\').replace("\\n", "\\\\")
                #print(py_code)
                #print(py_outs)
                #print(index, py_code, py_outs)
                if py_code == "'":
                    py_code = ''
                if index != 0:
                    #print(prints)
                    if index > 1:
                        py_outs = py_code.split('\\\\')
                        #print(py_outs)
                        rep = ''
                        offset = 0
                        for i in range(index):
                            rep = ''
                            for j in range(prints[i]):
                                #print('Index, i, j:', index, i, j)
                                if j > 1: offset += 1
                                else: offset += j
                                rep = rep + py_outs[i+offset]
                                if prints[i] > 1 and j < prints[i]-1:
                                    rep = rep + ' \\\\\n'
                                    #print('extra run')
                                #print('rep', rep)
                            tex = tex.replace(rem2[i],rep)
                            #print(rem2[i])
                    #elif index > 1:
                    #    py_code.replace(py_outs[0], '')
                    #    py_outs.append(py_code)
                        #print(py_code,py_outs)
                    else: tex = tex.replace(rem2[0],py_code)
            self.progress.emit(50)
            #print(index, py_outs)
            self.progress.emit(60)
            self.progress.emit(70)
            ####
            #print(tex)
            pdf = build_pdf(tex)
            self.progress.emit(80)
            if ".tex" in fname:
                fname = fname[:len(fname) - 4]
            self.progress.emit(85)
            pdf.save_to(fname + '.pdf')
            self.progress.emit(90)
            pdfname = fname + ".pdf"
            self.progress.emit(95)
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', pdfname))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(pdfname)
            else:                                   # linux variants
                subprocess.call(('xdg-open', pdfname))
            self.progress.emit(100)
            self.finished.emit(100)
        except Exception as e:
            print(e)
            self.progress.emit(0)
            self.finished.emit(0)

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        global app_name
        global ver
        global subtitleFont
        
        self.setWindowTitle('About ' + app_name)

        QBtn = QDialogButtonBox.StandardButton.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        title = QLabel(app_name)
        title.setFont(subtitleFont)
        version = QLabel(ver)
        widgets = [title, version, self.buttonBox]
        for w in widgets:
            self.layout.addWidget(w, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)
        self.setFixedWidth(240)
        self.setFixedHeight(150)

class Commands(QWidget):
    def __init__(self):
        super().__init__()
        global titleFont
        global subtitleFont
        comFont = QFont('Courier', 16, QFont.Weight.Normal)

        layout = QVBoxLayout()
        self.setWindowTitle('Commands')
        widgets = [
            QLabel('Shorthand TeX Commands'),
            QLabel(''),
            QLabel('Text'),
            QLabel('Title:\t\t\t\t-t-'),
            QLabel('Section:\t\t\t-sec-'),
            QLabel('Subsection:\t\t\t-subsec-'),
            QLabel('Bold:\t\t\t\t-b-'),
            QLabel('Italic:\t\t\t\t-i-'),
            QLabel('Underline:\t\t\t-u-'),
            QLabel('Emphasize:\t\t\t-emph-'),
            QLabel('Unordered Lists:\t\t-ul-'),
            QLabel('Ordered Lists:\t\t\t-ol-'),
            QLabel('List Item:\t\t\t-li-'),
            QLabel('\nMath and Computation'),
            QLabel('Eqations Section:\t\t-ma-'),
            QLabel('Fraction:\t\t\t-frac-'),
            QLabel('Chemical Formula:\t\t-ce-'),
            QLabel('Python Code:\t\t\t-py-'),
            QLabel('\nMiscellaneous'),
            QLabel('Center Align:\t\t\t-center-'),
            QLabel('Include Graphics:\t\t-ig-'),
        ]
        for w in widgets:
            if widgets.index(w) == 0:
                w.setFont(titleFont)
            elif widgets.index(w) == 2 or widgets.index(w) == 13 or widgets.index(w) == 18:
                w.setFont(subtitleFont)
            else:
                w.setFont(comFont)
            layout.addWidget(w)
        self.setLayout(layout)

class Main(QMainWindow):
    work_requested = Signal(str)

    def __init__(self):
        super(Main, self).__init__()
        global temp1
        global temp2
        global app_name

        self.setWindowTitle(app_name)

        menuBar = self.menuBar()
        
        fToolbar = QMenu('&File', self)
        menuBar.addMenu(fToolbar)
        newBtn = QAction('&New', self)
        loadBtn2 = QAction('Load &Template', self)
        openBtn = QAction('&Open', self)
        saveBtn = QAction('&Save', self)
        buildBtn2 = QAction('&Build', self)
        ftools = [newBtn,loadBtn2,openBtn,saveBtn,buildBtn2]
        for tool in ftools:
            fToolbar.addAction(tool)

        hToolbar = QMenu('&Help', self)
        menuBar.addMenu(hToolbar)
        comBtn = QAction('&Commands', self)
        aboutBtn = QAction('&About', self)
        htools = [comBtn,aboutBtn]
        for tool in htools:
            hToolbar.addAction(tool)

        layout = QVBoxLayout()
        loadBtn = QPushButton('Load Template')
        self.buildBtn = QPushButton('Build')
        self.nameArea = QLineEdit()
        self.prog = QProgressBar()
        self.prog.setMaximum(100)
        self.texArea = QTextEdit()
        self.texArea.isUndoRedoEnabled()
        self.texArea.textCursor().setKeepPositionOnInsert(True)
        self.texArea.setFont(QFont('Courier'))
        widgets = [
            self.prog,
            self.texArea
        ]
        hwidgets1 = [
            loadBtn,
            self.buildBtn
        ]
        hwidgets2 = [
            QLabel('Filename:'),
            self.nameArea,
        ]
        layout1 = QHBoxLayout()
        for w in hwidgets1:
            layout1.addWidget(w)
        layout.addLayout(layout1)
        layout2 = QHBoxLayout()
        for w in hwidgets2:
            layout2.addWidget(w)
        layout.addLayout(layout2)
        for w in widgets:
            layout.addWidget(w)
        widget = QWidget()
        widget.setLayout(layout)
        widget.setMinimumSize(720,480)
        self.setCentralWidget(widget)

        newBtn.triggered.connect(self.new)
        newBtn.setShortcut('Ctrl+N')
        openBtn.triggered.connect(self.openF)
        openBtn.setShortcut('Ctrl+O')
        saveBtn.triggered.connect(self.saveTex)
        saveBtn.setShortcut('Ctrl+S')
        loadBtn.clicked.connect(self.load_temp)
        loadBtn2.triggered.connect(self.load_temp)
        loadBtn2.setShortcut('F12')
        self.buildBtn.clicked.connect(self.build)
        buildBtn2.triggered.connect(self.build)
        buildBtn2.setShortcut('F5')

        comBtn.triggered.connect(self.commands)
        comBtn.setShortcut('F1')
        aboutBtn.triggered.connect(self.about)
        aboutBtn.setShortcut('Ctrl+I')
        self.texArea.textChanged.connect(self.getTex)

    def saveTex(self, closing=False):
        try:
            global fname
            global text
            if not closing:
                fname = self.nameArea.text()
                text = self.texArea.toPlainText()
            if fname == '' or fname == ' ':
                alert = QMessageBox()
                alert.setText('No file name!')
                alert.exec()
                return False
            else:
                if '.tex' in fname: fname = fname
                else: fname = fname + '.tex'
                if os.path.exists(fname) or os.path.exists('./' + fname):
                    with open(fname, 'wt', encoding='UTF-8') as tex:
                        tex.write(text)
                else:
                    saveDiag = QFileDialog.getSaveFileName(self, 'Save File', fname, 'TeX Files(*.tex)')
                    if saveDiag[0]:
                        fname = saveDiag[0]
                        with open(fname, 'wt', encoding='UTF-8') as tex:
                            tex.write(text)
                        alert = QMessageBox()
                        alert.setText('Saved!')
                        alert.exec()
                return True
        except Exception as e:
            print(e)
            return False
            
    def new(self):
        self.nameArea.setText('')
        self.texArea.setText('')

    def openF(self):
        home_dir = ''#str(Path.home())
        fname = QFileDialog.getOpenFileName(self, 'Open file', home_dir, 'TeX Files (*.tex)')
        if fname[0]:
            f = open(fname[0], 'r')
            self.nameArea.setText(fname[0])
            with f:
                self.texArea.setText(f.read())

    def build(self):
        if self.saveTex():
            #statusBar = self.statusBar()
            #statusBar.showMessage('Building PDF', 3000)
            try:
                self.prog.setValue(0)
                self.thread = QThread(parent=self)
                self.thread.setTerminationEnabled(True)
                self.worker = BuildWorker()
                self.worker.progress.connect(self.updateProg)
                self.work_requested.connect(self.worker.run)
                self.work_requested.emit(self.texArea.toPlainText())
                self.worker.finished.connect(self.complete)
                self.worker.finished.connect(self.thread.quit)
                self.worker.finished.connect(self.worker.deleteLater)
                self.thread.finished.connect(self.thread.deleteLater)
                self.worker.moveToThread(self.thread)
                self.thread.start()
                self.thread.setPriority(QThread.Priority.HighestPriority)
            except Exception as e:
                alert = QMessageBox()
                alert.setText('Something went bad on our end!')
                alert.exec()
                print(e)

    def updateProg(self, v):
        self.buildBtn.setText('Building...')
        self.prog.setValue(v)
        QApplication.processEvents()
        if v == 100:
            self.complete()
        elif v == 0:
            self.buildBtn.setText('Build Failed!')

    def complete(self):
        self.buildBtn.setText('Build Complete!')
        self.prog.setValue(100)

    def load_temp(self):
        #print('loading...')
        if '\\documentclass' in self.texArea.toPlainText():
            alert = QMessageBox()
            alert.setText('There is already a template loaded!')
            alert.exec()
        else:
            temp = temp1 + self.texArea.toPlainText() + temp2
            self.texArea.setText(temp)

    def commands(self):
        self.comms = Commands()
        self.comms.show()

    def about(self):
        dlg = AboutDialog()
        if dlg.exec():
            print('OK')

    def getTex(self):
        shorts = {'-t-':'\\title{}','-sec-':'\\section{}','-subsec-':'\\subsection{}','-b-':'\\textbf{}','-i-':'\\textit{}','-u-':'\\underline{}','-emph-':'\\emph{}','-ul-':'\\begin{itemize}\n\\item \n\\end{itemize}','-ol-':'\\begin{enumerate}\n\\item \n\\end{enumerate}','-li-':'\\item ','-ma-':'\\begin{math}\n \n\\end{math}','-frac-':'\\frac{}{}','-ce-':'\\ce{}','-py-':'<py></py>','-ig-':'\\includegraphics{}','-center-':'\\centering '}
        tex = self.texArea.toPlainText()
        c = self.texArea.textCursor()
        a = c.anchor()
        for i in shorts:
            if i in tex:
                ls = len(i)
                lt = len(shorts[i])
                self.texArea.setText(tex.replace(i, shorts[i]))
                if '{}{}' in shorts[i]:
                    c.setPosition(a+lt-(ls+3))
                elif '{}' in shorts[i]:
                    c.setPosition(a+lt-(ls+1))
                elif '\\begin' in shorts[i]:
                    segments = shorts[i].split('\n')
                    #print(segments)
                    skip = -1
                    if '\item ' in segments or '\\item ' in segments:
                        skip -= 6
                        #print(skip)
                    for i in range(0,len(segments)-1):
                        #print(segments[i])
                        skip += len(segments[i])
                    c.setPosition(a+lt-(ls+skip))
                elif '<py>' in shorts[i]:
                    c.setPosition(a+lt-(ls+5))
                else:
                    c.setPosition(a+lt-ls)
                self.texArea.setTextCursor(c)

        """
        if '-t-' in tex:
            self.texArea.setText(tex.replace('-t-', '\\title{}'))
            c.setPosition(a+4)
            self.texArea.setTextCursor(c)
        if '-sec-' in tex:
            self.texArea.setText(tex.replace('-sec-', '\\section{}'))
            c.setPosition(a+4)
            self.texArea.setTextCursor(c)
        if '-subsec-' in tex:
            self.texArea.setText(tex.replace('-subsec-', '\\subsection{}'))
            c.setPosition(a+4)
            self.texArea.setTextCursor(c)
        if '-b-' in tex:
            self.texArea.setText(tex.replace('-b-', '\\textbf{}'))
            c.setPosition(a+5)
            self.texArea.setTextCursor(c)
        if '-i-' in tex:
            self.texArea.setText(tex.replace('-i-', '\\textit{}'))
            c.setPosition(a+5)
            self.texArea.setTextCursor(c)
        if '-u-' in tex:
            self.texArea.setText(tex.replace('-u-', '\\underline{}'))
            c.setPosition(a+8)
            self.texArea.setTextCursor(c)
        if '-emph-' in tex:
            self.texArea.setText(tex.replace('-emph-', '\\emph{}'))
            c.setPosition(a)
            self.texArea.setTextCursor(c)
        if '-ul-' in tex:
            self.texArea.setText(tex.replace('-ul-', '\\begin{itemize}\n\\item \n\\end{itemize}'))
            c.setPosition(a+18)
            self.texArea.setTextCursor(c)
        if '-ol-' in tex:
            self.texArea.setText(tex.replace('-ol-', '\\begin{enumerate}\n\\item \n\\end{enumerate}'))
            c.setPosition(a+20)
            self.texArea.setTextCursor(c)
        if '-li-' in tex:
            self.texArea.setText(tex.replace('-li-', '\\item '))
            c.setPosition(a+2)
            self.texArea.setTextCursor(c)
        if '-ma-' in tex:
            self.texArea.setText(tex.replace('-ma-', '\\begin{math}\n\n\\end{math}'))
            c.setPosition(a+9)
            self.texArea.setTextCursor(c)
        if '-frac-' in tex:
            self.texArea.setText(tex.replace('-frac-', '\\frac{}{}'))
            c.setPosition(a)
            self.texArea.setTextCursor(c)
        if '-ce-' in tex:
            self.texArea.setText(tex.replace('-ce-', '\\ce{}'))
            c.setPosition(a)
            self.texArea.setTextCursor(c)
        if '-py-' in tex:
            self.texArea.setText(tex.replace('-py-', '<py></py>'))
            c.setPosition(a)
            self.texArea.setTextCursor(c)
        if '-ig-' in tex:
            self.texArea.setText(tex.replace('-ig-', '\\includegraphics{}'))
            c.setPosition(a+13)
            self.texArea.setTextCursor(c)
        if '-center-' in tex:
            self.texArea.setText(tex.replace('-center-', '\\centering '))
            c.setPosition(a+3)
            self.texArea.setTextCursor(c)
        """

    def closeEvent(self, event):
        alert = QMessageBox().question(self, 'Save your work?', 'Would you like to save before closing?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
        if alert == QMessageBox.StandardButton.Cancel.value:
            event.ignore()
        else:
            if alert == QMessageBox.StandardButton.Yes.value:
                global fname
                fname = self.nameArea.text()
                if not fname:
                    fname = 'autosave-' + str(datetime.now().strftime('%Y%m%d-%H%M%S'))
                saved = self.saveTex(True)
                if saved:
                    event.accept()
                else:
                    alert = QMessageBox()
                    alert.setText('Save failed!')
                    alert.exec()
                    event.ignore()
            else:
                event.accept()
        #return super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #app.setStyle('macos')
    app.setApplicationName(app_name)
    app.setApplicationDisplayName(app_name)
    app.setApplicationVersion(ver)
    window = Main()
    window.show()
    sys.exit(app.exec())
