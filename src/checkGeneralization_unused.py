'''
Created on Dec 5, 2016

@author: urishaham
'''

import os.path
from Calibration_Util import DataHandler as dh 
from Calibration_Util import FileIO as io
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import CostFunctions as cf
from sklearn import decomposition
from keras import backend as K
import ScatterHist as sh
from numpy import genfromtxt
import sklearn.preprocessing as prep
from keras.models import load_model
from keras import initializations
from keras.layers.normalization import BatchNormalization
from keras.layers import Input, Dense, merge, Activation
from keras.regularizers import l2
from keras.models import Model


# configuration hyper parameters
denoise = True # whether or not to train a denoising autoencoder to remover the zeros

######################
###### get data ######
######################
# we load two CyTOF samples 

data1 = 'person2_baseline'
data2 = 'person2_3month'

if data1 =='person1_baseline':
    sourcePath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day1_baseline.csv')
    targetPath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day2_baseline.csv')
    sourceLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day1_baseline_label.csv')
    targetLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day2_baseline_label.csv')
    autoencoder1 =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person1_baseline_DAE.h5'))  
if data1 =='person2_baseline':
    sourcePath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day1_baseline.csv')
    targetPath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day2_baseline.csv')
    sourceLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day1_baseline_label.csv')
    targetLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day2_baseline_label.csv')
    autoencoder1 =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person2_baseline_DAE.h5'))   
if data1 =='person1_3month':
    sourcePath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day1_3month.csv')
    targetPath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day2_3month.csv')
    sourceLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day1_3month_label.csv')
    targetLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day2_3month_label.csv')
    autoencoder1 =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person1_3month_DAE.h5'))  
if data1 =='person2_3month':
    sourcePath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day1_3month.csv')
    targetPath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day2_3month.csv')
    sourceLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day1_3month_label.csv')
    targetLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day2_3month_label.csv')
    autoencoder1 =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person2_3month_DAE.h5'))  
   
source1 = genfromtxt(sourcePath, delimiter=',', skip_header=0)
target1 = genfromtxt(targetPath, delimiter=',', skip_header=0)
sourceLabels1 = genfromtxt(sourceLabelPath, delimiter=',', skip_header=0)
targetLabels1 = genfromtxt(targetLabelPath, delimiter=',', skip_header=0)


if data2 =='person1_baseline':
    sourcePath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day1_baseline.csv')
    targetPath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day2_baseline.csv')
    sourceLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day1_baseline_label.csv')
    targetLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day2_baseline_label.csv')
    autoencoder2 =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person1_baseline_DAE.h5'))   
if data2 =='person2_baseline':
    sourcePath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day1_baseline.csv')
    targetPath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day2_baseline.csv')
    sourceLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day1_baseline_label.csv')
    targetLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day2_baseline_label.csv')
    autoencoder2 =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person2_baseline_DAE.h5'))   
if data2 =='person1_3month':
    sourcePath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day1_3month.csv')
    targetPath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day2_3month.csv')
    sourceLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day1_3month_label.csv')
    targetLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day2_3month_label.csv')
    autoencoder2 =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person1_3month_DAE.h5'))   
if data2 =='person2_3month':
    sourcePath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day1_3month.csv')
    targetPath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day2_3month.csv')
    sourceLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day1_3month_label.csv')
    targetLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day2_3month_label.csv')
    autoencoder2 =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person2_3month_DAE.h5'))  
   
source2 = genfromtxt(sourcePath, delimiter=',', skip_header=0)
target2 = genfromtxt(targetPath, delimiter=',', skip_header=0)
sourceLabels2 = genfromtxt(sourceLabelPath, delimiter=',', skip_header=0)
targetLabels2 = genfromtxt(targetLabelPath, delimiter=',', skip_header=0)


# pre-process data: log transformation, a standard practice with CyTOF data
target1 = dh.preProcessCytofData(target1)
source1 = dh.preProcessCytofData(source1) 
target2 = dh.preProcessCytofData(target2)
source2 = dh.preProcessCytofData(source2) 

if denoise:
    source1 = autoencoder1.predict(source1)
    target1 = autoencoder1.predict(target1)
    source2 = autoencoder2.predict(source2)
    target2 = autoencoder2.predict(target2)

# rescale source to have zero mean and unit variance
# apply same transformation to the target
preprocessor1 = prep.StandardScaler().fit(source1)
source1 = preprocessor1.transform(source1) 
target1 = preprocessor1.transform(target1)  

preprocessor2 = prep.StandardScaler().fit(source2)
source2 = preprocessor2.transform(source2) 
target2 = preprocessor2.transform(target2)    

##############################
######## load ResNets ########
##############################
mmdNetLayerSizes = [25, 25]
inputDim = 25
l2_penalty = 1e-2

def my_init (shape, name = None):
    return initializations.normal(shape, scale=.1e-4, name=name)
setattr(initializations, 'my_init', my_init)

calibInput_1 = Input(shape=(inputDim,))
block1_bn1_1 = BatchNormalization()(calibInput_1)
block1_a1_1 = Activation('relu')(block1_bn1_1)
block1_w1_1 = Dense(mmdNetLayerSizes[0], activation='linear',W_regularizer=l2(l2_penalty), init = my_init)(block1_a1_1) 
block1_bn2_1 = BatchNormalization()(block1_w1_1)
block1_a2_1 = Activation('relu')(block1_bn2_1)
block1_w2_1 = Dense(inputDim, activation='linear',W_regularizer=l2(l2_penalty), init = my_init)(block1_a2_1) 
block1_output_1 = merge([block1_w2_1, calibInput_1], mode = 'sum')
block2_bn1_1 = BatchNormalization()(block1_output_1)
block2_a1_1 = Activation('relu')(block2_bn1_1)
block2_w1_1 = Dense(mmdNetLayerSizes[1], activation='linear',W_regularizer=l2(l2_penalty), init = my_init)(block2_a1_1) 
block2_bn2_1 = BatchNormalization()(block2_w1_1)
block2_a2_1 = Activation('relu')(block2_bn2_1)
block2_w2_1 = Dense(inputDim, activation='linear',W_regularizer=l2(l2_penalty), init = my_init)(block2_a2_1) 
block2_output_1 = merge([block2_w2_1, block1_output_1], mode = 'sum')
block3_bn1_1 = BatchNormalization()(block2_output_1)
block3_a1_1 = Activation('relu')(block3_bn1_1)
block3_w1_1 = Dense(mmdNetLayerSizes[1], activation='linear',W_regularizer=l2(l2_penalty), init = my_init)(block3_a1_1) 
block3_bn2_1 = BatchNormalization()(block3_w1_1)
block3_a2_1 = Activation('relu')(block3_bn2_1)
block3_w2_1 = Dense(inputDim, activation='linear',W_regularizer=l2(l2_penalty), init = my_init)(block3_a2_1) 
block3_output_1 = merge([block3_w2_1, block2_output_1], mode = 'sum')

ResNet1 = Model(input=calibInput_1, output=block3_output_1)
ResNet1.compile(optimizer='rmsprop', loss=lambda y_true,y_pred: 
               cf.MMD(block3_output_1,target1,MMDTargetValidation_split=0.1).KerasCost(y_true,y_pred))

if data1 =='person1_baseline': 
    ResNet1.load_weights(os.path.join(io.DeepLearningRoot(),'savedModels/person1_baseline_ResNet_weights.h5'))  
if data1 =='person2_baseline': 
    ResNet1.load_weights(os.path.join(io.DeepLearningRoot(),'savedModels/person2_baseline_ResNet_weights.h5'))  
if data1 =='person1_3month': 
    ResNet1.load_weights(os.path.join(io.DeepLearningRoot(),'savedModels/person1_3month_ResNet_weights.h5'))  
if data1 =='person2_3month':  
    ResNet1.load_weights(os.path.join(io.DeepLearningRoot(),'savedModels/person2_3month_ResNet_weights.h5'))  

calibInput_2 = Input(shape=(inputDim,))
block1_bn1_2 = BatchNormalization()(calibInput_2)
block1_a1_2 = Activation('relu')(block1_bn1_2)
block1_w1_2 = Dense(mmdNetLayerSizes[0], activation='linear',W_regularizer=l2(l2_penalty), init = my_init)(block1_a1_2) 
block1_bn2_2 = BatchNormalization()(block1_w1_2)
block1_a2_2 = Activation('relu')(block1_bn2_2)
block1_w2_2 = Dense(inputDim, activation='linear',W_regularizer=l2(l2_penalty), init = my_init)(block1_a2_2) 
block1_output_2 = merge([block1_w2_2, calibInput_2], mode = 'sum')
block2_bn1_2 = BatchNormalization()(block1_output_2)
block2_a1_2 = Activation('relu')(block2_bn1_2)
block2_w1_2 = Dense(mmdNetLayerSizes[1], activation='linear',W_regularizer=l2(l2_penalty), init = my_init)(block2_a1_2) 
block2_bn2_2 = BatchNormalization()(block2_w1_2)
block2_a2_2 = Activation('relu')(block2_bn2_2)
block2_w2_2 = Dense(inputDim, activation='linear',W_regularizer=l2(l2_penalty), init = my_init)(block2_a2_2) 
block2_output_2 = merge([block2_w2_2, block1_output_2], mode = 'sum')
block3_bn1_2 = BatchNormalization()(block2_output_2)
block3_a1_2 = Activation('relu')(block3_bn1_2)
block3_w1_2 = Dense(mmdNetLayerSizes[1], activation='linear',W_regularizer=l2(l2_penalty), init = my_init)(block3_a1_2) 
block3_bn2_2 = BatchNormalization()(block3_w1_2)
block3_a2_2 = Activation('relu')(block3_bn2_2)
block3_w2_2 = Dense(inputDim, activation='linear',W_regularizer=l2(l2_penalty), init = my_init)(block3_a2_2) 
block3_output_2 = merge([block3_w2_2, block2_output_2], mode = 'sum')

ResNet2 = Model(input=calibInput_2, output=block3_output_2)
ResNet2.compile(optimizer='rmsprop', loss=lambda y_true,y_pred: 
               cf.MMD(block3_output_2,target2,MMDTargetValidation_split=0.1).KerasCost(y_true,y_pred))

if data2 =='person1_baseline': 
    ResNet2.load_weights(os.path.join(io.DeepLearningRoot(),'savedModels/person1_baseline_ResNet_weights.h5'))  
if data2 =='person2_baseline': 
    ResNet2.load_weights(os.path.join(io.DeepLearningRoot(),'savedModels/person2_baseline_ResNet_weights.h5'))  
if data2 =='person1_3month': 
    ResNet2.load_weights(os.path.join(io.DeepLearningRoot(),'savedModels/person1_3month_ResNet_weights.h5'))  
if data2 =='person2_3month':  
    ResNet2.load_weights(os.path.join(io.DeepLearningRoot(),'savedModels/person2_3month_ResNet_weights.h5'))  

###############################################
######### Train vertical nets ########
###############################################
'''
patient1_source -> patient2_source


patient2_target -> patient1_target
'''
###############################################
######## evaluate generalization ability ######
###############################################

calibration_11 =  ResNet1.predict(source1)
calibration_22 =  ResNet2.predict(source2)
calibration_12 =  ResNet1.predict(source2)
calibration_21 =  ResNet2.predict(source1)

# our hope is that:
#     calibration_b1 is as similar to newTarget1 as calibration_a1
#     calibration_a2 is as similar to newTarget2 as calibration_b2

##################################### qualitative evaluation: PCA #####################################
pca = decomposition.PCA(n_components=2)
pca.fit(target1)
target_sample_pca = np.dot(target1, pca.components_[[0,1]].transpose())
other_target_pca = np.dot(target2, pca.components_[[0,1]].transpose())
projection_before = np.dot(source1, pca.components_[[0,1]].transpose())
projection_org = np.dot(calibration_11, pca.components_[[0,1]].transpose())
projection_cross = np.dot(calibration_21, pca.components_[[0,1]].transpose())

pc1 = 0
pc2 = 1
axis1 = 'PC'+str(pc1)
axis2 = 'PC'+str(pc2)
sh.scatterHist(target_sample_pca[:,pc1], target_sample_pca[:,pc2], projection_before[:,pc1], projection_before[:,pc2], axis1, axis2)
sh.scatterHist(target_sample_pca[:,pc1], target_sample_pca[:,pc2], projection_org[:,pc1], projection_org[:,pc2], axis1, axis2)
sh.scatterHist(target_sample_pca[:,pc1], target_sample_pca[:,pc2], projection_cross[:,pc1], projection_cross[:,pc2], axis1, axis2)
sh.scatterHist(other_target_pca[:,pc1], other_target_pca[:,pc2], projection_cross[:,pc1], projection_cross[:,pc2], axis1, axis2)


pca = decomposition.PCA(n_components=2)
pca.fit(target2)
target_sample_pca = np.dot(target2, pca.components_[[0,1]].transpose())
other_target_pca = np.dot(target1, pca.components_[[0,1]].transpose())
projection_before = np.dot(source2, pca.components_[[0,1]].transpose())
projection_org = np.dot(calibration_22, pca.components_[[0,1]].transpose())
projection_cross = np.dot(calibration_12, pca.components_[[0,1]].transpose())

pc1 = 0
pc2 = 1
axis1 = 'PC'+str(pc1)
axis2 = 'PC'+str(pc2)
sh.scatterHist(target_sample_pca[:,pc1], target_sample_pca[:,pc2], projection_before[:,pc1], projection_before[:,pc2], axis1, axis2)
sh.scatterHist(target_sample_pca[:,pc1], target_sample_pca[:,pc2], projection_org[:,pc1], projection_org[:,pc2], axis1, axis2)
sh.scatterHist(target_sample_pca[:,pc1], target_sample_pca[:,pc2], projection_cross[:,pc1], projection_cross[:,pc2], axis1, axis2)
sh.scatterHist(other_target_pca[:,pc1], other_target_pca[:,pc2], projection_cross[:,pc1], projection_cross[:,pc2], axis1, axis2)

##################################### quantitative evaluation: MMD #####################################
# MMD with the scales used for training 
sourceInds = np.random.randint(low=0, high = source1.shape[0], size = 1000)
maxTargetInd = np.min([len(target1), len(target2)])
targetInds = np.random.randint(low=0, high = maxTargetInd, size = 1000)


mmd_before1 = K.eval(cf.MMD(source1,target1).cost(K.variable(value=source1[sourceInds]), K.variable(value=target1[targetInds])))
mmd_before2 = K.eval(cf.MMD(source1,target1).cost(K.variable(value=source2[sourceInds]), K.variable(value=target2[targetInds])))
mmd_after_11 = K.eval(cf.MMD(source1,target1).cost(K.variable(value=calibration_11[sourceInds]), K.variable(value=target1[targetInds])))
mmd_after_22 = K.eval(cf.MMD(source1,target1).cost(K.variable(value=calibration_22[sourceInds]), K.variable(value=target2[targetInds])))

mmd_after_12 = K.eval(cf.MMD(source1,target1).cost(K.variable(value=calibration_21[sourceInds]), K.variable(value=target1[targetInds])))
mmd_after_21 = K.eval(cf.MMD(source2,target2).cost(K.variable(value=calibration_12[sourceInds]), K.variable(value=target2[targetInds])))


print('patient 1: MMD to target1 before calibration:        ' + str(mmd_before1))
print('patient 1: MMD to target1 after calibration (net 1): ' + str(mmd_after_11))
print('patient 1: MMD to target1 after calibration (net 2): ' + str(mmd_after_21))
print('patient 2: MMD to target2 before calibration:        ' + str(mmd_before2))
print('patient 2: MMD to target2 after calibration (net 2): ' + str(mmd_after_22))
print('patient 2: MMD to target2 after calibration (net 1): ' + str(mmd_after_12))

'''
p1_base, p1_3month:
patient 1: MMD to target1 before calibration:        0.702666
patient 1: MMD to target1 after calibration (net 1): 0.301217
patient 1: MMD to target1 after calibration (net 2): 0.630393
patient 2: MMD to target2 before calibration:        0.841727
patient 2: MMD to target2 after calibration (net 2): 0.46446
patient 2: MMD to target2 after calibration (net 1): 0.581634




p2_base, p2_3month:






p1_base, p2_base
'''