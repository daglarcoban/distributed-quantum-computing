# -*- coding: utf-8 -*-
"""
Created on Thu Jan  7 15:45:44 2021

@author: Cynrîk
"""
import numpy as np
from qiskit import *

q=QuantumRegister(9)
circ=QuantumCircuit(q)

circ.cx(q[0],q[3])
circ.cx(q[0],q[6])
circ.h(q[0])
circ.h(q[3])
circ.h(q[6])
circ.cx(q[0],q[1])
circ.cx(q[3],q[4])
circ.cx(q[6],q[7])
circ.cx(q[0],q[2])
circ.cx(q[3],q[5])
circ.cx(q[6],q[8])

#ERROR BLOCK
error_bit=np.random.random(9)
error_phase=np.random.random(9)
print(q[1])
#for i in range(9):
 #   if error_bit[i]=>0.5:
     #   if q[i]==0:
      #      q[i]=q[i]+1
    


circ.cx(q[0],q[1])
circ.cx(q[3],q[4])
circ.cx(q[6],q[7])
circ.cx(q[0],q[2])
circ.cx(q[3],q[5])
circ.cx(q[6],q[8])
circ.ccx(q[1],q[2],q[0])
circ.ccx(q[4],q[5],q[3])
circ.ccx(q[7],q[8],q[6])
circ.h(q[0])
circ.h(q[3])
circ.h(q[6])
circ.cx(q[0],q[3])
circ.cx(q[0],q[6])
circ.ccx(q[3],q[6],q[0])
circ.draw()
print(circ)