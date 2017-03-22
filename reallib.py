import copy
import sys

class RealLib:
    ''' the class has basic functions to parse .real files, specifying
        quantum circuits '''
        
    def __init__(self):
        self.fname = None
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
        # each gate is specified by gateid:
        # gate type, number of inputs, varnames
        
   
    def loadReal(self,fname):
        self.fname = fname
        
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
                
            #if len(self.circuit) > 0:   
            #    print(line)
                
            #print(self.circuit)    
            # Process the preamble of the .real file
            if w[0] == '.numvars':
                self.numvar = int(w[1])
            elif w[0] == '.version':
                self.version = w[1]
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
    
    def writeTex(self,outfile,framed = False):
        ''' writes the specified quantum circuit in .tex format '''
        if framed:
            frame = "framed,background rectangle/.style={double,ultra thick,draw,rounded corners},thick"
        else:
            frame = ''
        header = '\\documentclass{standalone} \n \
        \\usepackage{graphicx} \n \
\\usepackage[hang,small,bf]{caption}    % fancy captions\n \
\\usepackage{tikz}	\n\n\
% TikZ libraries \n\
\\usetikzlibrary{shapes,snakes} \n\
\\usetikzlibrary{backgrounds,fit,decorations.pathreplacing} \n \
\\usetikzlibrary{shapes,arrows,fit,calc,positioning,automata} \n\
\\newcommand{\\ket}[1]{\\ensuremath{\\left|#1\\right\\rangle}} % Dirac Kets \n\
\\begin{document} \n\
    %\\begin{figure} \n\
    %\\centerline{ \n\
        \\begin{tikzpicture}['+frame+'] \n\
            \\tikzset{oplus/.style={path picture={% \n\
            \\draw[black] \n\
            (path picture bounding box.south) -- (path picture bounding box.north) \n\
            (path picture bounding box.west) -- (path picture bounding box.east);\n\
            }}}\n\
             \\tikzstyle{operator} = [draw,fill=white,minimum size=1.5em] \n\
             \\tikzstyle{phase} = [fill,shape=circle,minimum size=4pt,inner sep=0pt]\n\
             \\tikzstyle{surround} = [fill=blue!10,thick,draw=black,rounded corners=2mm]\n\
             \\tikzstyle{swap} = [draw,fill,shape=cross out,minimum size=5pt,inner sep=0pt]\n\
             \\tikzstyle{cnot} = [oplus,draw,thick,circle,minimum size = 12pt]'
        
        prefix = '\t\t'           
        outf = open(outfile,'w')
        outf.write(header)
        outf.write(prefix+'% Qubit\n')
        col = 0
        pos_dict = dict()
        last_point_dict = dict()
        sep = -0.5 # qubit line separatation
        
        for i in range(len(self.variables)):
            last_point_dict[i] = '(q'+str(col)+'_'+str(i)+')'
            outf.write(prefix+'\\node at ('+str(col)+','+str(i*sep)+')' + last_point_dict[i]+' {\\ket{'+str(self.variables[i])+'}};\n')  
            pos_dict[self.variables[i]] = i
        gate_sep = 0.5 # gate separation
        col_pos = 0.5
        for gate in self.circuit:
            col = col + 1
            col_pos = col_pos + gate_sep
            print(gate)
            outf.write(prefix+'% Gate '+str(col)+'\n')
            lines_active = list()
            for i in range(len(gate[2:])):
                var = gate[i+2]
                print(i,len(gate[2:])-1)
                new_point = '(q'+str(col)+'_'+str(pos_dict[var])+')'
                lines_active.append(pos_dict[var])
                loc = '('+str(col_pos)+','+str(sep*pos_dict[var])+')'
                if gate[0] == 'f' and i >= len(gate[2:])-2:
                    outf.write(prefix+'\\node[swap] '+ new_point+' at '+loc+ ' {} edge [-] '+ last_point_dict[pos_dict[var]]+';\n')
                elif i == len(gate[2:])-1 :
                    if gate[0] == 't':
                        outf.write(prefix+'\\node[cnot] '+ new_point+' at '+loc+ ' {} edge [-] '+ last_point_dict[pos_dict[var]]+';\n')
                    elif gate[0] == 'v':
                        outf.write(prefix+'\\node[operator] '+ new_point+' at '+loc+ ' {V} edge [-] '+ last_point_dict[pos_dict[var]]+';\n')
                    elif gate[0] == 'v+':
                        outf.write(prefix+'\\node[operator] '+ new_point+' at '+loc+ ' {V+} edge [-] '+ last_point_dict[pos_dict[var]]+';\n')
                else:
                    outf.write(prefix+'\\node[phase] '+ new_point+' at '+loc+ ' {} edge [-] '+ last_point_dict[pos_dict[var]]+';\n')
                last_point_dict[pos_dict[var]] = new_point
            
            lines_active.sort()
            for i in range(len(lines_active)-1):
                source = '(q'+str(col)+'_'+str(lines_active[i])+')'
                dest   = '(q'+str(col)+'_'+str(lines_active[i+1])+')'
                outf.write(prefix+'\\draw[-] '+source+'  -- '+dest+';\n')
                
               
        outf.write(prefix+'% Output\n')
        col = col + 1
        col_pos = col_pos + 2*gate_sep
        for i in range(len(self.outputs)):     
            out_var = '(q'+str(col)+'_'+str(i)+')'
            outf.write(prefix+'\\node at ('+str(col_pos)+','+str(i*sep)+')' + out_var+' {\\ket{'+str(self.outputs[i])+'}};\n')   
            source =  '(q0_'+str(i)+')' 
            outf.write(prefix+'\\draw[-] '+source+'  -- '+out_var+';\n')
        footer = '\t\t\\end{tikzpicture} \n \
  %}\n\
%\\end{figure}\n\
\end{document}\n'
        outf.write(footer)
        outf.close()
        
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
    ckt.loadReal(sys.argv[1])
    ckt.computeDelay()
    ckt.writeTex(sys.argv[2])
    #compareReal(sys.argv[1],sys.argv[2])
    
