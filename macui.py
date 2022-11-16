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
from PyQt6.QtGui import QAction, QFont, QCloseEvent
from PyQt6.QtCore import QObject, QThread, pyqtSignal, Qt#, QThreadPool
from latex import build_pdf
import os, platform, subprocess
import sys
from datetime import datetime
import os

temp1 = "\\documentclass[12pt,a4paper]{article}\n\\usepackage[utf8]{inputenc}\n\\usepackage{amsmath}\n\\usepackage{amsfonts}\n\\usepackage{amssymb}\n\\usepackage{graphicx}\n\\usepackage{mhchem} \\RequirePackage{amsmath,amssymb,latexsym}\n\\author{You}\n\\title{Title}\n\\date{\\today}\n\\begin{document}\n\\maketitle\n"
temp2 = "\n\\end{document}"

fname = ''
text = ''
global prog
titleFont = QFont('Helvetica', 32, QFont.Weight.Bold)
subtitleFont = QFont('Helvetica', 20, QFont.Weight.Bold)

ver = '0.0.2-d'
app_name = 'LaTeX Maker'

class BuildWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, thread, prog, buildBtn):
        super(BuildWorker, self).__init__()
        self.m_thread = thread
        self.prog = prog
        self.buildBtn = buildBtn

    def run(self):
        global fname
        global text
        tex = text
        prog = self.prog
        try:
            self.buildBtn.setText('Building...')
            prog.setValue(10)
            while '<py>' in tex and '</py>' in tex:
                py = tex.split('<py>')[1].split('</py>')[0]
                prog.setValue(5)
                #print(py)
                temp = "<py>" + py + "</py>"
                prog.setValue(10)
                #print(py)
                with open('temp.py', 'wt', encoding='UTF-8') as tempy:
                    tempy.write(py)
                prog.setValue(20)
                python = ""
                if platform.system() == 'Darwin':       # macOS
                    python = "python3"
                elif platform.system() == 'Windows':    # Windows
                    python = "python"
                else:               
                    python = "python3"                    # linux variants
                prog.setValue(30)
                py_code = str(subprocess.check_output([python, 'temp.py'])).split("b'")[1].split("\\n'")[0].replace('\\\\', '\\').replace("\\n", "\\\\")
                prog.setValue(50)
                print(py_code)
                prog.setValue(60)
                tex = tex.replace(temp, py_code)
                prog.setValue(70)
                #win['tex'].update(tex)
            pdf = build_pdf(tex)
            prog.setValue(80)
            if ".tex" in fname:
                fname = fname[:len(fname) - 4]
            prog.setValue(85)
            pdf.save_to(fname + '.pdf')
            prog.setValue(90)
            pdfname = fname + ".pdf"
            prog.setValue(95)
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', pdfname))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(pdfname)
            else:                                   # linux variants
                subprocess.call(('xdg-open', pdfname))
            prog.setValue(100)
            self.buildBtn.setText('Build Complete!')
        except Exception as e:
            print(e)
            self.buildBtn.setText('Build Failed!')
            self.m_thread.quit()
        #if self.m_thread:
        self.m_thread.quit()

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
        prog = QProgressBar()
        self.texArea = QTextEdit()
        self.texArea.isUndoRedoEnabled()
        self.texArea.textCursor().setKeepPositionOnInsert(True)
        self.texArea.setFont(QFont('Courier'))
        widgets = [
            prog,
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

        def new():
            self.nameArea.setText('')
            self.texArea.setText('')

        def openF():
            home_dir = ''#str(Path.home())
            fname = QFileDialog.getOpenFileName(self, 'Open file', home_dir, 'TeX Files (*.tex)')
            if fname[0]:
                f = open(fname[0], 'r')
                self.nameArea.setText(fname[0])
                with f:
                    self.texArea.setText(f.read())

        def build():
            if self.saveTex():
                #statusBar = self.statusBar()
                #statusBar.showMessage('Building PDF', 3000)
                try:
                    prog.setValue(0)
                    self.thread = QThread()
                    self.thread.setTerminationEnabled(True)
                    self.worker = BuildWorker(self.thread, prog, self.buildBtn)
                    self.worker.moveToThread(self.thread)
                    self.thread.started.connect(self.worker.run)
                    self.worker.finished.connect(self.thread.quit)
                    self.worker.finished.connect(self.worker.deleteLater)
                    self.thread.finished.connect(self.thread.deleteLater)
                    self.thread.start()
                    self.thread.setPriority(QThread.Priority.HighestPriority)
                    #print(self.worker)
                    #self.buildBtn.setEnabled(False)
                    #self.thread.finished.connect(self.buildBtn.setEnabled(True))
                except Exception as e:
                    alert = QMessageBox()
                    alert.setText('Something went bad on our end!')
                    alert.exec()

        def load_temp():
            #print('loading...')
            if '\\documentclass' in self.texArea.toPlainText():
                alert = QMessageBox()
                alert.setText('There is already a template loaded!')
                alert.exec()
            else:
                temp = temp1 + self.texArea.toPlainText() + temp2
                self.texArea.setText(temp)

        def commands():
            self.comms = Commands()
            self.comms.show()

        def about():
            dlg = AboutDialog()
            if dlg.exec():
                print('OK')

        newBtn.triggered.connect(new)
        newBtn.setShortcut('Ctrl+N')
        openBtn.triggered.connect(openF)
        openBtn.setShortcut('Ctrl+O')
        saveBtn.triggered.connect(self.saveTex)
        saveBtn.setShortcut('Ctrl+S')
        loadBtn.clicked.connect(load_temp)
        loadBtn2.triggered.connect(load_temp)
        loadBtn2.setShortcut('F12')
        self.buildBtn.clicked.connect(build)
        buildBtn2.triggered.connect(build)
        buildBtn2.setShortcut('F5')

        comBtn.triggered.connect(commands)
        comBtn.setShortcut('F1')
        aboutBtn.triggered.connect(about)
        aboutBtn.setShortcut('Ctrl+I')

        def getTex():
            shorts = {'-t-':'\\title{}','-sec-':'\\section{}','-subsec-':'\\subsection{}','-b-':'\\textbf{}','-i-':'\\textit{}','-u-':'\\underline{}','-emph-':'\\emph{}','-ul-':'\\begin{itemize}\n\\item \n\\end{itemize}','-ol-':'\\begin{enumerate}\n\\item \n\\end{enumerate}','-li-':'\\item','-ma-':'\\begin{math}\n \n\\end{math}','-frac-':'\\frac{}{}','-ce-':'\\ce{}','-py-':'<py></py>','-ig-':'\\includegraphics{}','-center-':'\\centering '}
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
                    else:
                        c.setPosition(a+lt-(ls+1))
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
        self.texArea.textChanged.connect(getTex)

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