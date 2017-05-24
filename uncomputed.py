import copy
import sys
from array import array

class RealLib:
    ''' the class has basic functions to parse .real files, specifying
        quantum circuits '''
        
    def __init__(self):
        self.fname = None
        self.outfile = None
        self.delay = -1
        self.gate_count = 0
        self.quantum_cost = 0 # clarify 
        self.version = ''
        self.variables = list()
        self.inputs = list()
        self.outputs = list()
        self.constants = list()
        self.garbage = list()
        self.numvar = None
        self.circuit = list()
        self.eckt = list() # a copy for easy processing
        # each gate is specified by gateid:
        # gate type, number of inputs, varnames
        
   
    def loadReal(self,fname, outfile):
        self.fname = fname
        self.outfile = outfile
        of = open(outfile,'w')
        
        of.write('# File written by RealLib \n')
        
        f = open(self.fname)
        is_gate_line = False
        for line in f:
            if line.find('#') > 0:
                line = line[:line.find('#')]
            # comment line
            if line == '' or line == '\n':
                continue
            #line = line[:-1]
            w = line.split()
            #print(w)
            # Process the circuit description
            if is_gate_line:
                if w[0] == '.end' or line == '.end':
                    break
                
                
                # valid gate types:
                '''
                Multiple Control Toffoli gates (MCT)
                t3 a b c
                
                Multiple Control Fredkin gate (MCF)
                f2 a b
                
                Peres gate (P)
                p3 a b c
                
                V gate
                v2 a b
                
                V+ gate
                v+2 a b 
                '''
                #get gate type
                g_type = w[0][0]
                if g_type == 'v' and len(w[0]) > 1 and w[0][1] == '+':
                    g_type = 'v+'
                
                self.gate_count = self.gate_count + 1
                self.circuit.append([g_type,len(w[1:])]+w[1:])
                self.eckt.append(w)
                
            #if len(self.circuit) > 0:   
            #    print(line)
            

            # Process the preamble of the .real file
            if w[0] == '.numvars':
                self.numvar = int(w[1])
                of.write(line)
            elif w[0] == '.version':
                self.version = w[1]
                of.write(line)
            elif w[0] == '.variables':
                self.variables = w[1:]
                of.write(line)
            elif w[0] == '.inputs':
                self.inputs = w[1:]
                of.write(line)
            elif w[0] == '.outputs':
                self.outputs = w[1:]
                of.write(line)
            elif w[0] == '.constants':
                self.constants = list(w[1:])
                of.write(line)
            elif w[0] == '.garbage':
                self.garbage = list(w[1:])
                of.write(line)
            elif w[0] == '.begin':
                is_gate_line = True
                of.write(line)  



        print("ckt")    
        print(self.circuit)
        print(self.eckt)
        print(self.garbage)
        print(self.variables)
        print(self.inputs)
        print(self.outputs)
        #print(self.garbage[0][0])   
        for x in self.eckt:
            of.write(" ".join(x))
            of.write("\n")

        for x in reversed(self.eckt):
            tar = x[-1]
            ind = int(tar[1:])
            if self.garbage[0][ind] == '1':
                of.write(" ".join(x))
                of.write("\n")

        of.write(".end\n")
        of.close();

        f.close()
    
    def countGate(self):
        self.gate_count = len(self.circuit)     
        
    def computeDelay(self):
        if self.fname == None:
            print('Error: No real file loaded')
            print('Use the loadReal method to load a real file')
            sys.exit(1)
        self.compute = []
        
        considered_gates = set()
        
        for i in range(len(self.circuit)):
            #print(considered_gates)
            if i in considered_gates:
                continue
            self.compute.append(list())
            self.compute[-1].append(i)
            considered_gates.add(i)
            
            var_set = set(self.variables)
            added_var_set = set(self.circuit[i][2:])
            var_set = var_set - added_var_set
            
            if var_set == set():
                continue
                
            for j in range(i+1, len(self.circuit)):
                if j in considered_gates:
                    continue
                gate_vars = set(self.circuit[j][2:])
                if gate_vars & added_var_set == set():
                    self.compute[-1].append(j)
                    considered_gates.add(j)
                added_var_set = added_var_set | gate_vars
                var_set = var_set - gate_vars
                
                if var_set == set():
                    break
        self.delay = len(self.compute)
        print('Total delay:',self.delay)
        #print(self.compute)
        
            
           
    def writeReal(self,out_file):
        ''' writes the specified quantum circuit in .real format '''
        of = open(out_file,'w')
        
        of.write('# File written by RealLib \n')
        of.write('# Gates: '+str(self.gate_count)+'\n')
        if self.delay != -1:
            of.write('# Delay: '+str(self.delay)+'\n')
        
        of.write('.version '+self.version+'\n')
        of.write('.numvars '+str(self.numvar)+'\n')
        of.write('.variables '+(" ".join(self.variables))+'\n')
        
        of.write('.inputs '+ (" ".join(self.inputs))+'\n')
        of.write('.outputs '+ (" ".join(self.outputs))+'\n')
        if self.constants != list():
            of.write('.constants '+ ("".join(self.constants))+'\n')
        if self.garbage != list():
            of.write('.garbage '+ ("".join(self.garbage))+'\n')
        
        
        of.write('.begin\n')
        for gate in self.circuit:
            #print(gate)
            of.write(str(gate[0])+str(gate[1])+' '+(' '.join(gate[2:]))+'\n') 
        of.write('.end\n')   
            
        of.close()
    
        
def gate_summary(ckt):
    gate_dict = dict()
    for gate in ckt.circuit:
        g_type = str(gate[0])+str(gate[1])
        if g_type in gate_dict.keys():
            gate_dict[g_type] = gate_dict[g_type] + 1
        else:
            gate_dict[g_type] = 1
    return gate_dict
    

def compareReal(ckt1_fname, ckt2_fname,outputformat='ascii'):
    ckt1 = RealLib()
    ckt1.loadReal(ckt1_fname)
    ckt1.computeDelay()   
    
    ckt2 = RealLib()
    ckt2.loadReal(ckt2_fname)
    ckt2.computeDelay()   
    
    #print summary of each circuit 
    # compare delay, #gates, #types of gates
    ckt1_gates = gate_summary(ckt1)
    ckt2_gates = gate_summary(ckt2)
                      
    gate_type = list(set(ckt1_gates.keys()) | set(ckt2_gates.keys()))
    gate_type.sort()
    
    print('Circuit 1: '+ckt1.fname)
    print('Circuit 2: '+ckt2.fname)
    print('Delay    :'+ repr(ckt1.delay).rjust(5)+' | '+repr(ckt2.delay).rjust(5))
    print('Gate     :'+ repr(ckt1.gate_count).rjust(5)+' | '+repr(ckt2.gate_count).rjust(5))
    
    for g in gate_type:
        if g in ckt1_gates.keys():
            c1 = ckt1_gates[g]
        else:
            c1 = 0
            
        if g in ckt2_gates.keys():
            c2 = ckt2_gates[g]
        else:
            c2 = 0    
        print('%9s:%5d | %5d'% (g,c1,c2))
    
if __name__=='__main__':
    if len(sys.argv) < 3:
        print('python3 RealLib inputfile outputfile')
        sys.exit(0)
    ckt = RealLib()
    ckt.loadReal(sys.argv[1],sys.argv[2])
    ckt.computeDelay()
    #ckt.writeTex(sys.argv[2])
    #compareReal(sys.argv[1],sys.argv[2])
    
