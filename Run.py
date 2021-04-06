import json
import os
import tkinter as tk
from tkinter import font as tkFont
from PIL import Image
from Environment import Environment,Player
from numpy import array as np_array

class Start_with_gui:
    def __init__(self,env):
        self.env=env
        self.started=False
        self.completed=False
        self.board_dims=Image.open(os.path.join(self.env.base_dir,"riskboard.png")).size
        self.root=None
        self.popup_win=None
        self.other_win=None

        self.tempvar=None
        self.curr_info_label=None
        self.logs_info_label=None
        self.territory_btns=None
        self.msg_label=None
        self.msg=""
        self.refresh_rate=250
    
    def reset(self):
        self.env.reset()
        if(self.popup_win is not None) : self.popup_win.destroy()
        if(self.other_win is not None) : self.other_win.destroy()
        if(self.root is not None) : self.root.destroy()
        self.started=False
        self.completed=False
        self.root=None
        self.popup_win=None
        self.other_win=None
        self.tempvar=None
        self.curr_info_label=None
        self.logs_info_label=None
        self.territory_btns=None
        self.msg_label=None
        self.msg=""


    def start_game(self):
        self.started=True
        self.completed=False
        if(self.popup_win is not None) : self.popup_win.destroy()
        if(self.other_win is not None) : self.other_win.destroy()
        if(self.root is not None) : self.root.destroy()
        self.env.distribute_troops_randomly()
        self.env.give_troops_to_deploy()
        self.msg="{} troops recieved. Select a territory to deploy to".format(self.env.curr_player.curr_troops_num)
        self.start_render()
    
    def exit_game(self):
        if(self.popup_win is not None) : self.popup_win.destroy()
        if(self.other_win is not None) : self.other_win.destroy()
        if(self.root is not None) : self.root.destroy()
        exit(1)
    
    def restart_game(self):
        self.reset()
        self.start_game()
    
    def completed_game(self):
        if(self.completed) : return

        self.completed=True
        self.msg=self.env.logs.messages[-1]

        self.other_win=tk.Toplevel()

        C=tk.Canvas(self.other_win,height=400,width=500,bg="white")
        C.pack()

        label=tk.Label(self.other_win,text=self.msg,relief=tk.RAISED,font=tkFont.Font(family='Helvetica',size=30,weight='bold'))
        label.place(x=0,y=150-100,h=300,w=500)

        restartB=tk.Button(self.other_win,text="Restart",font=tkFont.Font(family='Helvetica',size=12,weight='bold'),command=self.restart_game)
        restartB.place(x=175,y=250,h=50,w=150)

        homeB=tk.Button(self.other_win,text="Home",font=tkFont.Font(family='Helvetica',size=12,weight='bold'),command=lambda :[self.reset(),self.start_render()])
        homeB.place(x=175,y=300,h=50,w=150)


        self.root.withdraw()
        self.root.wait_window(self.other_win)
        self.root.deiconify()

    
    def pause_game(self):
        self.other_win=tk.Toplevel()

        C=tk.Canvas(self.other_win,height=300,width=600)
        C.pack()

        continueB=tk.Button(self.other_win,text="Continue",font=tkFont.Font(family='Helvetica',size=12,weight='bold'),command=lambda :self.continue_game())
        continueB.place(x=300-75,y=150-25,h=50,w=150)

        self.root.withdraw()
        self.root.wait_window(self.other_win)
        self.root.deiconify()

    def continue_game(self):
        self.other_win.destroy()

    def gui_num_input(self,prompt):
        self.popup_win=tk.Toplevel()

        inp=tk.StringVar()
        label=tk.Label(self.popup_win,text=prompt)
        entry=tk.Entry(self.popup_win,textvariable=inp)
        label.pack(side="left",padx=(20,0),pady=20)
        entry.pack(side="right",fill="x",padx=(0,20),pady=20,expand=True)
        entry.bind("<Return>",lambda event:self.popup_win.destroy())

        self.root.wait_window(self.popup_win)
        val=inp.get()
        try : return int(val)
        except : return 0
                

    
    def change_phase(self):
        self.env.change_phase()
        #if(self.env.curr_phase=="deploy"):
        #    self.env.give_troops_to_deploy()
        #    self.msg="{} troops recieved. Select a territory to deploy to".format(self.env.curr_player.curr_troops_num)
        if(self.env.curr_phase=="attack"):
            self.msg="Select a territory to attack from"
        elif(self.env.curr_phase=="fortify"):
            self.msg="Select a territory to fortify troops from"
    
    def change_turn(self):
        self.env.change_turn()
        self.env.give_troops_to_deploy()
        self.msg="{} troops recieved. Select a territory to deploy to".format(self.env.curr_player.curr_troops_num)
    


    def update_info(self):
        
        if(self.env.is_completed()):
            self.completed_game()


        if(self.territory_btns is not None):
            for i,tbtn in enumerate(self.territory_btns):
                tbtn['text']=str(self.env.curr_gamestate[i][1])
                tbtn['bg']=self.env.players[self.env.curr_gamestate[i][0]].color

        if(self.logs_info_label is not None):
            headings=['Player id','Territories owned','Continents owned','Troops owned']

            players_name=[p.name for p in self.env.players]
            players_id=[p.id for p in self.env.players]
            territories_owned=self.env.logs.territories_owned[-1]
            continents_owned=self.env.logs.continents_owned[-1]
            troops_owned=self.env.logs.troops_owned[-1]

            
            data=np_array([ [players_id[p],territories_owned[p],continents_owned[p],troops_owned[p]] for p in range(len(self.env.players))])
            row_format ="{:<30}"*(len(headings))
            out=""
            out+=row_format.format(*headings)+"\n"
            for team, row in zip(headings, data):
                out+=row_format.format(*row)+"\n"
            self.logs_info_label['text']=out

        
        if(self.msg_label is not None and len(self.msg)>0):
            self.msg_label['text']=self.msg


        if(self.curr_info_label is not None):
            self.curr_info_label['text']="Turn number : "+str(self.env.turn_no)+"\n"+\
                                            "Active player name: "+str(self.env.curr_player.name)+"\n"+\
                                            "Active player id: "+str(self.env.curr_player.id)+"\n"+\
                                            "Current phase : "+str(self.env.curr_phase)+"\n"+\
                                            "Current troops : "+str(self.env.curr_player.curr_troops_num)

        self.root.after(self.refresh_rate,self.update_info)


        

    def action(self,kwargs):
        if(self.env.curr_phase=="deploy"):
            territory_to=kwargs['tid']
            self.msg="Specify the number of troops to be deployed."
            troops_num=self.gui_num_input("Number of troops : ")
            self.env.deploy(territory_to,troops_num)
            self.msg="{} troops remaining. Select a territory to deploy to".format(self.env.curr_player.curr_troops_num)
        
        elif(self.env.curr_phase=="attack"):
            if(self.tempvar is None):
                self.tempvar=kwargs['tid']
                self.msg="Select a territory to attack to"
            else:
                territory_from=self.tempvar
                self.tempvar=None
                territory_to=kwargs['tid']
                min_troops=self.env.attack(territory_from,territory_to)

                if(min_troops>0):
                    self.msg="You won the attack. Specify the number of troops to be moved ({} minimum)".format(min_troops)
                    
                    if(not self.env.is_completed()):
                        troops_num=self.gui_num_input("Number of troops to be moved : ")
                    else:
                        return
                    if(troops_num>0) : self.env.move_after_attack(territory_from,territory_to,troops_num,min_troops)
                    self.msg="Select a territory to attack from"
                else:
                    self.msg="You lost the attack.Select a territory to attack from"

                

        elif(self.env.curr_phase=="fortify"):
            if(self.tempvar is None):
                self.tempvar=kwargs['tid']
                self.msg="Select a territory to fortify troops to"
            else:
                territory_from=self.tempvar
                self.tempvar=None
                territory_to=kwargs['tid']
                self.msg="Specify the number of troops to be fortified"
                troops_num=self.gui_num_input("Number of troops to be fortified : ")
                self.env.fortify(territory_from,territory_to,troops_num)
                self.msg="Fortified troops.Change the turn now"
        







        
        
    

    def start_render(self):


        self.root=tk.Tk()

        if(not self.started):
            C=tk.Canvas(self.root,height=self.board_dims[1],width=self.board_dims[0])
            C.pack()
            label=tk.Label(self.root,textvariable=tk.StringVar,relief=tk.RAISED,text="RISK",font=tkFont.Font(family='Helvetica',size=72,weight='bold'))
            label.place(x=self.board_dims[0]//2-150,y=self.board_dims[1]//2-200,h=100,w=300)

            startB=tk.Button(self.root,text="Start",font=tkFont.Font(family='Helvetica',size=18,weight='bold'),command=self.start_game)
            startB.place(x=self.board_dims[0]//2-75,y=self.board_dims[1]//2-25,h=50,w=150)

            exitB=tk.Button(self.root,text="Exit",font=tkFont.Font(family='Helvetica',size=18,weight='bold'),command=self.exit_game)
            exitB.place(x=self.board_dims[0]//2-75,y=self.board_dims[1]//2+25,h=50,w=150)

        else: 
            C=tk.Canvas(self.root,height=self.board_dims[1]+25+100,width=self.board_dims[0])
            C.pack()
            filename=tk.PhotoImage(file=os.path.join(self.env.base_dir,"riskboard.png"))
            background_label=tk.Label(self.root,image=filename)
            background_label.place(x=0,y=25)

            exitB=tk.Button(self.root,text="Exit",font=tkFont.Font(family='Helvetica',size=10,weight='bold'),command=self.exit_game)
            exitB.place(x=0,y=0,h=25,w=50)

            pauseB=tk.Button(self.root,text="Pause",font=tkFont.Font(family='Helvetica',size=10,weight='bold'),command=self.pause_game)
            pauseB.place(x=50,y=0,h=25,w=50)

            changephaseB=tk.Button(self.root,text="Next Phase",font=tkFont.Font(family='Helvetica',size=10,weight='bold'),command=self.change_phase)
            changephaseB.place(x=self.board_dims[0]-100,y=self.board_dims[1]+25+2,h=25,w=100)

            changeturnB=tk.Button(self.root,text="Next Turn",font=tkFont.Font(family='Helvetica',size=10,weight='bold'),command=self.change_turn)
            changeturnB.place(x=self.board_dims[0]-100,y=self.board_dims[1]+50+2,h=25,w=100)


            #current,message info,logs info and territory info

            self.curr_info_label=tk.Label(self.root,text="",font=tkFont.Font(family='Helvetica',size=10,weight='bold'),justify=tk.LEFT)
            self.curr_info_label.place(x=0,y=self.board_dims[1]+50,h=75,w=200)

            self.logs_info_label=tk.Label(self.root,text="",font=tkFont.Font(family='Helvetica',size=8,weight='bold'),justify=tk.RIGHT)
            self.logs_info_label.place(x=200,y=self.board_dims[1]+25+2,h=75,w=400)

            territories=self.env.map['territories']
            self.territory_btns=[]
            for n,t in territories.items():
                self.territory_btns.append( tk.Button(self.root,text="0",command=lambda kwargs={"tid":t['id']} :self.action(kwargs=kwargs),border=0,bg="green") )
                self.territory_btns[-1].place(x=t['center'][0],y=t['center'][1]+25,h=12,w=12)
            
            self.msg_label=tk.Label(self.root,text="",font=tkFont.Font(family='Helvetica',size=8,weight='bold'),justify=tk.RIGHT)
            self.msg_label.place(x=200,y=0,h=25,w=450)

            



        self.root.after(0,self.update_info)

        self.root.mainloop()
            






pl0=Player(id=0,name="Player 0",color="red")
pl1=Player(id=1,name="Player 1",color="green")
env=Environment(players=[pl0,pl1])
game=Start_with_gui(env)
game.start_render()