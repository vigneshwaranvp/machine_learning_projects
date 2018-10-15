# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 23:38:16 2017

@author: Vicky
"""

import numpy as np
import os
import cv2
import tensorflow as tf

test=[]
a=[]
train_labels=[]
test_labels=[]
val_labels=[]

#eyeglass labels into array
labelnew=np.zeros(shape=(202599,2))
f=open('CelebA/Anno/list_attr_celeba.txt','r') 
testsite_array=f.readlines()  
for i in range(2,len(testsite_array)):
    test=testsite_array[i].split()
    a.append(test[15])
results = [int(j) for j in a]
labels = np.asarray(results)
for i in range (len(labels)):
    if (labels[i] == 1):
       labelnew[i]= [1,0] 
    else:
	    labelnew[i]= [0,1] 
labelnew=np.asarray(labelnew)

#partitioning labels
train_n=int(0.8*len(labelnew))
y=int(0.1*len(labelnew))
test_n=train_n+y
val_n=test_n+y

for i in range(0,train_n):
    train_labels.append(labelnew[i])
train_labels=np.asarray(train_labels)

for i in range(train_n,test_n):
    test_labels.append(labelnew[i])
test_labels=np.asarray(test_labels)

for i in range(test_n,len(labels)):
    val_labels.append(labelnew[i])
val_labels=np.asarray(val_labels)


#image resize function
def resize_scale(img, size):
    img=cv2.resize(img, size)
    return np.array(img,"float32")

#images into array
data=[]
label=[]
attribute=[]
train_data=[]
test_data=[]
val_data=[]
sample_data=[]
path_to_data="CelebA\\Img\\img_align_celeba\\"
img_list=os.listdir(path_to_data)
sz=(28,28)
for name in sorted(img_list):
        if '.jpg' in name:
            img=cv2.imread(path_to_data + name)
            img=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            padded_img=cv2.copyMakeBorder(img,1,1,1,1,cv2.BORDER_CONSTANT)
            resized_img=resize_scale(padded_img, sz)
            data.append(resized_img.flatten())
data=np.array(data)

#partitioning images
train_d=int(0.8*len(labelnew))
z=int(0.1*len(labelnew))
test_d=train_d+z
val_d=test_d+z

for i in range(0,train_d):
    train_data.append(data[i])
train_data=np.asarray(train_data)

for i in range(train_d,test_d):
    test_data.append(data[i])
test_data=np.asarray(test_data)

for i in range(test_d,len(data)):
    val_data.append(data[i])
val_data=np.asarray(val_data)

#next_batch function
def next_batch(num, data_, labels_):

    idx = np.arange(0 , len(data_))
    np.random.shuffle(idx)
    idx = idx[:num]
    data_shuffle = data_[idx]
    labels_shuffle = labels_[idx]
    return np.asarray(data_shuffle), np.asarray(labels_shuffle)


batch_x, batch_y = next_batch(5, test_data, test_labels)

# Training Parameters
learning_rate = 0.001
num_steps = 200
batch_size = 50
display_step = 10

# Network Parameters
num_input = 784# celebA data input (img shape: 28*28)
num_classes = 2 # celebA total classes (0-9 digits)
dropout = 0.75 # Dropout, probability to keep units

# tf Graph input
X = tf.placeholder(tf.float32, [None, num_input])
Y = tf.placeholder(tf.float32, [None, num_classes])
keep_prob = tf.placeholder(tf.float32) # dropout (keep probability)


# Create some wrappers for simplicity
def conv2d(x, W, b, strides=1):
    # Conv2D wrapper, with bias and relu activation
    x = tf.nn.conv2d(x, W, strides=[1, strides, strides, 1], padding='SAME')
    x = tf.nn.bias_add(x, b)
    return tf.nn.relu(x)


def maxpool2d(x, k=2):
    # MaxPool2D wrapper
    return tf.nn.max_pool(x, ksize=[1, k, k, 1], strides=[1, k, k, 1],
                          padding='SAME')

#next_batch function
def next_batch(num, data_, labels_):

    
    #Return a total of `num` random samples and labels. 
    
    idx = np.arange(0 , len(data_))
    np.random.shuffle(idx)
    idx = idx[:num]
    data_shuffle = data_[idx]
    labels_shuffle = labels_[idx]
    return np.asarray(data_shuffle), np.asarray(labels_shuffle)
    

# Create model
def conv_net(x, weights, biases, dropout):
    # celebA data input is a 1-D vector of 784 features (28*28 pixels)
    # Reshape to match picture format [Height x Width x Channel]
    # Tensor input become 4-D: [Batch Size, Height, Width, Channel]
    x = tf.reshape(x, shape=[-1, 28, 28, 1])

    # Convolution Layer
    conv1 = conv2d(x, weights['wc1'], biases['bc1'])
    # Max Pooling (down-sampling)
    conv1 = maxpool2d(conv1, k=2)

    # Convolution Layer
    conv2 = conv2d(conv1, weights['wc2'], biases['bc2'])
    # Max Pooling (down-sampling)
    conv2 = maxpool2d(conv2, k=2)

    # Fully connected layer
    # Reshape conv2 output to fit fully connected layer input
    fc1 = tf.reshape(conv2, [-1, weights['wd1'].get_shape().as_list()[0]])
    fc1 = tf.add(tf.matmul(fc1, weights['wd1']), biases['bd1'])
    fc1 = tf.nn.relu(fc1)
    # Apply Dropout
    fc1 = tf.nn.dropout(fc1, dropout)

    # Output, class prediction
    out = tf.add(tf.matmul(fc1, weights['out']), biases['out'])
    return out

# Store layers weight & bias
weights = {
    # 5x5 conv, 1 input, 32 outputs
    'wc1': tf.Variable(tf.random_normal([5, 5, 1, 32])),
    # 5x5 conv, 32 inputs, 64 outputs
    'wc2': tf.Variable(tf.random_normal([5, 5, 32, 64])),
    # fully connected, 7*7*64 inputs, 1024 outputs
    'wd1': tf.Variable(tf.random_normal([7*7*64, 1024])),
    # 1024 inputs, 10 outputs (class prediction)
    'out': tf.Variable(tf.random_normal([1024, num_classes]))
}

biases = {
    'bc1': tf.Variable(tf.random_normal([32])),
    'bc2': tf.Variable(tf.random_normal([64])),
    'bd1': tf.Variable(tf.random_normal([1024])),
    'out': tf.Variable(tf.random_normal([num_classes]))
}

# Construct model
logits = conv_net(X, weights, biases, keep_prob)
prediction = tf.nn.softmax(logits)

# Define loss and optimizer
loss_op = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(
    logits=logits, labels=Y))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
train_op = optimizer.minimize(loss_op)


# Evaluate model
correct_pred = tf.equal(tf.argmax(prediction, 1), tf.argmax(Y, 1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

# Initialize the variables (i.e. assign their default value)
init = tf.global_variables_initializer()

# Start training
with tf.Session() as sess:

    # Run the initializer
    sess.run(init)

    for step in range(1, num_steps+1):
        batch_x, batch_y = next_batch(batch_size, train_data, train_labels)
        # Run optimization op (backprop)
        sess.run(train_op, feed_dict={X: batch_x, Y: batch_y, keep_prob: 0.8})
        if step % display_step == 0 or step == 1:
            # Calculate batch loss and accuracy
            loss, acc = sess.run([loss_op, accuracy], feed_dict={X: batch_x,
                                                                 Y: batch_y,
                                                                 keep_prob: 1.0})
            print("Step " + str(step) + ", Minibatch Loss= " + \
                  "{:.4f}".format(loss) + ", Training Accuracy= " + \
                  "{:.3f}".format(acc))

    print("\n")
     
    # Calculate accuracy for celebA test images
    print("Testing Accuracy:", \
        sess.run(accuracy, feed_dict={X: test_data ,Y: test_labels,keep_prob: 1.0}))

