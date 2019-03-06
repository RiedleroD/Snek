#!/usr/bin/python3.7
"""A renderer with almost no dependencies which draws directly into the shell"""
__authors__		=	["Riedler"]
__copyright__		=	"Copyright 2019, Riedler"
__credits__		=	["Riedler","Philip Damianik"]
__license__		=	"CC"
__version__		=	"0.03a"
__maintainer__		=	"Riedler"
__status__		=	"Development"
import os
import sys
import time
import asyncio
from contextlib import suppress
if os.name=="nt":
	import colorama
	colorama.init()
	def clearscreen():
		os.system("cls")
else:
	def clearscreen():
		os.system("clear")

										#COLOR
class color():
	def __init__(self):
		self.bck="\033[30m"
		self.red="\033[31m"
		self.grn="\033[32m"
		self.yel="\033[33m"
		self.bue="\033[34m"
		self.mag="\033[35m"
		self.cyn="\033[36m"
		self.wht="\033[37m"
		self.rst="\033[0m"
colr=color()
										#SHADES
class shades():
	def __init__(self):
		self.a="██"
		self.b="▓▓"
		self.c="▒▒"
		self.d="░░"
		self.e="  "
shds=shades()
										#GRAPHIC
class graphic():
	def __init__(self):
		self.posx=0
		self.posy=0
		self.speedx=0
		self.speedy=0
		self.content=[]
		self.bg=""
		self.prevcontent=[]
		self.hitbox=[]
	def init(self,width,height,bg=shds.a,warning=True):
		self.bg=bg
		for row in range(height):
			precontent=[]
			nonearray=[]
			for col in range(width):
				precontent.append(self.bg)
				nonearray.append(None)
			self.content.append(precontent)
			self.prevcontent.append(nonearray)
			self.hitbox.append(nonearray)
		rows, columns=os.popen('stty size', 'r').read().split()
		while int(rows)<height or int(columns)<width:
			sys.stdout.write("You need an output that's "+str(width*3)+"x"+str(height)+" big, but it's only "+columns+"x"+rows+" big.\r")
			sys.stdout.flush()
			rows, columns=os.popen('stty size', 'r').read().split()
	def display(self):
		try:
			bg=self.bg
			for row in range(len(self.content)):
				rowstr=str(row+1)+";"
				rowcontent=self.content[row]
				for col in range(len(rowcontent)):
					if rowcontent[col]!=self.prevcontent[row][col]:
						position="\033["+rowstr+str((col*2)+1)+"H"
						sys.stdout.write(colr.rst+position+rowcontent[col]+colr.rst)
						self.prevcontent[row][col]=rowcontent[col]
					self.content[row][col]=bg
			sys.stdout.flush()
		except KeyboardInterrupt:
			clearscreen()
			quit()	
	def stayin(self,other,type=0):
		try:
			x=self.posx
			y=self.posy
			w=len(self.content)
			h=len(self.content[0])
			ow=len(other.content)
			oh=len(other.content[0])
			o=oh-h
			o2=ow-w
			if type==0:
				if x<1:
					self.posx=1
				elif x>o:
					self.posx=o
				if y<1:
					self.posy=1
				elif y>o2:
					self.posy=o2
			elif type==1:
				if x<1:
					self.posx=2
					self.speedx*=-1
				elif x>o:
					self.posx=o-1
					self.speedx*=-1
				if y<1:
					self.posy=2
					self.speedy*=-1
				elif y>o2:
					self.posy=o2-1
					self.speedy*=-1
			else:
				raise ValueError("Wrong stayin type")
		except KeyboardInterrupt:
			clearscreen()
			quit()
	async def displayloop(self,maxfps=60):		
		task = asyncio.Task(self.raw_displayloop(maxfps))
		task.cancel()
		with suppress(asyncio.CancelledError):
			await task
	async def raw_displayloop(self,maxfps):
		f=fpslimiter()
		f.maxfps=maxfps
		while True:
			f.start()
			for item in self.drawpile:
				self.draw(item)
			self.display()
			f.end()
	def draw(other,self,noerr=False):
		try:
			posx=self.posx
			precontent=other.content
			for row in range(len(self.content)):
				newrow=row+self.posy
				rowcontent=self.content[row]
				for col in range(len(rowcontent)):
					if self.content[row][col] not in ["",None,'']:
						precontent[newrow][col+posx]=rowcontent[col]
			other.content=precontent
		except KeyboardInterrupt:
			clearscreen()
			quit()
		except:
			if noerr==False:
				raise ValueError("Failed to draw on object. self.position:"+str(self.posx)+"x"+str(self.posy)+", self.size: "+str(len(self.content))+"x"+str(len(self.content[0]))+", other.size: "+str(len(other.content))+"x"+str(len(other.content[0])))
	def move(self):
		try:
			self.posx+=self.speedx
			self.posy+=self.speedy
		except KeyboardInterrupt:
			clearscreen()
			quit()
	def collideswith(self,other):
		collision=None
		for x in range(len(self.hitbox)):
			for y in range(len(other.hitbox)):
				if self.posx+x==other.posx+y:
					collision=False
		if collision==None:
			return False
		else:
			for x in range(len(self.hitbox[0])):
				for y in range(len(other.hitbox[0])):
					if self.posx+x==other.posx+y:
						collision=True
		return collision
class fpslimiter():
	def __init__(self):
		self.fps=0
		self.maxfps=60
		self.time=time.time()
	def start(self):
		self.time=time.time()
	def end(self):
		try:
			mintime=1/self.maxfps
			t=self.time+mintime
			while time.time()<t:
				pass
			return 1/(time.time()-self.time)
		except KeyboardInterrupt:
			clearscreen()
			quit()
# ¢: ← If you need help, please torture this deamon.
