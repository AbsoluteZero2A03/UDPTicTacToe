#!/usr/bin/env python

from fltk import *
import socket, sys

class TicTacToe(Fl_Window):
	def __init__(self,x,y,w,h,label):
		self.can = False
		Fl_Window.__init__(self,x,y,w,h,label)
		self.csock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		self.BPORT=9999
		while True:
			try:
				self.csock.bind(('',self.BPORT))
				break
			except:
				self.BPORT+=1
		self.host = sys.argv[1]
		self.port = 9000 
		self.csock.sendto("INIT "+str(self.BPORT), (self.host,self.port))
		
		self.butarray = []
		
		self.begin()
		
		self.gamen_x = 5
		self.gamen_y = self.h() - 65
		self.gamen_w = self.w() - 50
		self.gamen_h = 50
		
		self.gamen = Fl_Input(self.gamen_x,self.gamen_y,self.gamen_w,self.gamen_h)
		
		self.but_w = (self.w() - 10) / 3
		self.but_h = (self.gamen_y - 8) / 3
		
		for b_y in range(3):
			for b_x in range(3):
				self.butarray.append(Fl_Button(5+b_x*self.but_w,4+b_y*self.but_h,self.but_w,self.but_h))
				self.butarray[-1].callback(self.send_g_cb)
				self.butarray[-1].deactivate()
				
		self.joiner_x = self.gamen_x+self.gamen_w+5
		self.joiner_y = self.gamen_y
		self.joiner_w = self.w() - self.joiner_x - 5
		self.joiner_h = self.gamen_h
		
		self.joiner = Fl_Button(self.joiner_x, self.joiner_y, self.joiner_w, self.joiner_h, "REQ")
		self.joiner.callback(self.send_j_cb)
		self.end()
		
		self.cfd = self.csock.fileno()
		Fl.add_fd(self.cfd,self.receive_data)
		
	def send_j_cb(self,wid):
		wid.deactivate()
		self.gamen.deactivate()
		self.csock.sendto("REQGAMENAME "+self.gamen.value(), (self.host,self.port))
	
	def send_g_cb(self,wid):
		if self.can == True:
			wid.label("X")
			self.csock.sendto("GAMEMOVE "+self.gamename+"\t"+str(self.butarray.index(wid)),(self.host,self.port))
			self.can = False
		
	def receive_data(self,fd):
		self.data,self.d=self.csock.recvfrom(65536)
		print self.data
		if self.data in ["YES", "NO"]:
			if self.data=="NO":
				self.csock.sendto("INITGAME "+self.gamen.value(),(self.host,self.port))
			self.csock.sendto("JOINGAME "+self.gamen.value(),(self.host,self.port))
			self.gamename = self.gamen.value()
		if ' '.join(self.data.split(' ')[:2]) == "JOINED GAME":
			if self.data.split(' ')[2] == '0':
				self.can = True
			else:
				self.can = False
			for b in self.butarray:
				b.activate()
		if self.data == "GAME FULL":
			self.gamen.activate()
			self.joiner.activate()
			self.gamename=""
		if self.data == 'GAMESTART':
			self.can = True
		if self.data.split(' ')[0] == 'MOVE':
			self.num = int(self.data.split(' ')[1])
			#if self.butarray[self.num].label() == "":
			self.butarray[self.num].label("O")
			self.butarray[self.num].redraw()
			self.butarray[self.num].deactivate()
			self.can = True
	def __del__(self):
		if Fl_Window is not None:
			Fl_Window.__del__(self)
		self.csock.close()
		

a = TicTacToe(2,2,512,512,"a")
a.show()
Fl.run()
