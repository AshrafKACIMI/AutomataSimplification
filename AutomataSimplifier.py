# -*-coding:utf8 -*
import pydot
import os
import copy

class Automate:
    def __init__(self):
        self.instructions=[]  #liste des instructions
        self.etats=[]    #liste des etats
        self.alphabet=[] #ensemble de mots
        self.alt=1  #le numero de l'etat intermediaire à creer
        self.table=[]  #table de transition
        self.vgraph=pydot.Dot(graph_type='digraph', strict = True)

    def __repr__(self):
        return self.instructions.__repr__()

    def lecture(self):
        nb=int(raw_input("Donner le nombre d'etats"))   #lecture du nombre d'etats
        print nb
        etats=[Etat("S"+str(i), False) for i in xrange(nb)]  #génère une liste d'états nommés S0, S1, .... et non finaux
        print "Donner les numeros des etats finaux (entre 0 et {} separés par des espaces)".format(nb-1) #lecture des numeros des etats finaux
        s=raw_input().split()
        print s
        for i in s:
            etats[int(i)].isFinal=True   #mettre l'attribut isFinal à True pour les etats finaux lus
        self.etats=etats
        print self.etats
        print "Donner les instructions sous la forme 'etat1 mot etat2' ou # quand vous aurez terminé"
        s=raw_input(">>")
        while s!="#":  # le # est le caractère d'arrêt de la lecture
            s=s.split()
            I=Instruction(self.get_state(s[0]), s[1], self.get_state(s[2]))
            if I not in self.instructions:
                self.instructions.append(I)  #on insère l'instruction dans la liste
            if I.mot not in self.alphabet:
                self.alphabet.append(I.mot)
            s=raw_input(">>")

    def creer_vgraph(self):
        self.vgraph=pydot.Dot(graph_type='digraph', strict = True)
        for e in self.etats:
            if e.isFinal:
                e.node.shape="doubledcircle"
            self.vgraph.add_node(e.node)
        for ins in self.instructions:
            self.vgraph.add_edge(ins.edge)
        
    def get_line(self, etat):  #renvoie la position de etat dans la liste d'etats
        for i in xrange(len((self.etats))):
            if self.etats[i].nom==etat.nom:
                return i
    
    def get_column(self, c): #renvoie la position de c dans l'alphabet
        for i in xrange(len((self.alphabet))):
            if self.alphabet[i]==c:
                return i
      
    def creer_table(self): # crée la table de transitions à partir des etats, instructions et l'alphabet
        self.table=[[ [] for c in self.alphabet] for e in self.etats ] #génère une matrice de listes vides
        for ins in self.instructions:
            self.table[self.get_line(ins.debut)][self.get_column(ins.mot)].append(ins.fin)
        self.print_table()
                
    def print_table(self):
        for i in xrange(len(self.etats)):
            print self.etats[i], self.table[i]
        
    def get_state(self, s):
        l=self.etats
        for e in l:
            if e.nom==s:
                return e
    

    def pseudo_simple(self):
        for ins in self.instructions:
            if len(ins.mot)>1:
                self.instructions+=ins.inst_simple(self.alt)
                self.alt+=len(ins.mot)-1
        for ins in self.instructions:
            if not ins.debut in self.etats:
                self.etats.append(ins.debut)
            if not ins.fin in self.etats:
                self.etats.append(ins.fin)
            if len(ins.mot)>1:
                if ins.mot in self.alphabet:
                    self.alphabet.remove(ins.mot)
                self.instructions.remove(ins)
            else:
                if not ins.mot in self.alphabet and ins.mot!="/":
                        self.alphabet.append(ins.mot)
        for ins in self.instructions:
            if not ins.debut in self.etats:
                self.etats.append(ins.debut)
            if not ins.fin in self.etats:
                self.etats.append(ins.fin)
            if len(ins.mot)>1:
                if ins.mot in self.alphabet:
                    self.alphabet.remove(ins.mot)
                self.instructions.remove(ins)
            else:
                if not ins.mot in self.alphabet and ins.mot!="/":
                        self.alphabet.append(ins.mot)
        self.alphabet.sort()
        self.etats.sort()
        if "/" in self.alphabet:
            self.alphabet.remove("/")
        self.alphabet=["/"]+self.alphabet
        print self.alphabet
        print self.etats
    
    def table_to_inst(self):
        return [Instruction(self.etats[i], self.alphabet[j], e) for i in range(len(self.etats)) for j in range(len(self.alphabet)) for e in self.table[i][j] if (len(self.table[i][j])>0)]
                        
    def simple(self):
        for i in range(len(self.etats)):
            for e in self.table[i][0]:
                if e.isFinal:
                    self.etats[i].isFinal=True
                for j in range(1, len(self.alphabet)):
                    for etat in self.table[self.get_line(e)][j]:
                        if etat not in self.table[i][j]:
                            self.table[i][j].append(etat)
            self.table[i][0]=[]
        self.instructions=self.table_to_inst()
                    


class Instruction:
    def __init__(self, debut, mot, fin):
        self.debut=debut
        self.mot=mot
        self.fin=fin
        self.edge=None
        if mot != "/":
            self.edge=pydot.Edge(debut.node, fin.node, label=mot)
        else:
            self.edge=pydot.Edge(debut.node, fin.node, label="ε")

    def inst_simple(self, n):
        l=[]
        l.append(Instruction(self.debut,self.mot[0],Etat("S'"+str(n), False)))
        n+=1
        for c in self.mot[1:-1]:
            l.append(Instruction(Etat("S'"+str(n-1), False), c, Etat("S'"+str(n), False)))
            n+=1
        l.append(Instruction(Etat("S'"+str(n-1), False), self.mot[-1], self.fin))
        n+=1
        return l

    def __repr__(self):
        return self.debut.__repr__()+" "+self.mot.__repr__()+" "+self.fin.__repr__()
    def __eq__(self, other):
        try:
            return (self.debut==other.debut) and (self.fin==other.fin) and (self.mot == other.mot)
        except AttributeError:
            return False


class Etat:
    def __init__(self, s, isF):
        self.nom=s
        self.isFinal=isF
        self.node=pydot.Node(s,style="filled")

    def __repr__(self):
        return self.nom+"f" if self.isFinal else self.nom
      
    def __cmp__(self, other):
        if  "'" not in self.nom and "'" in other.nom:
            return -1
        if "'" in self.nom and "'" not in other.nom:
            return +1
        if "'" in self.nom and "'" in other.nom:
            return 1 if self.nom[2:]>other.nom[2:] else -1
        if "'" not in self.nom and "'" not in other.nom:
            return 1 if self.nom > other.nom else -1
    
        
    def __eq__(self, other):
        try:
            return (self.nom==other.nom) and (self.isFinal==other.isFinal)
        except AttributeError:
            return False


B=Automate()
B.lecture()
B.creer_vgraph()
B.vgraph.write_png("L'automate lu A.png")
os.system("L'automate lu A.png")
A=copy.deepcopy(B)
A.pseudo_simple()
A.creer_vgraph()
A.vgraph.write_png("l'automate pseudo simple.png")
os.system("l'automate pseudo simple.png")
A.creer_table()
A.simple()
A.creer_vgraph()
A.vgraph.write_png("l'automate simple.png")
os.system("l'automate simple.png")
print A.alphabet
print A.instructions
print A.print_table()
raw_input()
