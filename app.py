#!/usr/bin/env python3
from tkinter import *
import subprocess
import threading
import time
import sys
import re
alive=1

def GetPlayerPath(path):
	return(subprocess.getoutput('dbus-send --system --print-reply --dest=org.bluez '+path+' org.freedesktop.DBus.Properties.Get string:org.bluez.MediaControl1 string:Player').split()[-1][1:-1])
def GetProperty(playerpath,property):
	t_pattern	= re.compile(r'"Title"\n'+' '*12+'variant'+16*' '+'string "(.+)"')
	d_pattern	= re.compile(r'"Duration"\n'+' '*12+'variant'+16*' '+'uint32 (\d+)')
	front		= 'dbus-send --system --print-reply --dest=org.bluez '+playerpath+' org.freedesktop.DBus.Properties.Get string:org.bluez.MediaPlayer1 string:'
	if property=='Status':
		return(subprocess.getoutput(front+property).split()[-1][1:-1])
	elif property=='Title':
		return(t_pattern.findall(subprocess.getoutput(front+'Track'))[0])
	elif property=='Duration':
		return(int(d_pattern.findall(subprocess.getoutput(front+'Track'))[0]))
	elif property=='Position':
		return(int(subprocess.getoutput(front+property).split()[-1]))
def autoupdate(app,bluez):
	try:
		while (alive):
			bluez.update()
			app.update(bluez.title,bluez.percentage)
			time.sleep(0.5)
	except:
		pass
	
class BluezMusicControl:
	def __init__(self,path):
		self.path       = path
	def update(self):
		self.playerpath = GetPlayerPath(self.path)
		self.title      = GetProperty(self.playerpath,'Title')
		self.duration   = GetProperty(self.playerpath,'Duration')
		self.position   = GetProperty(self.playerpath,'Position')
		self.status     = GetProperty(self.playerpath,'Status')
		self.percentage,self.cur_time,self.tot_time = self.notify()
	def notify(self):
		ms=int(self.duration/1000)
		m,s = (str(ms//60).zfill(2),str(ms%60).zfill(2))
		cms=int(self.position/1000)
		cm,cs = (str(cms//60).zfill(2),str(cms%60).zfill(2))
		percent=int(str(int(cms/ms*100)).zfill(2))
		cur_time=cm+":"+cs
		tot_time=m+":"+s
		return (percent,cur_time,tot_time)
	def cmd(self,act):
		subprocess.getoutput('dbus-send --system --print-reply --dest=org.bluez '+self.path+' org.bluez.MediaControl1.'+act)
	def Prev(self):
		self.cmd('Previous')
	def Next(self):
		self.cmd('Next')
	def PlayPause(self):
		if self.status=='playing':
			self.cmd('Pause')
		else :
			self.cmd('Play')

def framebox(source,side):
	frameObj = Frame(source,bg="powder blue",bd=10,borderwidth=0)
	frameObj.pack(side=side, expand=YES, fill=BOTH)
	return frameObj
def addbutton(frame,text,command=None,side=LEFT):
	buttonObj=Button(frame,text=text,command = command,relief=FLAT,bg="powder blue")
	buttonObj.pack(side=side,expand=YES,fill=BOTH)
def addplayercontrol(frame):
	addbutton(frame,"PREV",command=bluez.Prev)
	addbutton(frame,"PLAY/PAUSE",command=bluez.PlayPause)
	addbutton(frame,"NEXT",command=bluez.Next)
def addscale(frame):
	scaleObj = Scale(frame, from_=0, to=100, orient=HORIZONTAL,bg="powder blue")
	scaleObj.pack(expand=YES,fill=BOTH)
	return scaleObj

class App(Frame):
	def __init__(self):
		Frame.__init__(self)
		self.option_add('*Font','arial 10 bold')
		self.pack(expand=YES,fill=BOTH)
		self.master.title('Bluez Music Player')
		self.display = StringVar()
		entry_area=Label(self,relief=FLAT,textvariable=self.display,justify='center',bd=10,bg='powder blue')
		entry_area.pack(side=TOP,expand=YES,fill=BOTH)
		newframe=framebox(self,TOP)
		self.scale=addscale(newframe)
		newframe=framebox(self,TOP)
		addplayercontrol(newframe)
	def update(self,title,percent):
		self.display.set(title)
		self.scale.set(percent)

if __name__ == '__main__':
	bluez = BluezMusicControl(sys.argv[1])
	app=App()
	thread=threading.Thread(target=autoupdate,args=[app,bluez])
	thread.start()
	alive=app.mainloop()
