import tensorflow as tf
import math
import sys
from template_model import template_model
from template_model import define_scope

class Model(template_model):
    # parameter lists
    initial_variation=0.005 #standard deviation of initial variables in the convolution filters
    dimension1=320 #the number of the convolution filters in the 1st layer
    dimension2=480
    dimension20=480 #the number of the convolution filters in the 2nd layer
    dimension21=480
    dimension22=480
    dimension4=925 #the number of the neurons in each layer of the fully-connected neural network
    conv1_filter=9
    conv2_filter=9
    conv21_filter=7
    conv22_filter=8
    max_to_keep=2
    train_speed=0.0001

    def __init__(self, *args, **kwargs):
        self.data_length=kwargs["data_length"]
        self.image = kwargs["image"]
        self.label = kwargs["label"]
        self.phase=kwargs["phase"]
        self.keep_prob=kwargs["keep_prob"]
        self.keep_prob2=kwargs["keep_prob2"]
        self.keep_prob3=kwargs["keep_prob3"]
        self.start_at=kwargs["start_at"]
        self.output_dir=kwargs["output_dir"]
        self.max_to_keep=kwargs["max_to_keep"]
        self.fc1_param=int(math.ceil((math.ceil((math.ceil((math.ceil((#math.ceil((
            self.data_length-self.conv1_filter+1)/2.0)
                        -self.conv2_filter+1)/2.0)
                        #-self.conv20_filter+1)/2.0)
                        -self.conv21_filter+1)/2.0)
                        -self.conv22_filter+1)/4.0))
        
        self.prediction
        super(Model, self).__init__(self.label, self.prediction,self.max_to_keep,self.train_speed )

        #print 'Running deap shark model'
        if self.output_dir is not None:
            flog=open(str(self.output_dir)+self.start_at+'.log', 'w')
            flog.write(str(sys.argv[0])+"\n"
                    +"the filer number of conv1:"+ str(self.dimension1)+"\n"
                      +"the filer size of conv1:"+ str(self.conv1_filter)+"\n"
                      +"the filer number of conv2:"+ str(self.dimension2)+"\n"
                      +"the filer size of conv2:"+ str(self.conv2_filter)+"\n"
                      #+"the filer number of conv20:"+ str(self.dimension20)+"\n"
                      #+"the filer size of conv20:"+ str(self.conv20_filter)+"\n"
                      +"the filer number of conv21:"+ str(self.dimension21)+"\n"
                      +"the filer size of conv21:"+ str(self.conv21_filter)+"\n"
                      +"the filer number of conv22:"+ str(self.dimension22)+"\n"
                      +"the filer size of conv22:"+ str(self.conv22_filter)+"\n"
                      +"the number of neurons in the fully-connected layer:"+ str(self.dimension4)+"\n"
                      +"the standard deviation of initial varialbles:"+ str(self.initial_variation)+"\n"
                      +"train speed:"+ str(self.train_speed)+"\n"
                      +"data length:" + str(self.data_length)+"\n")
            flog.close()
        

    @define_scope
    def prediction(self):
        x_image = self.image

        def weight_variable(shape, variable_name):
            initial = tf.truncated_normal(shape, mean=0, stddev=self.initial_variation)
            return tf.Variable(initial, name=variable_name)
          
        def bias_variable(shape, variable_name):
            initial = tf.constant(0.1, shape=shape)
            return tf.Variable(initial, name=variable_name)
        
        def bias_variable_high(shape, variable_name, carry_bias=-0.1):
            initial = tf.constant(carry_bias, shape=shape)
            return tf.Variable(initial, name=variable_name)
        
        def conv2d_1(x, W):
            return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='VALID')
        def conv2d(x, W):
            return tf.nn.conv2d(x, W, strides=[1, 2, 1, 1], padding='VALID')
        def conv2d_depth(x, W):
            return tf.nn.depthwise_conv2d(x, W, strides=[1, 1, 1, 1], padding='VALID')
        def max_pool_2x2(x):
            return tf.nn.max_pool(x, ksize=[1, 2, 1, 1], strides=[1, 2, 1, 1], padding='SAME')
        def max_pool_4x1(x):
            return tf.nn.max_pool(x, ksize=[1, 4, 1, 1], strides=[1, 4, 1, 1], padding='SAME')
        def max_pool_8x1(x):
            return tf.nn.max_pool(x, ksize=[1, 17, 1, 1], strides=[1, 17, 1, 1], padding='SAME')
 
        l2norm_list=[]
        W_conv1 = weight_variable([self.conv1_filter, 4, 1, self.dimension1], 'W_conv1')
        cond=tf.constant(0.9)
        wconv1_l2=tf.reduce_sum(tf.square(W_conv1))
        l2norm_list.append(wconv1_l2)
        W_conv1.assign(tf.cond(wconv1_l2>cond, lambda: tf.multiply(W_conv1, cond/wconv1_l2),lambda: W_conv1 ))
        h_conv11=conv2d_1(x_image, W_conv1)
        W_conv1_rc=tf.reverse(W_conv1, [0, 1])
        h_conv12=conv2d_1(x_image, W_conv1_rc)
        h_conv11_ = tf.nn.dropout(tf.nn.relu(h_conv11), self.keep_prob)
        h_conv12_ = tf.nn.dropout(tf.nn.relu(h_conv12), self.keep_prob)
        h_pool1 = max_pool_2x2(h_conv11_)
        h_pool1_rc = max_pool_2x2(h_conv12_)
        
        W_conv2 = weight_variable([self.conv2_filter, 1, self.dimension1, self.dimension2], 'W_conv2')
        wconv2_l2=tf.reduce_sum(tf.square(W_conv2))
        l2norm_list.append(wconv2_l2)
        W_conv2.assign(tf.cond(wconv2_l2>cond, lambda: tf.multiply(W_conv2, cond/wconv2_l2),lambda: W_conv2 ))
        W_conv2_rc=tf.reverse(W_conv2, [0,1])
        h_conv2 = tf.nn.dropout(tf.add(tf.nn.relu(conv2d_1(h_pool1, W_conv2)), tf.nn.relu(conv2d_1(h_pool1_rc, W_conv2_rc))), self.keep_prob2)
        h_pool2 = max_pool_2x2(h_conv2)
                         
        W_conv21 = weight_variable([self.conv21_filter, 1, self.dimension2, self.dimension21], 'W_conv21')
        wconv21_l2=tf.reduce_sum(tf.square(W_conv21))
        l2norm_list.append(wconv21_l2)
        W_conv21.assign(tf.cond(wconv21_l2>cond, lambda: tf.multiply(W_conv21, cond/wconv21_l2),lambda: W_conv21 ))
        h_conv21 = tf.nn.dropout(tf.nn.relu(conv2d_1(h_pool2, W_conv21)), self.keep_prob2)
        h_pool21 = max_pool_2x2(h_conv21)

        W_conv22 = weight_variable([self.conv22_filter, 1, self.dimension21, self.dimension22], 'W_conv22')
        wconv22_l2=tf.reduce_sum(tf.square(W_conv22))
        l2norm_list.append(wconv22_l2)
        W_conv22.assign(tf.cond(wconv22_l2>cond, lambda: tf.multiply(W_conv22, cond/wconv22_l2),lambda: W_conv22 ))
        h_conv22 = tf.nn.dropout(tf.nn.relu(conv2d_1(h_pool21, W_conv22)), self.keep_prob2)
        h_pool22 = max_pool_4x1(h_conv22)
    
        W_fc1 = weight_variable([1 * self.fc1_param * self.dimension22, self.dimension4], 'W_fc1')
        wfc1_l2=tf.reduce_sum(tf.square(W_fc1))
        l2norm_list.append(wfc1_l2)
        W_fc1.assign(tf.cond(wfc1_l2>cond, lambda: tf.multiply(W_fc1, cond/wfc1_l2),lambda: W_fc1 ))
        
        b_fc1 = bias_variable([self.dimension4], 'b_fc1')
        bfc1_2=tf.reduce_sum(tf.square(b_fc1))
        l2norm_list.append(bfc1_2)
        b_fc1.assign(tf.cond(bfc1_2>cond, lambda: tf.multiply(b_fc1, cond/bfc1_2),lambda: b_fc1 ))
        
        h_pool3_flat = tf.reshape(h_pool22, [-1, 1*self.fc1_param*self.dimension22])
        h_fc1 = tf.nn.relu(tf.add(tf.matmul(h_pool3_flat, W_fc1), b_fc1))
        h_fc1_drop = tf.nn.dropout(h_fc1, self.keep_prob3)
        
        label_shape=self.label.shape[1]
        
        W_fc4 = weight_variable([self.dimension4, tf.cast(label_shape, tf.int32)], 'W_fc4')
        wfc4_l2=tf.reduce_sum(tf.square(W_fc4))
        l2norm_list.append(wfc4_l2)
        W_fc4.assign(tf.cond(wfc4_l2>cond, lambda: tf.multiply(W_fc4, cond/wfc4_l2),lambda: W_fc4 ))        
        
        b_fc4 = bias_variable([label_shape], 'b_fc4')
        bfc4_l2=tf.reduce_sum(tf.square(b_fc4))
        l2norm_list.append(bfc4_l2)
        b_fc4.assign(tf.cond(bfc4_l2>cond, lambda: tf.multiply(b_fc4, cond/bfc4_l2),lambda: b_fc4 ))
        
        
        y_conv=tf.add(tf.matmul(h_fc1_drop, W_fc4), b_fc4)
        
        variable_dict={"W_conv1": W_conv1, 
                       "W_conv2": W_conv2,
                       "W_conv21": W_conv21, 
                       "W_conv22": W_conv22, 
                       "W_fc1": W_fc1,
                       "W_fc4": W_fc4, 
                       "b_fc1": b_fc1, 
                       "b_fc4": b_fc4}
        neurons_dict={"h_conv22":h_conv22,
                      "h_conv21":h_conv21, 
                      "h_conv2":h_conv2,
                      "h_conv11":h_conv11,
                      "h_conv12":h_conv12,
                      "h_fc1_drop": h_fc1_drop,
                      "h_pool3_flat":h_pool3_flat,
                      "h_pool22":h_pool22,
                      "h_pool21":h_pool21,
                      "h_pool2":h_pool2,
                      "h_pool1":h_pool1,
                      "h_pool1_rc":h_pool1_rc}
        return y_conv,tf.nn.sigmoid(y_conv), variable_dict, neurons_dict, l2norm_list
