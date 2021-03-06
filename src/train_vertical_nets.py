'''
Created on Dec 5, 2016

@author: urishaham
'''
  
import os.path
import keras.optimizers
from Calibration_Util import DataHandler as dh 
from Calibration_Util import FileIO as io
from keras.layers import Input, Dense, merge, Activation
from keras.models import Model
from keras import callbacks as cb
import numpy as np
import matplotlib
from keras.layers.normalization import BatchNormalization
matplotlib.use('TkAgg')
import CostFunctions as cf
import Monitoring as mn
from keras.regularizers import l2
from sklearn import decomposition
from keras.callbacks import LearningRateScheduler
import math
import ScatterHist as sh
from keras import initializations
from numpy import genfromtxt
import sklearn.preprocessing as prep
from keras.models import load_model
import os
havedisplay = "DISPLAY" in os.environ
#if we have a display use a plotting backend
if havedisplay:
    matplotlib.use('TkAgg')
else:
    matplotlib.use('Agg')



# configuration hyper parameters
denoise = True # whether or not to train a denoising autoencoder to remove the zeros
keepProb=.8

# AE confiduration
ae_encodingDim = 25
l2_penalty_ae = 1e-2 

#MMD net configuration
mmdNetLayerSizes = [25, 25]
l2_penalty = 1e-2
#init = lambda shape, name:initializations.normal(shape, scale=.1e-4, name=name)
def my_init (shape, name = None):
    return initializations.normal(shape, scale=.1e-4, name=name)
#my_init = 'glorot_normal'

#######################
###### read data ######
#######################
# we load two CyTOF samples 

#sourcePath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day2_baseline.csv')
#targetPath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day2_baseline.csv')
# To train the net p1d1 --> p2d1, change the two lines above to:
sourcePath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day1_baseline.csv')
targetPath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day1_baseline.csv')


source = genfromtxt(sourcePath, delimiter=',', skip_header=0)
target = genfromtxt(targetPath, delimiter=',', skip_header=0)

# pre-process data: log transformation, a standard practice with CyTOF data
target = dh.preProcessCytofData(target)
source = dh.preProcessCytofData(source) 

if denoise:
    #autoencoder_s =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person2_baseline_DAE.h5'))  
    #autoencoder_t =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person1_baseline_DAE.h5'))
    # To train the net p1d1 --> p2d1, change the two lines above to:
    autoencoder_s =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person1_baseline_DAE.h5'))  
    autoencoder_t =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person2_baseline_DAE.h5'))  
    source = autoencoder_s.predict(source)
    target = autoencoder_t.predict(target)

inputDim = target.shape[1]


# rescale source to have zero mean and unit variance
# apply same transformation to the target
preprocessor = prep.StandardScaler().fit(source)
source = preprocessor.transform(source) 
target = preprocessor.transform(target)    

#############################
######## train MMD net ######
#############################


calibInput = Input(shape=(inputDim,))
block1_bn1 = BatchNormalization()(calibInput)
block1_a1 = Activation('relu')(block1_bn1)
block1_w1 = Dense(mmdNetLayerSizes[0], activation='linear',W_regularizer=l2(l2_penalty), init = my_init)(block1_a1) 
block1_bn2 = BatchNormalization()(block1_w1)
block1_a2 = Activation('relu')(block1_bn2)
block1_w2 = Dense(inputDim, activation='linear',W_regularizer=l2(l2_penalty), init = my_init)(block1_a2) 
block1_output = merge([block1_w2, calibInput], mode = 'sum')
block2_bn1 = BatchNormalization()(block1_output)
block2_a1 = Activation('relu')(block2_bn1)
block2_w1 = Dense(mmdNetLayerSizes[1], activation='linear',W_regularizer=l2(l2_penalty), init = my_init)(block2_a1) 
block2_bn2 = BatchNormalization()(block2_w1)
block2_a2 = Activation('relu')(block2_bn2)
block2_w2 = Dense(inputDim, activation='linear',W_regularizer=l2(l2_penalty), init = my_init)(block2_a2) 
block2_output = merge([block2_w2, block1_output], mode = 'sum')
block3_bn1 = BatchNormalization()(block2_output)
block3_a1 = Activation('relu')(block3_bn1)
block3_w1 = Dense(mmdNetLayerSizes[1], activation='linear',W_regularizer=l2(l2_penalty), init = my_init)(block3_a1) 
block3_bn2 = BatchNormalization()(block3_w1)
block3_a2 = Activation('relu')(block3_bn2)
block3_w2 = Dense(inputDim, activation='linear',W_regularizer=l2(l2_penalty), init = my_init)(block3_a2) 
block3_output = merge([block3_w2, block2_output], mode = 'sum')

calibMMDNet = Model(input=calibInput, output=block3_output)

# learning rate schedule
def step_decay(epoch):
    initial_lrate = 0.001
    drop = 0.1
    epochs_drop = 150.0
    lrate = initial_lrate * math.pow(drop, math.floor((1+epoch)/epochs_drop))
    return lrate
lrate = LearningRateScheduler(step_decay)

#train MMD net
optimizer = keras.optimizers.rmsprop(lr=0.0)

calibMMDNet.compile(optimizer=optimizer, loss=lambda y_true,y_pred: 
               cf.MMD(block3_output,target,MMDTargetValidation_split=0.1).KerasCost(y_true,y_pred))
K.get_session().run(tf.global_variables_initializer())

sourceLabels = np.zeros(source.shape[0])
calibMMDNet.fit(source,sourceLabels,nb_epoch=500,batch_size=1000,validation_split=0.1,verbose=1,
           callbacks=[lrate, mn.monitorMMD(source, target, calibMMDNet.predict),
                      cb.EarlyStopping(monitor='val_loss',patience=50,mode='auto')])

##############################
###### evaluate results ######
##############################

calibratedSource = calibMMDNet.predict(source)

##################################### qualitative evaluation: PCA #####################################
pca = decomposition.PCA()
pca.fit(target)

# project data onto PCs
target_sample_pca = pca.transform(target)
projection_before = pca.transform(source)
projection_after = pca.transform(calibratedSource)

# choose PCs to plot
pc1 = 0
pc2 = 1
axis1 = 'PC'+str(pc1)
axis2 = 'PC'+str(pc2)
sh.scatterHist(target_sample_pca[:,pc1], target_sample_pca[:,pc2], projection_before[:,pc1], projection_before[:,pc2], axis1, axis2)
sh.scatterHist(target_sample_pca[:,pc1], target_sample_pca[:,pc2], projection_after[:,pc1], projection_after[:,pc2], axis1, axis2)
 
'''
# save models
calibMMDNet.save_weights(os.path.join(io.DeepLearningRoot(),'savedModels/person2_1_baseline_weights.h5'))  
# To train the net p1d1 --> p2d1, change the line above to:
# calibMMDNet.save_weights(os.path.join(io.DeepLearningRoot(),'savedModels/person1_2_baseline_weights.h5'))  
'''
