from builtins import range
import numpy as np


def affine_forward(x, w, b):
    """
    Computes the forward pass for an affine (fully-connected) layer.

    The input x has shape (N, d_1, ..., d_k) and contains a minibatch of N
    examples, where each example x[i] has shape (d_1, ..., d_k). We will
    reshape each input into a vector of dimension D = d_1 * ... * d_k, and
    then transform it to an output vector of dimension M.

    Inputs:
    - x: A numpy array containing input data, of shape (N, d_1, ..., d_k)
    - w: A numpy array of weights, of shape (D, M)
    - b: A numpy array of biases, of shape (M,)

    Returns a tuple of:
    - out: output, of shape (N, M)
    - cache: (x, w, b)
    """
    out = None
    ###########################################################################
    # TODO: Implement the affine forward pass. Store the result in out. You   #
    # will need to reshape the input into rows.                               #
    ###########################################################################
    # Dimension D is a product of all the subsequent layer dimension, it's like squashing a tensor into a single
    # dimensional array.
    D = np.prod(x.shape[1:])
    x_tf = x.reshape(x.shape[0], D) # (N x D)
    # Think of M as the hidden layer dimension. We have M biaes which makes sense.
    out = np.dot(x_tf, w) # (N x M)
    out += b
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    cache = (x, w, b)
    return out, cache


def affine_backward(dout, cache):
    """
    Computes the backward pass for an affine layer.

    Inputs:
    - dout: Upstream derivative, of shape (N, M)
    - cache: Tuple of:
      - x: Input data, of shape (N, d_1, ... d_k)
      - w: Weights, of shape (D, M)

    Returns a tuple of:
    - dx: Gradient with respect to x, of shape (N, d1, ..., d_k)
    - dw: Gradient with respect to w, of shape (D, M)
    - db: Gradient with respect to b, of shape (M,)
    """
    x, w, b = cache
    dx, dw, db = None, None, None
    ###########################################################################
    # TODO: Implement the affine backward pass.                               #
    ###########################################################################
    D = np.prod(x.shape[1:]) # As usual, squash everything into D dimension
    x_tf = x.reshape(x.shape[0], D) # (N x D)
    dw = np.dot(x_tf.T, dout) # (D x N)(N x M) => (D x M)
    dx = np.dot(dout, w.T).reshape(x.shape) # (N x M)(M x D) => (N x D) then reshape => (N x d_1 x d_2 x d_3 x ... x d_k)

    # Take a careful look at biases, it's actually very easy. If we keep (N x M) as our biaes, we wouldn't need to perform
    # the squashing. db is simply dout. However, we want biases to be just M and use array broadcasting to apply to N
    # examples. Thus, we are going to squash them from N dimensions into 1 using sum.
    db = np.sum(dout.T, axis=1) # (M x N) squash into (M,)
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    return dx, dw, db


def relu_forward(x):
    """
    Computes the forward pass for a layer of rectified linear units (ReLUs).

    Input:
    - x: Inputs, of any shape

    Returns a tuple of:
    - out: Output, of the same shape as x
    - cache: x
    """
    out = None
    ###########################################################################
    # TODO: Implement the ReLU forward pass.                                  #
    ###########################################################################
    out = np.maximum(0, x)
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    cache = x
    return out, cache


def relu_backward(dout, cache):
    """
    Computes the backward pass for a layer of rectified linear units (ReLUs).

    Input:
    - dout: Upstream derivatives, of any shape
    - cache: Input x, of same shape as dout

    Returns:
    - dx: Gradient with respect to x
    """
    dx, x = None, cache
    ###########################################################################
    # TODO: Implement the ReLU backward pass.                                 #
    ###########################################################################
    # If the forward value is 0 or less, ReLU squashes it and thus there isn't any gradient otherwise it's 1. A ReLu gate,
    # a.k.a. max gate, routes gradient. The gradient for a max gate is 1 for the highest value, and 0 for all other values.
    dx = dout
    dx[x <= 0] = 0
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    return dx


def batchnorm_forward(x, gamma, beta, bn_param):
    """
    Forward pass for batch normalization.

    During training the sample mean and (uncorrected) sample variance are
    computed from minibatch statistics and used to normalize the incoming data.
    During training we also keep an exponentially decaying running mean of the
    mean and variance of each feature, and these averages are used to normalize
    data at test-time.

    At each timestep we update the running averages for mean and variance using
    an exponential decay based on the momentum parameter:

    running_mean = momentum * running_mean + (1 - momentum) * sample_mean
    running_var = momentum * running_var + (1 - momentum) * sample_var

    Note that the batch normalization paper suggests a different test-time
    behavior: they compute sample mean and variance for each feature using a
    large number of training images rather than using a running average. For
    this implementation we have chosen to use running averages instead since
    they do not require an additional estimation step; the torch7
    implementation of batch normalization also uses running averages.

    Input:
    - x: Data of shape (N, D)
    - gamma: Scale parameter of shape (D,)
    - beta: Shift paremeter of shape (D,)
    - bn_param: Dictionary with the following keys:
      - mode: 'train' or 'test'; required
      - eps: Constant for numeric stability
      - momentum: Constant for running mean / variance.
      - running_mean: Array of shape (D,) giving running mean of features
      - running_var Array of shape (D,) giving running variance of features

    Returns a tuple of:
    - out: of shape (N, D)
    - cache: A tuple of values needed in the backward pass
    """
    mode = bn_param['mode']
    eps = bn_param.get('eps', 1e-5)
    momentum = bn_param.get('momentum', 0.9)

    N, D = x.shape
    running_mean = bn_param.get('running_mean', np.zeros(D, dtype=x.dtype))
    running_var = bn_param.get('running_var', np.zeros(D, dtype=x.dtype))

    out, cache = None, None
    if mode == 'train':
        #######################################################################
        # TODO: Implement the training-time forward pass for batch norm.      #
        # Use minibatch statistics to compute the mean and variance, use      #
        # these statistics to normalize the incoming data, and scale and      #
        # shift the normalized data using gamma and beta.                     #
        #                                                                     #
        # You should store the output in the variable out. Any intermediates  #
        # that you need for the backward pass should be stored in the cache   #
        # variable.                                                           #
        #                                                                     #
        # You should also use your computed sample mean and variance together #
        # with the momentum variable to update the running mean and running   #
        # variance, storing your result in the running_mean and running_var   #
        # variables.                                                          #
        #######################################################################
        sample_mean = x.mean(axis=0)
        sample_var = x.var(axis=0)
        x_norm = (x - sample_mean) / np.sqrt(sample_var + eps)
        out = x_norm * gamma + beta

        # This is the formula for exponential moving average
        running_mean = momentum * running_mean + (1 - momentum) * sample_mean
        running_var = momentum * running_var + (1 - momentum) * sample_var
        cache = (x, x_norm, gamma, beta, sample_mean, sample_var, eps)
        #######################################################################
        #                           END OF YOUR CODE                          #
        #######################################################################
    elif mode == 'test':
        #######################################################################
        # TODO: Implement the test-time forward pass for batch normalization. #
        # Use the running mean and variance to normalize the incoming data,   #
        # then scale and shift the normalized data using gamma and beta.      #
        # Store the result in the out variable.                               #
        #######################################################################
        x_norm_test = (x - running_mean) / np.sqrt(running_var + eps)
        out = x_norm_test * gamma + beta
        #######################################################################
        #                          END OF YOUR CODE                           #
        #######################################################################
    else:
        raise ValueError('Invalid forward batchnorm mode "%s"' % mode)

    # Store the updated running means back into bn_param
    bn_param['running_mean'] = running_mean
    bn_param['running_var'] = running_var

    return out, cache


def batchnorm_backward(dout, cache):
    """
    Backward pass for batch normalization.

    For this implementation, you should write out a computation graph for
    batch normalization on paper and propagate gradients backward through
    intermediate nodes.

    Inputs:
    - dout: Upstream derivatives, of shape (N, D)
    - cache: Variable of intermediates from batchnorm_forward.

    Returns a tuple of:
    - dx: Gradient with respect to inputs x, of shape (N, D)
    - dgamma: Gradient with respect to scale parameter gamma, of shape (D,)
    - dbeta: Gradient with respect to shift parameter beta, of shape (D,)
    """
    dx, dgamma, dbeta = None, None, None
    ###########################################################################
    # TODO: Implement the backward pass for batch normalization. Store the    #
    # results in the dx, dgamma, and dbeta variables.                         #
    ###########################################################################
    x, x_norm, gamma, beta, sample_mean, sample_var, eps = cache
    dx_norm = dout * gamma

    dvar = (-0.5) * (x - sample_mean) * (sample_var + eps)**(-3.0/2)
    dvar = np.sum(dx_norm * dvar, axis=0)

    dmean = -1 / np.sqrt(sample_var + eps)
    dmean = np.sum(dx_norm * dmean, axis=0) + np.sum((-2) * (x - sample_mean) * dvar, axis=0) * (1 / x.shape[0])

    dx = 1 / np.sqrt(sample_var + eps)
    dx = (dx_norm * dx) + (2 * dvar * (x - sample_mean) / x.shape[0]) + (dmean / x.shape[0])

    dgamma = (dout * x_norm).sum(axis=0) # Sum over N, such that (N, D) => (D,)
    dbeta = dout.sum(axis=0) # Sum over N, such that (N, D) => (D,)
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################

    return dx, dgamma, dbeta


def batchnorm_backward_alt(dout, cache):
    """
    Alternative backward pass for batch normalization.

    For this implementation you should work out the derivatives for the batch
    normalizaton backward pass on paper and simplify as much as possible. You
    should be able to derive a simple expression for the backward pass.

    Note: This implementation should expect to receive the same cache variable
    as batchnorm_backward, but might not use all of the values in the cache.

    Inputs / outputs: Same as batchnorm_backward
    """
    dx, dgamma, dbeta = None, None, None
    ###########################################################################
    # TODO: Implement the backward pass for batch normalization. Store the    #
    # results in the dx, dgamma, and dbeta variables.                         #
    #                                                                         #
    # After computing the gradient with respect to the centered inputs, you   #
    # should be able to compute gradients with respect to the inputs in a     #
    # single statement; our implementation fits on a single 80-character line.#
    ###########################################################################
    x, x_norm, gamma, beta, mean, var, eps = cache
    N = dout.shape[0]
    dx_norm = dout * gamma

    dx = (1. / N) * (1 / np.sqrt(var + eps)) * (N * dx_norm - np.sum(dx_norm, axis=0) - x_norm * np.sum(dx_norm * x_norm, axis=0))
    dgamma = (dout * x_norm).sum(axis=0) # Sum over N, such that (N, D) => (D,)
    dbeta = dout.sum(axis=0) # Sum over N, such that (N, D) => (D,)
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################

    return dx, dgamma, dbeta


def dropout_forward(x, dropout_param):
    """
    Performs the forward pass for (inverted) dropout.

    Inputs:
    - x: Input data, of any shape
    - dropout_param: A dictionary with the following keys:
      - p: Dropout parameter. We drop each neuron output with probability p.
      - mode: 'test' or 'train'. If the mode is train, then perform dropout;
        if the mode is test, then just return the input.
      - seed: Seed for the random number generator. Passing seed makes this
        function deterministic, which is needed for gradient checking but not
        in real networks.

    Outputs:
    - out: Array of the same shape as x.
    - cache: tuple (dropout_param, mask). In training mode, mask is the dropout
      mask that was used to multiply the input; in test mode, mask is None.
    """
    p, mode = dropout_param['p'], dropout_param['mode']
    if 'seed' in dropout_param:
        np.random.seed(dropout_param['seed'])

    mask = None
    out = None

    if mode == 'train':
        #######################################################################
        # TODO: Implement training phase forward pass for inverted dropout.   #
        # Store the dropout mask in the mask variable.                        #
        #######################################################################
        mask = np.ones(x.shape)
        probability = np.random.random(x.shape)
        mask[probability <= p] = 0
        out = mask * x
        #######################################################################
        #                           END OF YOUR CODE                          #
        #######################################################################
    elif mode == 'test':
        #######################################################################
        # TODO: Implement the test phase forward pass for inverted dropout.   #
        #######################################################################
        out = x
        #######################################################################
        #                            END OF YOUR CODE                         #
        #######################################################################

    cache = (dropout_param, mask)
    out = out.astype(x.dtype, copy=False)

    return out, cache


def dropout_backward(dout, cache):
    """
    Perform the backward pass for (inverted) dropout.

    Inputs:
    - dout: Upstream derivatives, of any shape
    - cache: (dropout_param, mask) from dropout_forward.
    """
    dropout_param, mask = cache
    mode = dropout_param['mode']

    dx = None
    if mode == 'train':
        #######################################################################
        # TODO: Implement training phase backward pass for inverted dropout   #
        #######################################################################
        dout[mask ==0] = 0
        dx = dout
        #######################################################################
        #                          END OF YOUR CODE                           #
        #######################################################################
    elif mode == 'test':
        dx = dout
    return dx


def conv_forward_naive(x, w, b, conv_param):
    """
    A naive implementation of the forward pass for a convolutional layer.

    The input consists of N data points, each with C channels, height H and
    width W. We convolve each input with F different filters, where each filter
    spans all C channels and has height HH and width WW.

    Input:
    - x: Input data of shape (N, C, H, W)
    - w: Filter weights of shape (F, C, HH, WW)
    - b: Biases, of shape (F,)
    - conv_param: A dictionary with the following keys:
      - 'stride': The number of pixels between adjacent receptive fields in the
        horizontal and vertical directions.
      - 'pad': The number of pixels that will be used to zero-pad the input.

    Returns a tuple of:
    - out: Output data, of shape (N, F, H', W') where H' and W' are given by
      H' = 1 + (H + 2 * pad - HH) / stride
      W' = 1 + (W + 2 * pad - WW) / stride
    - cache: (x, w, b, conv_param)
    """
    ###########################################################################
    # TODO: Implement the convolutional forward pass.                         #
    # Hint: you can use the function np.pad for padding.                      #
    ###########################################################################
    # F is the number of filters, C is the depth of the filter and HH and WW are filter height and filter width
    N = x.shape[0]
    num_filter = w.shape[0]
    stride = conv_param['stride']
    pad = conv_param['pad']

    # API for pad_width is ((before_1, after_1), ..., (before_N, afterN))
    pad_width = ((0, 0,), (0, 0), (pad, pad), (pad, pad))
    padded_x = np.pad(x, pad_width=pad_width, mode='constant', constant_values=0)

    input_height = x.shape[2]
    input_width = x.shape[3]
    filter_height = w.shape[2] # a.k.a HH
    filter_width = w.shape[3] # a.k.a WW

    output_height = int(1 + (input_height + 2 * pad - filter_height) / stride)
    output_width = int(1 + (input_width + 2 * pad - filter_width) / stride)
    output = np.zeros((N, num_filter, output_height, output_width))

    for n in range(N):
        for f in range(num_filter):
            for out_h in range(output_height):
                h_idx = out_h * stride
                for out_w in range(output_width):
                    w_idx = out_w * stride
                    conv_sum = np.sum(padded_x[n][:, h_idx:h_idx + filter_height, w_idx:w_idx + filter_width]* w[f])
                    output[n, f, out_h, out_w] += conv_sum + b[f]
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    cache = (x, w, b, conv_param)
    return output, cache


def conv_backward_naive(dout, cache):
    """
    A naive implementation of the backward pass for a convolutional layer.

    Inputs:
    - dout: Upstream derivatives.
    - cache: A tuple of (x, w, b, conv_param) as in conv_forward_naive

    Returns a tuple of:
    - dx: Gradient with respect to x
    - dw: Gradient with respect to w
    - db: Gradient with respect to b
    """
    dx, dw, db = None, None, None
    ###########################################################################
    # TODO: Implement the convolutional backward pass.                        #
    ###########################################################################
    # The backward pass for a convolution operation (for both the data and the weights) is also a convolution, but with
    # spatially-flipped filters. It's very easy to derive in 1 dimensional example.
    #
    # Suppose your x is a (3, 2, 2) i.e. (D, H, W) and filter is (3, 1, 1) i.e. (D, H, W) with stride = 1 and no
    # padding. We have three numbers that constitute the filter weight matrix, w[0], w[1], and w[2]. You will easily see
    # that grad_w[0] = x[0][0][0] + x[0][0][1] + x[0][1][0] + x[0][1][1]
    # that grad_w[1] = x[1][0][0] + x[1][0][1] + x[1][1][0] + x[0][1][1]
    # that grad_w[2] = x[2][0][0] + x[2][0][1] + x[2][1][0] + x[0][1][1]
    #
    # If you have N examples, then just sum across N examples
    x, w, b, conv_param = cache
    dw = np.zeros(w.shape)
    dx = np.zeros(x.shape)
    db = np.zeros(b.shape)

    N = x.shape[0]
    num_filter = w.shape[0]
    stride = conv_param['stride']
    pad = conv_param['pad']

    # API for pad_width is ((before_1, after_1), ..., (before_N, afterN))
    pad_width = ((0, 0,), (0, 0), (pad, pad), (pad, pad))
    padded_x = np.pad(x, pad_width=pad_width, mode='constant', constant_values=0)
    padded_dx = np.zeros(padded_x.shape)

    input_height = x.shape[2]
    input_width = x.shape[3]
    filter_height = w.shape[2] # a.k.a HH
    filter_width = w.shape[3] # a.k.a WW

    output_height = int(1 + (input_height + 2 * pad - filter_height) / stride)
    output_width = int(1 + (input_width + 2 * pad - filter_width) / stride)

    for n in range(N):
        for f in range(num_filter):
            for out_h in range(output_height):
                h_idx = out_h * stride
                for out_w in range(output_width):
                    w_idx = out_w * stride
                    dw[f] += padded_x[n, :, h_idx:h_idx + filter_height, w_idx:w_idx + filter_width] * dout[n, f, out_h, out_w]
                    padded_dx[n, :, h_idx:h_idx + filter_height, w_idx:w_idx + filter_width] += w[f] * dout[n, f, out_h, out_w]

    # Get rid of the padding
    dx = padded_dx[:, :, pad:pad + input_height, pad:pad + input_width]

    for n in range(b.shape[0]):
        db[n] = np.sum(dout[:, n, :, :])
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    return dx, dw, db


def max_pool_forward_naive(x, pool_param):
    """
    A naive implementation of the forward pass for a max pooling layer.

    Inputs:
    - x: Input data, of shape (N, C, H, W)
    - pool_param: dictionary with the following keys:
      - 'pool_height': The height of each pooling region
      - 'pool_width': The width of each pooling region
      - 'stride': The distance between adjacent pooling regions

    Returns a tuple of:
    - out: Output data
    - cache: (x, pool_param)
    """
    ###########################################################################
    # TODO: Implement the max pooling forward pass                            #
    ###########################################################################
    N = x.shape[0]
    C = x.shape[1]
    stride = pool_param['stride']

    input_height = x.shape[2]
    pool_height = pool_param['pool_height']
    output_height = int(1 + (input_height - pool_height) / stride)

    input_width = x.shape[3]
    pool_width = pool_param['pool_width']
    output_width = int(1 + (input_width - pool_width) / stride)

    output = np.zeros((N, C, output_height, output_width))
    for n in range(N):
        for c in range(C):
            for h in range(output_height):
                h_idx = h * stride
                for w in range(output_width):
                    w_idx = w * stride
                    output[n, c, h, w] = np.max(x[n, c, h_idx:h_idx + pool_height, w_idx:w_idx + pool_width])
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    cache = (x, pool_param)
    return output, cache


def max_pool_backward_naive(dout, cache):
    """
    A naive implementation of the backward pass for a max pooling layer.

    Inputs:
    - dout: Upstream derivatives
    - cache: A tuple of (x, pool_param) as in the forward pass.

    Returns:
    - dx: Gradient with respect to x
    """
    ###########################################################################
    # TODO: Implement the max pooling backward pass                           #
    ###########################################################################
    x, pool_param = cache

    N = x.shape[0]
    C = x.shape[1]
    stride = pool_param['stride']

    input_height = x.shape[2]
    pool_height = pool_param['pool_height']
    output_height = int(1 + (input_height - pool_height) / stride)

    input_width = x.shape[3]
    pool_width = pool_param['pool_width']
    output_width = int(1 + (input_width - pool_width) / stride)

    dx = np.zeros(x.shape)
    for n in range(N):
        for c in range(C):
            for h in range(output_height):
                h_idx = h * stride
                for w in range(output_width):
                    w_idx = w * stride
                    curr_pool = x[n, c, h_idx:h_idx + pool_height, w_idx:w_idx + pool_width]
                    max_idx = np.unravel_index(curr_pool.argmax(), curr_pool.shape)
                    dx[n, c][max_idx[0] + h_idx, max_idx[1] + w_idx] += 1 * dout[n, c, h, w]
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    return dx


def spatial_batchnorm_forward(x, gamma, beta, bn_param):
    """
    Computes the forward pass for spatial batch normalization.

    Inputs:
    - x: Input data of shape (N, C, H, W)
    - gamma: Scale parameter, of shape (C,)
    - beta: Shift parameter, of shape (C,)
    - bn_param: Dictionary with the following keys:
      - mode: 'train' or 'test'; required
      - eps: Constant for numeric stability
      - momentum: Constant for running mean / variance. momentum=0 means that
        old information is discarded completely at every time step, while
        momentum=1 means that new information is never incorporated. The
        default of momentum=0.9 should work well in most situations.
      - running_mean: Array of shape (D,) giving running mean of features
      - running_var Array of shape (D,) giving running variance of features

    Returns a tuple of:
    - out: Output data, of shape (N, C, H, W)
    - cache: Values needed for the backward pass
    """
    out, cache = None, None

    ###########################################################################
    # TODO: Implement the forward pass for spatial batch normalization.       #
    #                                                                         #
    # HINT: You can implement spatial batch normalization using the vanilla   #
    # version of batch normalization defined above. Your implementation should#
    # be very short; ours is less than five lines.                            #
    ###########################################################################
    N, C, height, width = x.shape
    # First step is to move height and width to the front and then flatten the first three layers
    flatten_x = x.transpose(0, 2, 3, 1).reshape((N * height * width, C))
    # Now we have an input matrix that is (D, C) with D = N * height * width
    out, cache = batchnorm_forward(flatten_x, gamma, beta, bn_param)
    out = out.reshape((N, height, width, C)).transpose(0, 3, 1, 2)
    # So what is this doing? We are comparing statistics across channels for each individual pixel and normalize w.r.t
    # the mean and variance across channels. If I have 100 10x10 images, then I have 10,000 pixels each with 3 channels.
    # These 10,000 pixels will receive normalization w.r.t the 3 channels, which I think is not doing much...However,
    # if we are using it on features, then C will be replaced by number of filters and that is useful. Normalizing across
    # MANY MANY filters gives good result.
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################

    return out, cache


def spatial_batchnorm_backward(dout, cache):
    """
    Computes the backward pass for spatial batch normalization.

    Inputs:
    - dout: Upstream derivatives, of shape (N, C, H, W)
    - cache: Values from the forward pass

    Returns a tuple of:
    - dx: Gradient with respect to inputs, of shape (N, C, H, W)
    - dgamma: Gradient with respect to scale parameter, of shape (C,)
    - dbeta: Gradient with respect to shift parameter, of shape (C,)
    """
    dx, dgamma, dbeta = None, None, None

    ###########################################################################
    # TODO: Implement the backward pass for spatial batch normalization.      #
    #                                                                         #
    # HINT: You can implement spatial batch normalization using the vanilla   #
    # version of batch normalization defined above. Your implementation should#
    # be very short; ours is less than five lines.                            #
    ###########################################################################
    N, C, height, width = dout.shape
    flatten_dout = dout.transpose(0, 2, 3, 1).reshape((N * height * width, C))
    dx, dgamma, dbeta = batchnorm_backward_alt(flatten_dout, cache)
    dx = dx.reshape((N, height, width, C)).transpose(0, 3, 1, 2)
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################

    return dx, dgamma, dbeta


def svm_loss(x, y):
    """
    Computes the loss and gradient using for multiclass SVM classification.

    Inputs:
    - x: Input data, of shape (N, C) where x[i, j] is the score for the jth
      class for the ith input.
    - y: Vector of labels, of shape (N,) where y[i] is the label for x[i] and
      0 <= y[i] < C

    Returns a tuple of:
    - loss: Scalar giving the loss
    - dx: Gradient of the loss with respect to x
    """
    N = x.shape[0]
    correct_class_scores = x[np.arange(N), y]
    margins = np.maximum(0, x - correct_class_scores[:, np.newaxis] + 1.0)
    margins[np.arange(N), y] = 0
    loss = np.sum(margins) / N
    num_pos = np.sum(margins > 0, axis=1)
    dx = np.zeros_like(x)
    dx[margins > 0] = 1
    dx[np.arange(N), y] -= num_pos
    dx /= N
    return loss, dx


def softmax_loss(x, y):
    """
    Computes the loss and gradient for softmax classification.

    Inputs:
    - x: Input data, of shape (N, C) where x[i, j] is the score for the jth
      class for the ith input.
    - y: Vector of labels, of shape (N,) where y[i] is the label for x[i] and
      0 <= y[i] < C

    Returns a tuple of:
    - loss: Scalar giving the loss
    - dx: Gradient of the loss with respect to x
    """
    shifted_logits = x - np.max(x, axis=1, keepdims=True)
    Z = np.sum(np.exp(shifted_logits), axis=1, keepdims=True)
    log_probs = shifted_logits - np.log(Z)
    probs = np.exp(log_probs)
    N = x.shape[0]
    loss = -np.sum(log_probs[np.arange(N), y]) / N
    dx = probs.copy()
    dx[np.arange(N), y] -= 1
    dx /= N
    return loss, dx
