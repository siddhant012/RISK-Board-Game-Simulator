import json
import os
import random
from math import ceil as math_ceil
from numpy import bincount as np_bincount
from numpy import array as np_array

class Player:
    def __init__(self,id=0,name="",color="red"):
        self.id=id
        self.name="player"+str(id) if len(name)==0 else name
        self.color=color
        self.curr_troops_num=0
    
    '''def attack(self,territory_from,territory_to):
        return self.env_obj.attack(self,territory_from,territory_to)
    
    def deploy(self,territory_to,troops_num):
        return self.env_obj.deploy(self,territory_to,troops_num)
    
    def fortify(self,territory_from,territory_to,troops_num):
        return self.env_obj.fortify(self,territory_from,territory_to,troops_num)
    
    def move_after_attack(self,territory_from,territory_to,troops_num):
        return self.env_obj.move_after_attack(self,territory_from,territory_to,troops_num)'''
    


class Logs:
    def __init__(self,size=1000):
        self.messages=[]
        self.territories_owned=[]
        self.continents_owned=[]
        self.troops_owned=[]
        self.size=size    #in number of turns




class Environment:
    def __init__(self,base_dir="./",starting_troops_num=40,players_num=2,players=None,start_with=0):
        self.base_dir=base_dir
        self.starting_troops_num=starting_troops_num
        self.players_num=players_num
        self.players=players
        self.start_with=start_with
        self.curr_player=self.players[self.start_with]
        self.curr_phase="deploy"    #deploy,attack,move_after_attack,fortify
        self.turn_no=1
        self.logs=Logs()
        for p in self.players : p.curr_troops_num=self.starting_troops_num

        self.logs.messages.append('Environment initialized')
        self.map=self.load_map()
        self.curr_gamestate=self.init_gamestate()
    
    def reset(self):
        self.curr_player=self.players[self.start_with]
        self.curr_phase="deploy"
        self.turn_no=1
        self.logs=Logs()
        for p in self.players : p.curr_troops_num=self.starting_troops_num
        self.logs.messages.append('Environment reset')
        self.curr_gamestate=self.init_gamestate()


    
    def load_map(self):
        with open(os.path.join(self.base_dir,'map.json')) as f:
            self.map=json.load(f)
        self.logs.messages.append('Map loaded')
        return self.map
    
    def  init_gamestate(self):
        if(self.map is None) : raise ValueError('Map is None.')
        self.curr_gamestate = [[-1,0] for _ in range(len(self.map['territories']))]    #gamestate=[occupird_by(-1=noone, 0=player1, 1=player2), troops_num]

        self.logs.messages.append('Gamestate initialized')
        return self.curr_gamestate

    
    def distribute_troops_randomly(self):
        territories_num=len(self.map.get('territories'))
        split=random.randint(territories_num//2-5,territories_num//2+5)
        territories1 = random.sample(range(0,territories_num-1),split)
        territories2 = [i for i in range(territories_num) if i not in territories1 ]

        for i in territories1:
            self.curr_gamestate[i][0]=0
            self.curr_gamestate[i][1]=1

        for j in territories2:
            self.curr_gamestate[j][0]=1
            self.curr_gamestate[j][1]=1
        
        troops1=self.players[0].curr_troops_num-split
        troops2=self.players[1].curr_troops_num-(territories_num-split)
        while(troops1>0 or troops2>0):

            if(troops1>0):
                t1=random.choice(territories1)
                n1=random.randint(1,troops1)%10
                self.curr_gamestate[t1][1]+=n1
                troops1-=n1

            if(troops2>0):
                t2=random.choice(territories2)
                n2=random.randint(1,troops2)%10
                self.curr_gamestate[t2][1]+=n2
                troops2-=n2
        
        self.players[0].curr_troops_num=0
        self.players[1].curr_troops_num=0

        self.update_logs(message="Troops distributed randomly")
        return None
    
    def are_neighbours(self,t1,t2):
        territories=self.map['territories']

        t1_=[t for n,t in territories.items() if t['id']==t1 ][0]
        t2_=[t for n,t in territories.items() if t['id']==t2 ][0]

        if(t1_['name'] in t2_['neighbours']) : return True
        return False
        
    
    def deploy(self,territory_to,troops_num):
        if(self.curr_phase!="deploy") : raise ValueError('Not the deploy phase')

        if(self.curr_gamestate[territory_to][0] not in [self.curr_player.id,-1]) : raise ValueError('Unable to deploy as the player does not control the territory.')
        if(self.curr_player.curr_troops_num<troops_num) : raise ValueError('Unable to deploy as the player does not have enough troops.')

        self.curr_gamestate[territory_to][1]+=troops_num
        self.curr_player.curr_troops_num-=troops_num

        t_name=[t['name'] for n,t in self.map['territories'].items() if t['id']==territory_to][0]
        self.update_logs(message="{0} deployed {1} troops to {2}".format(self.curr_player.name,troops_num,t_name))

    
    def fortify(self,territory_from,territory_to,troops_num):
        if(self.curr_phase!="fortify") : raise ValueError('Not the fortify phase')
        if(self.curr_gamestate[territory_from][0] != self.curr_player.id  or  self.curr_gamestate[territory_to][0] != self.curr_player.id) : raise ValueError('Unable to fortify as the player does not control the territory.')
        if(self.curr_gamestate[territory_from][1]-1<troops_num) : raise ValueError('Unable to fortify as the player does not have enough troops.')
        if(not self.are_neighbours(territory_from,territory_to)) : raise ValueError('Unable to fortify as the territories are not neighbours.')

        self.curr_gamestate[territory_from][1]-=troops_num
        self.curr_gamestate[territory_to][1]+=troops_num


        t1_name=[t['name'] for n,t in self.map['territories'].items() if t['id']==territory_from][0]
        t2_name=[t['name'] for n,t in self.map['territories'].items() if t['id']==territory_to][0]
        self.update_logs(message="{0} fortified {1} troops from {2} to {3}".format(self.curr_player.name,troops_num,t1_name,t2_name))


    def attack(self,territory_from,territory_to):
        if(self.curr_phase!="attack") : raise ValueError('Not the attack phase')
        if(self.curr_gamestate[territory_from][0] != self.curr_player.id) : raise ValueError('Unable to attack as the player does not control the territory.')
        if(self.curr_gamestate[territory_to][0] == self.curr_player.id) : raise ValueError('Unable to attack own territory.')
        if(self.curr_gamestate[territory_to][0] == -1) : raise ValueError('Error. Unable to attack a neutral territory.')
        if(self.curr_gamestate[territory_from][1] <= 1) : raise ValueError('Unable to attack as the player does not have enough troops')
        if(not self.are_neighbours(territory_from,territory_to)) : raise ValueError('Unable to attack as the territories are not neighbours.')

        troops1=self.curr_gamestate[territory_from][1]-1
        troops2=self.curr_gamestate[territory_to][1]
        while(troops1>0 and troops2>0):
            dice1=sorted([random.randint(1,6) for i in range(min(3,troops1))])[::-1]
            dice2=sorted([random.randint(1,6) for i in range(min(2,troops2))])[::-1]

            if(dice1[0]>dice2[0]) : troops2-=1
            else : troops1-=1

            if(len(dice1)==2 and len(dice2)==2):
                if(dice1[1]>dice2[1]) : troops2-=1
                else : troops1-=1
        
        self.curr_gamestate[territory_from][1]=troops1+1
        self.curr_gamestate[territory_to][1]=troops2
        
        if(troops2==0):
            self.curr_gamestate[territory_to][0]=self.curr_player.id
            self.curr_gamestate[territory_to][1]=0
        
        
        t1_name=[t['name'] for n,t in self.map['territories'].items() if t['id']==territory_from][0]
        t2_name=[t['name'] for n,t in self.map['territories'].items() if t['id']==territory_to][0]
        outcome="won" if troops2==0 else "lost"
        self.update_logs(message="{0} attacked territory {1} from territory {2} and {3}".format(self.curr_player.name,t1_name,t2_name,outcome))

        return len(dice1) if outcome=="won" else 0
    

    def move_after_attack(self,territory_from,territory_to,troops_num,min_troops):
        if(min_troops==0) : return None
        if(self.curr_phase!="attack") : raise ValueError('Not the attack phase')
        if(self.curr_gamestate[territory_from][0] != self.curr_player.id  or  self.curr_gamestate[territory_to][0] != self.curr_player.id) : raise ValueError('Error. Unable to move as the player does not control the territory.')
        if(self.curr_gamestate[territory_from][1]-1<troops_num) : raise ValueError('Unable to move as the player does not have enough troops.')
        if(self.curr_gamestate[territory_to][1]!=0) : raise ValueError('Unable to move as the territory has not been recently attacked')
        if(troops_num<min_troops) : raise ValueError('Unable to move as the player must move atleast as many troops to a new territory captured after an attack as the number of dice rolled in the winning roll.')
        if(not self.are_neighbours(territory_from,territory_to)) : raise ValueError('Unable to move as the territories are not neighbours.')

        self.curr_gamestate[territory_from][1]-=troops_num
        self.curr_gamestate[territory_to][1]+=troops_num

        t1_name=[t['name'] for n,t in self.map['territories'].items() if t['id']==territory_from][0]
        t2_name=[t['name'] for n,t in self.map['territories'].items() if t['id']==territory_to][0]
        self.update_logs(message="{0} moved {1} troops from territory {2} to territory {3} after an attack".format(self.curr_player.name,troops_num,t1_name,t2_name))
    
    
    def change_turn(self):
        i=self.players.index(self.curr_player)+1
        i=i%len(self.players)
        self.curr_player=self.players[i]
        if(i==self.start_with) : self.turn_no+=1

        self.curr_phase="deploy"

        self.update_logs(message="Turn changed")
        return self.curr_player
    
    def change_phase(self):
        if(self.curr_phase=="deploy") : self.curr_phase="attack"
        elif(self.curr_phase=="attack") : self.curr_phase="fortify"
        else:
            raise ValueError('Unable to change phase. Please change the turn first.')

        self.update_logs(message="Phase changed")
        return self.curr_phase
        
    def is_completed(self):
        if(len(self.logs.territories_owned)==0) : return 0

        if(self.logs.territories_owned[-1][0]==0):
            self.update_logs(message="{} wins the game".format(self.players[1].name))
            return 1
        elif(self.logs.territories_owned[-1][1]==0):
            self.update_logs(message="{} wins the game".format(self.players[0].name))
            return 1
        return 0


    def give_troops_to_deploy(self):
        if(self.curr_phase!="deploy") : raise ValueError('Unable to provide troops.Not the deploy phase')
        bonus_troops=0

        i=self.players.index(self.curr_player)
        num=len([1 for r in self.curr_gamestate if r[0]==i])
        bonus_troops=min(3,int(math_ceil(num/3)))

        continents=self.map.get('continents')
        territories=self.map.get('territories')

        '''for i,p in enumerate(self.players):
            for n,c in continents.items():
                
                territories_in_c = [t for n,t in territories.items() if continents.get(t['continent'])['id']==c['id']]
                territories_in_c_under_player_p = [t for t in territories_in_c if self.curr_gamestate[t['id']][0]==p.id]

                if(len(territories_in_c)==len(territories_in_c_under_player_p)):
                    bonus_troops+=int(c['value'])'''

        for n,c in continents.items():
            
            territories_in_c = [t for n,t in territories.items() if continents.get(t['continent'])['id']==c['id']]
            territories_in_c_under_curr_player = [t for t in territories_in_c if self.curr_gamestate[t['id']][0]==self.curr_player.id]

            if(len(territories_in_c)==len(territories_in_c_under_curr_player)):
                bonus_troops+=int(c['value'])
        
        
        self.curr_player.curr_troops_num+=bonus_troops

        self.update_logs(message="{0} recieved {1} new troops to deploy".format(self.curr_player.name,bonus_troops))


    def display_logs(self,last=1):
        if(len(self.logs.troops_owned)==0) : print("Nothing to display");return
        last=min(len(self.logs.troops_owned),last)
        for i in range(1,last+1):
            print("-"*50)
            print("Turn number : ",self.turn_no)
            print("Active player name: ",self.curr_player.name)
            print("Active player id: ",self.curr_player.id)
            print("Current phase : ",self.curr_phase)
            print("Current troops : ",self.curr_player.curr_troops_num)

            players_name=[p.name for p in self.players]
            players_id=[p.id for p in self.players]

            territories_owned=self.logs.territories_owned[i*-1]
            continents_owned=self.logs.continents_owned[i*-1]
            troops_owned=self.logs.troops_owned[i*-1]


            #printing map
            numbering=[i for i in range(len(self.curr_gamestate))]
            map=[r[0] for r in self.curr_gamestate]
            troops=[r[1] for r in self.curr_gamestate]
            row_format ="{:>3}"*(len(map))
            print("Territory_id : ",row_format.format(*numbering))
            print("Map          : ",row_format.format(*map))
            print("Troops       : ",row_format.format(*troops))
            print("Last message  :",self.logs.messages[-1])

            
            #printing data in tabular form
            headings=['Player name','Player id','Territories owned','Continents owned','Troops owned']
            data=np_array([ [players_name[p],players_id[p],territories_owned[p],continents_owned[p],troops_owned[p]] for p in range(len(self.players))])

            #row_format ="{:<20}"*(len(headings)+1)
            row_format ="{:>20}"*(len(headings))

            print("\n")
            print(row_format.format(*headings))
            for team, row in zip(headings, data):
                print(row_format.format(*row))


    def update_logs(self,message):  #after each activity 
        troops_owned=[ sum([r[1] for r in self.curr_gamestate if r[0]==p.id]) for p in self.players ]
        territories_owned=np_bincount([r[0] for r in self.curr_gamestate if r[0]>=0]).tolist()
        territories_owned.extend([0 for _ in range(self.players_num-len(territories_owned))])

        continents_owned=[0 for _ in range(len(self.players))]
        continents=self.map.get('continents')
        territories=self.map.get('territories')
        for i,p in enumerate(self.players):
            for n,c in continents.items():
                
                territories_in_c = [t for n,t in territories.items() if continents.get(t['continent'])['id']==c['id']]
                territories_in_c_under_player_p = [t for t in territories_in_c if self.curr_gamestate[t['id']][0]==p.id]

                if(len(territories_in_c)==len(territories_in_c_under_player_p)):
                    continents_owned[i]+=1
        
        self.logs.continents_owned.append(continents_owned)
        self.logs.territories_owned.append(territories_owned)
        self.logs.troops_owned.append(troops_owned)
        self.logs.messages.append(message)

        if(len(self.logs.continents_owned)==self.logs.size) : self.logs.continents_owned.pop(0)
        if(len(self.logs.territories_owned)==self.logs.size) : self.logs.territories_owned.pop(0)
        if(len(self.logs.troops_owned)==self.logs.size) : self.logs.troops_owned.pop(0)
        if(len(self.logs.messages)>=self.logs.size) : self.logs.messages=self.logs.messages[len(self.logs.messages)-self.logs.size:]
    
    def display_messages(self,last=100):
        print("\n")
        last=min(len(self.logs.messages),last)

        for m in self.logs.messages[-1*last:] : print(m)
        return None




'''def main():
    pl0=Player(40,id=0,color="red")
    pl1=Player(40,id=1,color="green")
    env=Environment(players=[pl0,pl1])
    env.distribute_troops_randomly()

    for i in range(3):
        env.give_troops_to_deploy()

        env.display_logs(last=1)

        t1,tr=(None,None)
        while(t1!=0 and tr!=0):
            t1,tr=list(map(int,input('territory_to and troops_num (0,0 to exit) : ').split(' ')))
            if(tr>0):
                env.deploy(t1,tr)
                env.display_logs(last=1)
        
        env.change_phase()
        env.display_logs(last=1)

        t1,t2=(None,None)
        while(t1!=0 and t2!=0):
            t1,t2=list(map(int,input('territory_from and territory_to (0,0 to exit) : ').split(' ')))
            if(t1>0 and t2>0):
                min_troops=env.attack(t1,t2)
                env.display_logs(last=1)
                if(min_troops>0):
                    tr=int(input('troops_num : '))
                    env.move_after_attack(t1,t2,tr,min_troops)
                    env.display_logs(last=1)
        
        env.change_phase()
        env.display_logs(last=1)

        t1,t2,tr=(None,None,None)
        t1,t2,tr=list(map(int,input('territory_from,territory_to and troops_num (0,0,0 to exit) : ').split(' ')))
        if(t1>0 and t2>0 and tr>0):
            env.fortify(t1,t2,tr)
            env.display_logs(last=1)
        
        env.change_turn()
        env.display_logs(last=1)




    #env.deploy(1,5)

    #env.display_logs(last=1)

    #env.display_messages(last=5)

    #print(env.logs.troops_owned)
    
    #for t in 10:
    #    env.deploy()

if(__name__=="__main__") : main()'''