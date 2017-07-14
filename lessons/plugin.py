from builtins import object
# -*- coding: utf-8 -*-

import os
import webbrowser
import shutil

from qgis.PyQt.QtCore import Qt, QDir
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon

from qgis.core import QgsApplication

from qgiscommons.gui import (addAboutMenu,
                             removeAboutMenu,
                             addHelpMenu,
                             removeHelpMenu)

import lessons
from lessons.lessonwidget import LessonWidget
from lessons.lessonselector import LessonSelector
from lessons.utils import execute

class LessonsPlugin(object):

    def __init__(self, iface):
        self.iface = iface

        # add tests to test plugin
        try:
            from qgistester.tests import addTestModule
            from lessons.test import testerplugin
            addTestModule(testerplugin, "Lessons")
        except Exception as e:
            pass

        self.lessonWidget = None

    def unload(self):
        self.iface.removePluginMenu("Lessons", self.action)
        del self.action

        removeHelpMenu("Lessons")
        removeAboutMenu("Lessons")

        tempDir = os.path.join(QDir.tempPath(), 'lessons' , 'lesson')
        if QDir(tempDir).exists():
            shutil.rmtree(tempDir, True)

        try:
            from qgistester.tests import removeTestModule
            from lessons.test import testerplugin
            removeTestModule(testerplugin, "Lessons")
        except Exception as e:
            pass

    def initGui(self):
        lessonIcon = QIcon(os.path.dirname(__file__) + '/lesson.gif')
        self.action = QAction(lessonIcon, "Open Lessons Library...", self.iface.mainWindow())
        self.action.triggered.connect(self.start)
        self.iface.addPluginToMenu("Lessons", self.action)

        addHelpMenu("Lessons")
        addAboutMenu("Lessons")

        self.lessonwidget = None

        lessons.loadLessons()


    def start(self):
        if self.lessonWidget is not None:
            QMessageBox.warning(self.iface.mainWindow(), "Lesson", "A lesson is currently being run")
            return
        dlg = LessonSelector()
        dlg.exec_()
        if dlg.lesson:
            self.lessonWidget = LessonWidget(dlg.lesson)
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.lessonWidget)
            def lessonFinished():
                self.lessonWidget = None
                execute(dlg.lesson.cleanup)
            self.lessonWidget.lessonFinished.connect(lessonFinished)
