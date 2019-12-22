#!usr/bin/python3
import os,sys,Genetic as gen,random
pool=gen.Pool(network_layers=[10,8,8,8,8,6,6,6,6,4,4,2,1],pop_count=20,elite_size=5)
try:
	while True:
		inpot=[float(random.randrange(0,100)) for x in range(10)]
		results=[]
		out=sum(inpot)
		for nw in pool.pop:
			a=nw.react(inpot)[0]
			nw.nice=-abs(a.n-out)
			results.append(nw.nice)
		print(100-(-100*max(results)/out),end="\r")
		pool.evolve()
	print()
finally:
	pass
