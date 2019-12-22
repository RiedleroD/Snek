import random,copy,pickle,rgraphics,os,curses,sys,math
import numpy as np
from time import time, sleep
import Snek as snek

class Network():
	def __init__(self,syns:list=[x+2 for x in reversed(range(49))]):
		self.nodes=[[0,[random.randrange(1-syns,syns)]] for y in range(syns)]
		self.nice=0
		self.lessernice=0
		self.steps=0
	def react(self,inpot:list,r:int=1):
		self.steps+=1
		for i in range(len(inpot)):
			self.nodes[i][0]=inpot[i]
		for i in range(len(self.nodes)):
			for source in self.nodes[i][1]:
				if source>=0:
					self.nodes[i][0]+=self.nodes[source][0]
				elif source<0:
					self.nodes[i][0]-=self.nodes[-source][0]
		result=[node[0] for node in self.nodes[-r:]]
		for i in range(len(self.nodes)):
			self.nodes[i][0]=0
		return result 
	def mutate(self,rate:float=0.1):
		mut=random.choices([True,False,None],[rate,100,rate//2],k=len(self.nodes))
		for i in range(len(self.nodes)):
			if mut[i]:
				self.nodes[i][1].append(random.randrange(1-len(self.nodes),len(self.nodes)))
			elif mut[i]==None and len(self.nodes[i][1])>0:
				self.nodes[i][1].pop(random.randrange(len(self.nodes[i][1])))
	def getf_cked(self,orgyattenders:list):
		if len(orgyattenders)==0:
			raise ValueError("List can't be empty")
		orgyattenders.append(self)
		whirlpool=[[perv.nodes[i][1] for perv in orgyattenders] for i in range(len(self.nodes))]
		self.nodes=[[0,random.choice(whirlpool[i])] for i in range(len(whirlpool))]

class Pool():
	def __init__(self,pop_count:int=100,elite_size:int=10,mutation_rate:float=0.1,name:str="default",network_syns:int=1024,loadin:bool=False):
		if not loadin:
			self.gen=0
			self.name=name.lower()
			self.elite_size=elite_size
			self.rate=mutation_rate
			self.pop_count=pop_count
			print("  Generating %s Neural Networks with %s synapses each"%(pop_count,network_syns))
			self.pop=[Network(network_syns) for x in range(pop_count) if print("  ",100*x//pop_count,"%",sep="",end="\r") or True]
	def evolve(self,rate:float=0.5):
		elite=[]
		self.sort()
		for x in range(self.elite_size):
			elite.append(self.pop.pop(0))
		self.pop=copy.deepcopy(elite)+self.pop
		for nw in self.pop:
			nw.mutate(rate)
		self.pop=elite+self.pop
		self.pop=self.pop[:self.pop_count]
		for nw in self.pop[-10:]:
			nw.getf_cked(elite)
		self.sort()
		for nw in self.pop:
			nw.steps=0
			nw.nice=0
		self.gen+=1
	def sort(self):
		self.pop.sort(key=self._sortbylessernice,reverse=True)
		self.pop.sort(key=self._sortbynice,reverse=True)
	def _sortbynice(self,item:Network):
		return item.nice
	def _sortbylessernice(self,item:Network):
		return item.lessernice
	def dump_best(self):
		self.pop.sort(key=self._sortbynice,reverse=True)
		with open(".best_net_"+self.name+".pkl","wb") as f:
			pickle.dump(self.pop[0],f,pickle.HIGHEST_PROTOCOL)
		
class Snek_Manager():
	def __init__(self,load_from_file:bool=True):
		print("  Initializing the pool")
		self.pool=Pool(loadin=load_from_file)
		if load_from_file:
			print("  Loading from file")
			with open(".genetic_pool.pkl","rb") as f:
				self.pool.name,self.pool.elite_size,self.pool.rate,self.pool.pop_count,self.pool.pop,self.pool.gen=pickle.load(f)
	def dump(self):
		self.pool.dump_best()
		with open(".genetic_pool.pkl","wb") as f:
			pickle.dump((self.pool.name,self.pool.elite_size,self.pool.rate,self.pool.pop_count,self.pool.pop,self.pool.gen),f,pickle.HIGHEST_PROTOCOL)
	def snek_main(self,stdscr,cycle:int):
		nearest=-99
		snek.apple=self.apple
		snek.bos=self.bos
		nw=self.pool.pop[cycle]
		while not snek.snek.dead:
			key,n1,n2=self.autokey(nw)
			snek.snek.keyfunc(key)							#steers the snek
			snek.snek.move() 								#moves the snake
			snek.snek.wrap(snek.screen) 							#wraps the edges of the screen
			snek.snek.dead=snek.snek.checkdeath(snek.snek.dots+snek.walls)	#checks if the snake dies of going into itsef or the walls
			snek.apple=snek.snek.checkapple(snek.apple)				#checks if snake eats apple and sets a new apple and lengthens the snek if true
			snek.bos=snek.snek.checkbos(snek.bos)						#handles the bottle of speed
			snek.snek.t=nw.steps/64								#calculates passed time
			snek.snek.scorecalc()							#calculates scores
			snek.snek.checkdots()
			dist=snek.getdist(snek.apple)*-1
			if dist>nearest:
				nearest=dist
			if cycle<10:
				snek.snek.drawon() 								#renders and displays all objects
				snek.draw()
				if n1>1e20:
					n1="inf"
				elif n1<-1e20:
					n1="-inf"
				else:
					n1=str(n1)
				if n2>1e20:
					n2=",inf"
				elif n2<-1e20:
					n2=",-inf"
				else:
					n2=","+str(n2)
				sys.stdout.write("\n\rNET:"+str(cycle)+"/"+str(len(self.pool.pop))+"  \n\rGEN:"+str(self.pool.gen)+"  \n\rHISC:"+str(round(self.highscore,2))+" net "+str(self.champ[1])+" in gen "+str(self.champ[0])+"     \n\rHIDI:"+str(round(nearest,2))+"   \n\r\033[2KOUT:("+n1+n2+")    ")
				if cycle==0:
					sleep(0.01)
			elif nw.steps==2:
				sys.stdout.write("\rNET:"+str(cycle)+"/"+str(len(self.pool.pop)))
			elif cycle==10 and nw.steps==1:
				sys.stdout.write("\033[4A")
			if nw.steps>64 and (snek.snek.len-2)/(nw.steps/64)<0.3:
				snek.snek.dead=True
		return nearest
	def main(self,stdscr):
		stdscr.nodelay(True)
		self.highscore=0
		self.champ=(0,0)
		while True:
			self.bos=snek.randpos()+[0]
			self.apple=snek.randpos()
			for cycle in range(len(self.pool.pop)):
				nw=self.pool.pop[cycle]
				snek.apple=self.apple
				snek.bos=self.bos
				nw.lessernice=self.snek_main(stdscr,cycle)
				nw.nice=snek.snek.score
				if snek.snek.score>self.highscore:
					self.highscore=snek.snek.score
					self.champ=(self.pool.gen,cycle)
				snek.snek=snek.Snek()
			self.pool.evolve()
			self.dump()
			
	def autokey(self,nw):
		inpot=[snek.snek.dir,snek.snek.posy,snek.snek.posx]+[coordinate for x,y in snek.snek.dots for coordinate in (x,y)]		#appends a 5x5 radius around the snake to the input
		n1,n2=nw.react(inpot,2)
		if n1<0 and n2<0:
			return 259,n1,n2			#up
		elif n1>0 and n2>0:
			return 258,n1,n2			#down
		elif n1>0 and n2<0:
			return 260,n1,n2			#left
		elif n1<0 and n2>0:
			return 261,n1,n2			#right
		else:
			return 0,n1,n2			#none
		
		
if __name__=="__main__":
	os.system("setterm -cursor off")
	if "-l" in sys.argv or "--load" in sys.argv:
		load=True
	else:
		load=False
	print("Initializing the snek manager...")
	snekman=Snek_Manager(load_from_file=load)
	try:
		print("Starting the main program")
		curses.wrapper(snekman.main)
	except KeyboardInterrupt:
		pass
	finally:
		snekman.dump()
		#rgraphics.clearscreen()
		os.system("setterm -cursor on")


