#! /Library/Frameworks/Python.framework/Versions/3.4/bin/python3 -u
import curses
from time import sleep
from random import randint
DEBUG = 0
SLEEPTIMER = 0

if DEBUG==2:
    ddprint = print
else:
    def ddprint(*x):
        return 0

if DEBUG:
    dprint = print
else:
    def dprint(*x):
        return 0

class Bear:
    def __init__(self, row, col, index):
        self.index = index
        self.row = row
        self.col = col
        self.age = 0
        self.maws = 0
    def step(self, F):
        locations = F.adjacentcoords(self.row,self.col)
        return locations[randint(0,len(locations)-1)]
    def wander(self, F):
        ddprint("-- Bear",self,"wandering from",self.row,self.col)
        self.age += 1
        fail = 0
        for i in range(5):
            oldrow = self.row
            oldcol = self.col
            ddprint("---0",i)
            p = self.step(F)
            ddprint("----",p)
            if F.nobear(p[0],p[1]):
                ddprint("---1")
                L = F.getlumberjack(p[0],p[1])
                self.row = p[0]
                self.col = p[1]
                F.grid[oldrow][oldcol].remove(self)
                F.grid[p[0]][p[1]].add(self)
                ddprint("---- now at",p)
                if L:
                    ddprint("---2")
                    self.maw(L, F)
                    break
            elif fail:
                ddprint("---3")
                break
            else:
                ddprint("---4")
                fail = 1
                continue
        return
    def maw(self, L, F):
        self.maws += 1
        F.mawcount += 1
        F.removelumberjack(L.row, L.col)
        if not F.lumberjacks:
            F.addrandomlumberjack()
        return

class Lumberjack:
    def __init__(self, row, col, index):
        self.index = index
        self.row = row
        self.col = col
        self.age = 0
        self.chops = 0
    def step(self, F):
        locations = F.adjacentcoords(self.row,self.col)
        return locations[randint(0,len(locations)-1)]
    def wander(self, F):
        ddprint("-- Lumberjack",self,"wandering from",self.row,self.col)
        self.age += 1
        fail = 0
        for i in range(3):
            oldrow = self.row
            oldcol = self.col
            ddprint("---0",i)
            p = self.step(F)
            ddprint("----",p)
            T = F.gettree(p[0],p[1])
            fire = False
            if T and T.status == 3:
                fire = True
            if F.nolumberjack(p[0],p[1]) and F.nobear(p[0],p[1]) and not fire:
                ddprint("---1")
                self.row = p[0]
                self.col = p[1]
                F.grid[oldrow][oldcol].remove(self)
                F.grid[p[0]][p[1]].add(self)
                ddprint("---- now at",p)
                if T and T.status and T.status != 3:
                    ddprint("---2")
                    self.chop(T, F)
                    break
            elif fail:
                ddprint("---3")
                break
            else:
                ddprint("---4")
                fail = 1
                continue
        return
    def chop(self, T, F):
        self.chops += 1
        F.choptree(T.row, T.col)
        return


class Tree:
    def __init__(self, row, col, index):
        self.index = index
        self.row = row
        self.col = col
        self.age = 0
        self.status = 0 #0 sapling, 1 tree, 2 elder, 3 ON FIRE
    def grow(self, F):
        self.age += 1
        ddprint("--Aging", self, "to age", self.age)
        if self.status == 3:
            return
        if self.age < 12:
            self.status = 0
        elif self.age < 120:
            self.status = 1
        else:
            self.status = 2
    def symbol(self):
        if self.status == 0:
            return "s"
        elif self.status == 1:
            return "t"
        elif self.status == 2:
            return "T"
        else:
            return "&"
    def plant(self, F):
        coords = 0
        if self.status == 3:
            return 0
        if self.status:
            L = F.adjacenttreeless(self.row,self.col)
            dprint("---",L)
            if L and randint(1,10//self.status)==1:
                coords = L[randint(0,len(L)-1)]
        return coords
    def catchfire(self):
        self.status = 3
        return


class Forest:
    def __init__(self, N):
        self.TREEINDEX = 0
        self.LUMBERJACKINDEX = 0
        self.BEARINDEX = 0
        self.saplingcount = 0
        self.chopcount = 0
        self.mawcount = 0
        self.month = 0
        self.year = 0
        self.grid = []
        self.bears = dict()
        self.lumberjacks = dict()
        self.trees = dict()
        self.size = N
        self.empty_char = " "
        self._scale = "  "
        for x in range(N):
            self.grid.append([])
            for y in range(N):
                self.grid[x].append(set())
            self._scale = self._scale + "{:2}".format(x)
        dprint("--Forest of size",N,"created")
    def symbol(self, row, col):
        s1 = self.gettree(row,col)
        s2 = self.getlumberjack(row,col)
        s3 = self.getbear(row,col)
        if s3:
            return "B"
        if s2:
            if s2.age < 120:
                return "L"
            else:
                return "X"
        if s1:
            return s1.symbol()
        return self.empty_char
    def draw(self):
        dprint("--Drawing Forest")
        rs = "Month " + str(self.month) + "\n"
        rs = rs + self._scale + "\n"
        i = 0
        for row in self.grid:
            rs = rs + "{:2}".format(i) + " "
            j = 0
            for col in row:
                s = self.symbol(i,j)
                rs = rs+self.symbol(i,j)+" "
                j += 1
            rs = rs + "\n"
            i += 1
        return rs
    def newbear(self, row, col):
        i = self.BEARINDEX
        self.bears[i] = Bear(row, col, i)
        self.grid[row][col].add(self.bears[i])
        dprint("--Bear placed at row",row,"col",col,"index",i)
        self.BEARINDEX += 1
    def newlumberjack(self, row, col):
        i = self.LUMBERJACKINDEX
        self.lumberjacks[i] = Lumberjack(row, col, i)
        self.grid[row][col].add(self.lumberjacks[i])
        dprint("--Lumberjack placed at row",row,"col",col,"index",i)
        self.LUMBERJACKINDEX += 1
    def newtree(self, row, col):
        i = self.TREEINDEX
        self.trees[i] = Tree(row, col, i)
        self.grid[row][col].add(self.trees[i])
        dprint("--Tree placed at row",row,"col",col,"index",i)
        self.TREEINDEX += 1
    def removebear(self, row, col):
        dprint("--Removing bear at row",row,"col",col)
        B = self.getbear(row,col)
        del self.bears[B.index]
        self.grid[row][col].remove(B)
    def removelumberjack(self, row, col):
        dprint("--Removing lumberjack at row",row,"col",col)
        L = self.getlumberjack(row,col)
        del self.lumberjacks[L.index]
        self.grid[row][col].remove(L)
    def choptree(self, row, col):
        dprint("--Chopping tree at row",row,"col",col)
        T = self.gettree(row,col)
        if T.status == 1:
            self.chopcount += 1
        elif T.status == 2:
            self.chopcount += 2
        del self.trees[T.index]
        self.grid[row][col].remove(T)
    def adjacentcoords(self,row,col):
        L = []
        for x in range(-1,2):
            for y in range(-1,2):
                if x or y:
                    r = row + x
                    c = col + y
                    if r >= 0 and r < self.size:
                        if c >= 0 and c < self.size:
                            L.append((r,c))
        return L
    def adjacentbearless(self,row,col):
        coords = self.adjacentcoords(row,col)
        B = []
        for coord in coords:
            if self.nobear(coord[0],coord[1]):
                B.append(coord)
        return B
    def adjacentlumberjackless(self,row,col):
        coords = self.adjacentcoords(row,col)
        L = []
        for coord in coords:
            if self.nolumberjack(coord[0],coord[1]):
                L.append(coord)
        return L
    def adjacenttreeless(self,row,col):
        coords = self.adjacentcoords(row,col)
        T = []
        for coord in coords:
            if self.notree(coord[0],coord[1]):
                T.append(coord)
        return T
    def firestart(self):
        fs = []
        for row in range(1,self.size):
            for col in range(1,self.size):
                if not self.notree(row,col):
                    if not self.adjacenttreeless(row,col):
                        if not randint(0,999): #Chance of a random fire starting
                            fs.append((row,col))
        return fs
    def firecoords(self,row,col):
        L = []
        for x in range(-1,2):
            for y in range(-1,2):
                if (x or y) and not (x and y):
                    r = row + x
                    c = col + y
                    if r >= 0 and r < self.size:
                        if c >= 0 and c < self.size:
                            L.append((r,c))
        return L
    def tick(self):
        self.month += 1
        dprint("--Tick", self.month)
        dprint("--Tree Count", len(self.trees))
        P = set()
        burncandidates = []
        chopcandidates = []
        for T in self.trees.values():
            T.grow(self)
            if T.status == 3:
                if not randint(0,4): #Chance of tree burning down
                    chopcandidates.append(T)
                L = self.firecoords(T.row, T.col)
                for coords in L:
                    Tprime = self.gettree(coords[0],coords[1])
                    if Tprime:
                        burncandidates.append(Tprime)
            else:
                p = T.plant(self)
                if p:
                    P.add(p)
        dprint("----",P)
        for tree in chopcandidates:
            self.choptree(tree.row,tree.col)
        for coords in P:
            self.newtree(coords[0],coords[1])
            self.saplingcount += 1
        for L in self.lumberjacks.values():
            L.wander(self)
        for B in self.bears.values():
            B.wander(self)
        for fire in self.firestart():
            T = self.gettree(fire[0],fire[1])
            T.catchfire()
        for victim in burncandidates:
            if not randint(0,3): #Chance of passing fire on
                victim.catchfire()
        rs = ""
        if not self.month % 12:
            rs = self.yearly()
        return rs
    def removerandombear(self):
        bears = list(self.bears.keys())
        bearindex = bears[randint(0,len(bears)-1)]
        B = self.bears[bearindex]
        self.grid[B.row][B.col].remove(B)
        del self.bears[bearindex]
    def removerandomlumberjack(self):
        lumberjacks = list(self.lumberjacks.keys())
        lumberjackindex = lumberjacks[randint(0,len(lumberjacks)-1)]
        L = self.lumberjacks[lumberjackindex]
        self.grid[L.row][L.col].remove(L)
        del self.lumberjacks[lumberjackindex]
    def addrandombear(self):
        coords = []
        for x in range(self.size):
            for y in range(self.size):
                if self.nolumberjack(x,y) and self.nobear(x,y):
                    coords.append((x,y))
        coord = coords[randint(0,len(coords)-1)]
        self.newbear(coord[0],coord[1])
    def addrandomlumberjack(self):
        coords = []
        for x in range(self.size):
            for y in range(self.size):
                if self.nolumberjack(x,y) and self.nobear(x,y):
                    coords.append((x,y))
        coord = coords[randint(0,len(coords)-1)]
        self.newlumberjack(coord[0],coord[1])
        
    def yearly(self):
        rs = ""
        dprint("--Yearly")
        rs = rs + "Year " + str(self.year) + " Report:\n"
        self.year += 1
        rs = rs + "  Number of new trees planted:   {:5}\n".format(\
                self.saplingcount)
        rs = rs + "  Number of trees chopped:       {:5}\n".format(\
                self.chopcount)
        rs = rs + "  Number of lumberjacks maw'd:   {:5}\n\n".format(\
                self.mawcount)
        rs = rs + "Populations:\n"
        lp = len(self.lumberjacks.values())
        bp = len(self.bears.values())
        tp = [0,0,0]
        for T in self.trees.values():
            if T.status != 3:
                tp[T.status] = tp[T.status] + 1
        rs = rs + "  Saplings  Trees  Elders  Lumberjacks  Bears\n"
        rs = rs + "  {0:8}  {1:5}  {2:6}  {3:11}  {4:5}\n\n"\
                .format(tp[0],tp[1],tp[2],lp,bp)
        rs = rs + "Events:\n" 
        if self.mawcount:
            rs = rs + "  --Due to a maw'ing incident, a bear was removed!\n"
            self.removerandombear()
        else:
            rs = rs + "  ++No maw'ings this year! A new bear is born!\n"
            self.addrandombear()
        if self.chopcount < lp:
            if lp > 1:
                rs=rs+"  --Not enough lumber produced! Lumberjack fired!\n"
                self.removerandomlumberjack()
        else:
            newhires=((self.chopcount - lp)//lp)//2
            if newhires:
                s = ""
                if newhires > 1:
                    s = "s"
                rs = rs + "  ++Lumber surplus! "+str(newhires)+" lumberjack" +\
                        s+" hired!\n"
                for i in range(newhires):
                    self.addrandomlumberjack()
        self.mawcount = 0
        self.saplingcount = 0
        self.chopcount = 0
        return rs

    def getbear(self, row, col):
        s1 = set(self.bears.values())
        s2 = self.grid[row][col].intersection(s1)
        if s2:
            return s2.pop()
        else:
            return 0
    def getlumberjack(self, row, col):
        s1 = set(self.lumberjacks.values())
        s2 = self.grid[row][col].intersection(s1)
        if s2:
            return s2.pop()
        else:
            return 0
    def gettree(self, row, col):
        s1 = set(self.trees.values())
        s2 = self.grid[row][col].intersection(s1)
        if s2:
            return s2.pop()
        else:
            return 0
    def notree(self,row,col):
        return not bool(self.gettree(row,col))
    def nolumberjack(self,row,col):
        return not bool(self.getlumberjack(row,col))
    def nobear(self,row,col):
        return not bool(self.getbear(row,col))
    def emptytile(self,row,col):
        return self.notree(row,col) and self.nolumberjack(row,col) and \
                self.nobear(row,col)
    def initbears(self):
        s = (self.size*self.size)//50
        dprint("--Placing",s,"initial bears")
        l = []
        for x in range(self.size):
            for y in range(self.size):
                if self.emptytile(x,y):
                    l.append((x,y))
        if not s:
            s = 1
        for i in range(s):
            z = randint(0, len(l)-1)
            w = l[z]
            if not self.getbear(w[0],w[1]):
                self.newbear(w[0],w[1])
            l.remove(w)
        return
    def initlumberjacks(self):
        s = (self.size*self.size)//20
        dprint("--Placing",s,"initial lumberjacks")
        l = []
        for x in range(self.size):
            for y in range(self.size):
                if self.emptytile(x,y):
                    l.append((x,y))
        if not s:
            s = 1
        for i in range(s):
            z = randint(0, len(l)-1)
            w = l[z]
            if not self.getlumberjack(w[0],w[1]):
                self.newlumberjack(w[0],w[1])
            l.remove(w)
        return
    def inittrees(self):
        dprint("--Planting",(self.size*self.size)//2,"initial trees")
        l = []
        for x in range(self.size):
            for y in range(self.size):
                l.append((x,y))
        for i in range((self.size*self.size)//2):
            z = randint(0, len(l)-1)
            w = l[z]
            if not self.gettree(w[0],w[1]):
                self.newtree(w[0],w[1])
            l.remove(w)
        a = (0,12,120)
        for t in self.trees.values():
            r = randint(0,2)
            t.status = r
            t.age = a[r]
        return

def main(stdscr):
    stdscr.clear()
    curses.curs_set(False)
    curses.init_pair(1,curses.COLOR_WHITE,curses.COLOR_BLACK)
    curses.init_pair(2,curses.COLOR_GREEN,curses.COLOR_BLACK)
    curses.init_pair(3,curses.COLOR_RED,curses.COLOR_BLACK)
    curses.init_pair(4,curses.COLOR_YELLOW,curses.COLOR_BLACK)
    curses.init_pair(5,curses.COLOR_RED,curses.COLOR_WHITE)
    curses.init_pair(6,curses.COLOR_BLACK,curses.COLOR_GREEN)
    curses.init_pair(7,curses.COLOR_BLACK,curses.COLOR_YELLOW)
    curses.init_pair(8,curses.COLOR_YELLOW,curses.COLOR_RED)
    height,width = stdscr.getmaxyx()
    height = height - 2
    width = (width - 57)//2
    size = min(height,width)
    F=Forest(size)
    F.inittrees()
    F.initlumberjacks()
    F.initbears()
    s  = ""
    s1 = ""
    s2 = ""
    while True:
        try:
            stdscr.clear()
            sleep(SLEEPTIMER)
            s = F.tick()
            if s:
                s1 = s
            s2 = F.draw()
            sx2 = s2.split("\n")
            stdscr.addstr(0,0,sx2[0],curses.A_UNDERLINE+curses.A_BOLD)
            sx2 = sx2[1:]
            x = 1
            for line in sx2:
                y = 0
                for char in line:
                    attr = curses.color_pair(1)
                    if char == "s":
                        attr = curses.A_DIM + curses.color_pair(2)
                    elif char == "t":
                        attr = curses.color_pair(2)
                    elif char == "T":
                        attr = curses.A_BOLD + curses.color_pair(6)
                    elif char == "L":
                        attr = curses.A_BOLD + curses.color_pair(4)
                    elif char == "X":
                        attr = curses.A_BOLD + curses.color_pair(7)
                    elif char == "B":
                        attr = curses.A_BOLD + curses.color_pair(3)
                    elif char == "&":
                        attr = curses.A_BOLD + curses.color_pair(8)
                    else:
                        attr = curses.color_pair(1)
                    stdscr.addstr(x,y,char,attr)
                    y += 1
                x += 1
            sx1 = s1.split("\n")
            i = 1
            stdscr.addstr(0,F.size*2 + 5,sx1[0], \
                    curses.A_UNDERLINE+curses.A_BOLD)
            sx1 = sx1[1:]
            for line in sx1:
                attr = curses.color_pair(1)
                if len(line) > 0 and line[0] in "PE":
                    attr += curses.A_BOLD + curses.A_UNDERLINE
                elif len(line) > 2 and line[2] == "-":
                    attr = curses.color_pair(3)
                elif len(line) > 2 and line[2] == "+":
                    attr = curses.color_pair(2)
                stdscr.addstr(i,F.size*2 + 5,line,attr)
                i += 1
            stdscr.refresh()
            if not F.trees:
                sd = " !!! DEFORESTATION COMPLETE !!! "
                stdscr.addstr(height-2,(stdscr.getmaxyx()[1]//2)-len(sd)//2,\
                        sd,curses.color_pair(5)+curses.A_BOLD)
                stdscr.refresh()
                break
        except KeyboardInterrupt:
            return  
    stdscr.getkey()
try:
    curses.wrapper(main)
except ValueError:
    print("ERROR: Perhaps try increasing your terminal window size")
