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
            elif w[0] == '.version':
                self.version = w[1]
                of.write(line)
            elif w[0] == '.variables':
                self.variables = w[1:]
            elif w[0] == '.inputs':
                self.inputs = w[1:]
            elif w[0] == '.outputs':
                self.outputs = w[1:]
            elif w[0] == '.constants':
                self.constants = list(w[1:])
            elif w[0] == '.garbage':
                self.garbage = list(w[1:])
            elif w[0] == '.begin':
                is_gate_line = True



        print("ckt")    
        print(self.circuit)
        print(self.numvar)
        print(self.eckt)
        print(self.garbage)
        print(self.variables)
        print(self.inputs)
        print(self.outputs)
        print(self.constants)
        no_garb = 0
        for val in self.garbage[0]:
            if val == '1':
                no_garb = no_garb + 1
       

        #numvars        
        of.write(".numvars ")
        self.numvar = int(self.numvar)+len(self.garbage[0]) - no_garb
        print(self.numvar)
        of.write(str(self.numvar)+"\n")

        #variables
        of.write(".variables")
        for i in range(self.numvar):
            of.write(" x"+str(i))
        of.write("\n")

        #inputs
        of.write(".inputs")
        for i in self.inputs:
            of.write(" "+i)
        for i in range(len(self.garbage[0]) - no_garb):
            of.write(" e"+str(i+1))
        of.write("\n")

        #outputs
        of.write(".outputs")
        for i in range(self.numvar - len(self.garbage[0]) + no_garb):
            of.write(" ui"+str(i))
        for i in range(len(self.garbage[0]) - no_garb):
            of.write(" o"+str(i+1))

        #constants
        of.write("\n.constants ")
        of.write(self.constants[0])
        for i in range(len(self.garbage[0]) - no_garb):
            of.write("0")

        #garbage
        #self.garbage still has original garbage list
        of.write("\n.garbage ")
        for i in range(self.numvar):
            of.write("-")

        of.write("\n.begin\n")

        #original ckt
        for i in self.eckt:
            of.write(" ".join(i)+"\n")

        #copying inputs
        #no. of outputs excluding garbage = len(self.garbage[0]) - no_garb
        #of.write("#copying inputs\n")
        no_orig_var = self.numvar - len(self.garbage[0]) + no_garb
        k = 0
        for i in range(no_orig_var):
            if self.garbage[0][i] == '-':
                of.write("t2 "+self.variables[i]+" x"+str(no_orig_var+k)+"\n")
                self.circuit.append(['t',2,self.variables[i],"x"+str(no_orig_var+k)])
                k = k+1

        #in reverse order
        #of.write("#in reverse order\n")
        for idx,x in enumerate(reversed(self.eckt)):
            self.circuit.append([x[0][0],x[0][1:]]+x[1:]) # append to the circuit for delay computation
            of.write(" ".join(x)+"\n")


        of.write(".end\n")
        of.close();
        print(self.circuit)
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
        
            
    
        
def gate_summary(ckt):
    gate_dict = dict()
    for gate in ckt.circuit:
        g_type = str(gate[0])+str(gate[1])
        if g_type in gate_dict.keys():
            gate_dict[g_type] = gate_dict[g_type] + 1
        else:
            gate_dict[g_type] = 1
    return gate_dict
    


if __name__=='__main__':
    if len(sys.argv) < 3:
        print('python3 RealLib inputfile outputfile')
        sys.exit(0)
    ckt = RealLib()
    ckt.loadReal(sys.argv[1],sys.argv[2])
    ckt.computeDelay()
    
    
