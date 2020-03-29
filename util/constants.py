import sys
import os
sys.stdout = open(os.devnull, 'w')
import arcade
import tensorflow as tf
import numpy as np
from tensorflow import keras
import multiprocessing
from zlib import crc32

sys.stdout = sys.__stdout__

RANDOM_SEED = 1

SPRITE_SCALING = 0.5
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Adaptive AI"

ARROW_IMAGE_HEIGHT = 7.9
MOVEMENT_SPEED = 3#7.5 
ARROW_SPEED = 12  #20
ANGLE_SPEED = 4
#variables for making walls for arcade viewing and a* algo
VERT_WALL_START=1
VERT_WALL_END=1
VERT_CENTER = 465 # X value
HOR_WALL_START=1
HOR_WALL_END=1
HOR_CENTER = 200 # y value
BOX = 3


PLAYER_HEALTH = 1000#80
SCALING_ADJUSTMENT = PLAYER_HEALTH/80

ARROW_HITS_UNTIL_DEATH = 5.2 * SCALING_ADJUSTMENT #5.5
ARROW_DAMAGE = PLAYER_HEALTH / ARROW_HITS_UNTIL_DEATH
FIREBALL_HITS_UNTIL_DEATH = 5.4 * SCALING_ADJUSTMENT
FIREBALL_DAMAGE = PLAYER_HEALTH / FIREBALL_HITS_UNTIL_DEATH
KNIFE_HITS_UNTIL_DEATH = 3.2 * SCALING_ADJUSTMENT
KNIFE_DAMAGE = PLAYER_HEALTH / KNIFE_HITS_UNTIL_DEATH


SHORT_SPEED_HANDICAP = .145#.955
MID_SPEED_HANDICAP = .09#1

GENE_LENGTH = 20  
# JTW length of genes used for adaptive network weights
# Weights used will be a composite function of genes from a stretch of weights
# this long


MAGE_IMAGE = 'images/mage.png'
KNIGHT_IMAGE = 'images/lilknight.png'

# def decideWinner(num):
#     health = float(num)
#     if health < 
class Counter(object):
    def __init__(self, initval=0):
        self.val = multiprocessing.RawValue('i', initval)
        self.lock = multiprocessing.Lock()

    def increment(self):
        with self.lock:
            self.val.value += 1

    @property
    def value(self):
        return self.val.value
class HitBox(arcade.Sprite):
    z = 500
    y = ARROW_IMAGE_HEIGHT
class Knife(arcade.Sprite):
    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
class Arrow(arcade.Sprite):
    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
class Fireball(arcade.Sprite):
    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
class ArrowSimulated:
    def __init__(self, x, y, v, box):
        self.x = x 
        self.y = y
        self.vel = v
        self.box = box
class FireballSimulated:
    def __init__(self, x, y, v, box):
        self.x = x 
        self.y = y
        self.vel = v
        self.box = box
class Layer:
    def __init__(self, weights):
        self.weights = weights

class Network:
    def __init__(self, layers):
        self.layers = layers
    def createNetwork(self, adaptive = False):
        if adaptive == True:
            net = AdaptiveNetwork(self.layers)
            return net.createNetwork()
        else:
            tensors = []
            results = []
            layer = tf.keras.layers.Dense(1, input_shape=(17,1))
            inputs = keras.Input(shape=(17,))
            for i in range(len(self.layers) - 4):
                if len(self.layers)- 5 == 0:
                    move_x = tf.keras.layers.Dense(1,activation='tanh')
                    move_y = tf.keras.layers.Dense(1,activation='tanh')
                    shoot1 = tf.keras.layers.Dense(1,activation='sigmoid')
                    shoot2 = tf.keras.layers.Dense(1,activation='sigmoid')
                    shoot3 = tf.keras.layers.Dense(1,activation='sigmoid')
                    tensors.append(move_x)
                    tensors.append(move_y)
                    tensors.append(shoot1)
                    tensors.append(shoot2)
                    tensors.append(shoot3)
                    results.append(move_x(inputs))
                    results.append(move_y(inputs))
                    results.append(shoot1(inputs))
                    results.append(shoot2(inputs))
                    results.append(shoot3(inputs))
                elif i == 0:
                    h = tf.keras.layers.Dense(len(self.layers[i].weights[0]), activation='relu')
                    results.append(h(inputs))
                    tensors.append(h)
                elif i <= len(self.layers)- 4 - 2:
                    h = tf.keras.layers.Dense(len(self.layers[i].weights[0]), activation='relu')
                    results.append(h(results[i-1]))
                    tensors.append(h)
                else:
                    move_x = tf.keras.layers.Dense(1,activation='tanh')
                    move_y = tf.keras.layers.Dense(1,activation='tanh')
                    shoot1 = tf.keras.layers.Dense(1,activation='sigmoid')
                    shoot2 = tf.keras.layers.Dense(1,activation='sigmoid')
                    shoot3 = tf.keras.layers.Dense(1,activation='sigmoid')
                    results.append(move_x(results[i-1]))
                    results.append(move_y(results[i-1]))
                    results.append(shoot1(results[i-1]))
                    results.append(shoot2(results[i-1]))
                    results.append(shoot3(results[i-1]))
                    tensors.append(move_x)
                    tensors.append(move_y)
                    tensors.append(shoot1)
                    tensors.append(shoot2)
                    tensors.append(shoot3)
            counter = 0
            for i in range(len(tensors)):
                if i < len(self.layers) - 5:
                    tensors[i].set_weights([np.asarray(self.layers[i].weights),np.zeros(len(self.layers[i].weights[0]))])
                else:
                    tensors[i].set_weights([np.asarray(self.layers[i - counter].weights),np.zeros(len(self.layers[i - counter].weights[0]))])
                    counter += 1 
    
            return tf.keras.Model(inputs=inputs, outputs=[results[len(results)-5],results[len(results)-4],results[len(results)-3],results[len(results)-2],results[len(results)-1]])
                    
    
    
class AdaptiveNetwork:
    def __init__(self, layers):
        #layers is a list of Layer objects, each of which has a list of weights
        self.layers = layers
    def createNetwork(self, adaptive = True):
        tensors = []
        results = []
        inputs = keras.Input(shape=(17,),batch_size =1)
        for i in range(len(self.layers) - 4):
            if len(self.layers)- 5 == 0:
                move_x = tf.keras.layers.Dense(1,activation='tanh')
                move_y = tf.keras.layers.Dense(1,activation='tanh')
                shoot1 = tf.keras.layers.Dense(1,activation='sigmoid')
                shoot2 = tf.keras.layers.Dense(1,activation='sigmoid')
                shoot3 = tf.keras.layers.Dense(1,activation='sigmoid')
                normed_inputs = tf.keras.layers.LayerNormalization()(inputs)
                adaptive_inputs = tf.expand_dims(normed_inputs,0)
                adaptive_layer = tf.keras.layers.LSTM(6, stateful=True,time_major = True)
                adaptive_outputs = adaptive_layer(adaptive_inputs)
                tensors.append(move_x)
                tensors.append(move_y)
                tensors.append(shoot1)
                tensors.append(shoot2)
                tensors.append(shoot3)
                results.append(move_x(inputs))
                results.append(move_y(inputs))
                results.append(shoot1(inputs))
                results.append(shoot2(inputs))
                results.append(shoot3(inputs))
            elif i == 0:
                h = tf.keras.layers.Dense(len(self.layers[i].weights[0]), activation='relu')
                results.append(h(inputs))
                tensors.append(h)
            elif i <= len(self.layers)- 4 - 2:
                h = tf.keras.layers.Dense(len(self.layers[i].weights[0]), activation='relu')
                results.append(h(results[i-1]))
                tensors.append(h)
            else:
                move_x = tf.keras.layers.Dense(1,activation='tanh')
                move_y = tf.keras.layers.Dense(1,activation='tanh')
                shoot1 = tf.keras.layers.Dense(1,activation='sigmoid')
                shoot2 = tf.keras.layers.Dense(1,activation='sigmoid')
                shoot3 = tf.keras.layers.Dense(1,activation='sigmoid')
                normed_inputs = tf.keras.layers.LayerNormalization()(results[i-1])
                adaptive_inputs = tf.expand_dims(normed_inputs,0)
                adaptive_layer = tf.keras.layers.LSTM(6, stateful=True,time_major = True)
                adaptive_outputs = adaptive_layer(adaptive_inputs)
                results.append(move_x(results[i-1]))
                results.append(move_y(results[i-1]))
                results.append(shoot1(results[i-1]))
                results.append(shoot2(results[i-1]))
                results.append(shoot3(results[i-1]))
                tensors.append(move_x)
                tensors.append(move_y)
                tensors.append(shoot1)
                tensors.append(shoot2)
                tensors.append(shoot3)
        counter = 0
        for i in range(len(tensors)):
            if i < len(self.layers) - 5:
                tensors[i].set_weights([np.asarray(self.layers[i].weights),np.zeros(len(self.layers[i].weights[0]))])
            else:
                tensors[i].set_weights([np.asarray(self.layers[i - counter].weights),np.zeros(len(self.layers[i - counter].weights[0]))])
                counter += 1 
                
        #set model weights for the child_weight matrix outputs
        input_weights,hidden_weights, bias = adaptive_layer.get_weights()
        
        #Repeat the weights and reshape them into the correct shape for the adaptive 
        #layer shape
        
        weight_list = []
        counter = 0
        for weights in [input_weights, hidden_weights, bias]:          
            #Input weights are based on the first layer weights
            #Hidden unit weights are based on the second layer weights
            #Bias is based on the 3rd layer weights
            first_layer_weights = np.asarray(self.layers[counter].weights) 
            counter+=1
            weights_1d = np.ravel(first_layer_weights)
            times_to_repeat = np.ceil(weights.size / weights_1d).astype(int)  
            
            #Each weight used for the adaptive layer is based on alternating addition and 
            #subtraction of the weights used for the first three layers
            weights_1d = np.repeat(weights_1d, times_to_repeat)[:weights.size]
            new_weights = np.copy(weights_1d)
            for i in range(1,GENE_LENGTH):
                if i%2 ==0:
                    new_weights += np.roll(weights_1d,i)
                else:
                    new_weights -= np.roll(weights_1d,i)
            assert not np.isnan(np.sum(new_weights))        
            weight_list.append(np.reshape(new_weights,weights.shape))
            
        adaptive_layer.set_weights(np.asarray(weight_list))   
        model = tf.keras.Model(inputs=inputs, outputs=[results[len(results)-5],
                                                      results[len(results)-4],
                                                      results[len(results)-3],
                                                      results[len(results)-2],
                                                      results[len(results)-1],
                                                      adaptive_outputs])
        #Compile model so that it can be trained
        model.compile(loss = ['mean_squared_error',
                                'mean_squared_error',
                                'mean_squared_error',
                                'mean_squared_error',
                                'mean_squared_error',
                                None])
        return model
                


