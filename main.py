import arcade
import sys
from MyGame import *
from sim import *
from util.constants import * 
from util.inputFunctions import * 
from GENNFunctions import * 
import time
import multiprocessing
from operator import add 
from ctypes import c_int


def runOneGame(a):

        # Need to find an answer to the counter problem 
    x = Game(a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7],a[8],a[9],-1)
    x.setup()
    val = True
    while val == True:
        val = x.update()
    return val

def main(args):
    """ Main method """

    graphics = 'no'
    evolutions = False
    # games = int(input('Enter the amount of games to be played: '))
    spacer()
    conCurrentGame = get_int_choice('How many games would you like played at the same time (Recommended amount based on computer cores '+str(multiprocessing.cpu_count())+"):",1,1000)
    iterations = get_int_choice('Enter the amount of generations to be played: ',1,5000)
    simulation_player_1 = get_str_choice("What type of simulation do you want for player 1?",'fsm','freeplay','dc','genn')
    if simulation_player_1.lower() == "freeplay":
        player_1_type = "human"
        graphics = 'yes'
    elif simulation_player_1.lower() == "fsm":
        player_1_type = get_str_choice("What type of player is player 1 ?",'short','mid','range','pq')
    elif simulation_player_1.lower() == "dc":
        player_1_type = get_str_choice("What type of dynamic controller is player 1 ?",'master','average','random','train')
    elif simulation_player_1.lower() == "genn":
        player_1_type = "genn"
    simulation_player_2 = get_str_choice("What type of simulation do you want for player 2?",'fsm','dc','freeplay','genn')
    if simulation_player_2 == "freeplay":
        player_2_type = "human"
        graphics = 'yes'
    if simulation_player_2 == "fsm":
        player_2_type = get_str_choice("What type of player is player 2?",'short','mid','range','pq')
    elif simulation_player_2.lower() == "dc":
        player_2_type = get_str_choice("What type of dynamic controller is player 2 ?",'master','average','random')
    if graphics == 'no':
        graphics = get_str_choice('Run Graphically?: ','yes','no')

    if player_1_type == 'genn':
        evolutions = True
        player_1_nets = createNets(conCurrentGame)
    else: player_1_nets = None
    if player_2_type == 'genn':
        evolutions = True
        player_2_nets = createNets(conCurrentGame)
    else: player_2_nets = None
    # count = Counter()
    if graphics == 'yes':
        window = MyGame(SCREEN_WIDTH,SCREEN_HEIGHT,SCREEN_TITLE,iterations,player_1_type,player_2_type)
        window.setup()
        try:
            arcade.run()
        except:
            pass
    elif graphics == 'no':
        start = time.time()
        player1Wins = 0
        player2Wins = 0
        draws = 0
        leftOverHealth = 0
        evolutionHealth = []
        for game in range(iterations):
            spacer()
            print("Total iterations %d out of %d" % (game + 1, iterations) )
            if evolutions == True:
                        # Update the evolutions every 9 games 
                if game % 9 == 0:
                    #Evolve Networks
                    pass

            p = multiprocessing.Pool(multiprocessing.cpu_count())
                # map will always return the results in order, if order is not important in the future use pool.imap_unordered()
            result = p.map(runOneGame,[ x for x in [[SCREEN_WIDTH,SCREEN_HEIGHT,SCREEN_TITLE,1,player_1_type,player_2_type,conCurrentGame,game,player_1_nets,player_2_nets]] * conCurrentGame])
            if game == 0: evolutionHealth = [float(i) for i in result]
            else: evolutionHealth = list(map(add, [float(i) for i in result], evolutionHealth)) 
            player1Wins += sum(int(i) > 0 for i in [int(i) for i in result]) 
            player2Wins += sum(int(i) < 0 for i in [int(i) for i in result])
            draws += sum(int(i) == 0 for i in [int(i) for i in result])  
            leftOverHealth += sum([float(i) for i in result])
            p.close()
            p.join()
        print("player 1 (" + player_1_type + "):",player1Wins)
        print("player 2 (" + player_2_type + "):",player2Wins)
        print("Draws: ",draws)
        print("Average Health Difference: ",round(abs(leftOverHealth) / (conCurrentGame * iterations),4))
        print("Total Time: ",round(time.time() - start,4))
        
if __name__ == "__main__":
    main(sys.argv)

