import numpy as np
import tensorflow as tf
import pdb

# model: softmax(W2*tanh(W1*x)) where x are embeddings
def model(inputs, params, pretrain=None):
    n = params['gram_size'] - 1 # -1 to get shape of context
    V = params['vocab_size']
    d_emb = params['emb_size']
    d_hid = params['hid_size']

    if pretrain:
        emebed_init = pretrain
    else:
        embed_init = tf.random_uniform([V, d_emb], -1.0, 1.0)
    #embed_init = init if init else embed_init = tf.random_uniform([V, d_emb], -1.0, 1.0)
    embeddings = tf.Variable(embed_init)
    embeds = tf.nn.embedding_lookup(embeddings, inputs) # will want to load pretrained
    reshape = tf.reshape(embeds, [-1, n*d_emb], name='reshape') # TODO explore position depedent embs
    with tf.name_scope('linear1'):
        weights = tf.Variable(tf.random_uniform([n*d_emb, d_hid], -1.0, 1.0), name='weights')
        biases = tf.Variable(tf.zeros([d_hid], name='biases'))
        linear1 = tf.matmul(reshape, weights)+biases
    activation = tf.nn.tanh(linear1)
    with tf.name_scope('linear2'):
        weights = tf.Variable(tf.random_uniform([d_hid, V], -1.0, 1.0), name='weights')
        biases = tf.Variable(tf.zeros([V], name='biases'))
        linear2 = tf.matmul(activation, weights)+biases
    return linear2

# takes in logits (pre-softmax normalized scores)
def loss(logits, labels):
    labels = tf.to_int64(labels)
    cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(logits, labels, name='xentropy')
    loss = tf.reduce_mean(cross_entropy, name='xentropy_mean')
    return loss

# TODO normalize embeddings; clip/normalize gradient?; decay learning rate
def train(loss, learning_rate): # NOTE learning rate not used here
    #tf.scalar_summary(loss.op.name, loss) # TODO what does this do
    learning_rate_ph = tf.placeholder(tf.float32, shape=[])
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate_ph)
    global_step = tf.Variable(0, name='global_step', trainable=False) # counter for number of batches
    train_op = optimizer.minimize(loss, global_step=global_step)
    return train_op

# uses the loss score to compute perplexity
# Note: not really used because need to average loss then take exp
def validate(loss):
    ppl = tf.exp(loss, name='ppl')
    return ppl
