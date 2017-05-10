import copy
import numpy as np


def rand(lower, upper):
    return (upper - lower) * np.random.random() + lower


def sigmoid(x):
    output = 1 / (1 + np.exp(-x))
    return output


def sigmoid_derivative(y):
    return y * (1 - y)


def make_mat(m, n, fill=0.0):
    mat = []
    for i in range(m):
        mat.append([fill] * n)
    return np.array(mat)


def make_rand_mat(m, n, lower=-1, upper=1):
    mat = []
    for i in range(m):
        mat.append([rand(lower, upper)] * n)
    return np.array(mat)


def int_to_bin(x, dim=0):
    x = bin(x)[2:]
    # align
    k = dim - len(x)
    if k > 0:
        x = "0" * k + x
    return x


class LSTM:
    def __init__(self):
        self.input_n = 0
        self.hidden_n = 0
        self.output_n = 0
        self.input_weights = []  # (input, hidden)
        self.output_weights = []  # (hidden, output)
        self.hidden_weights = []  # (hidden, hidden)

    def setup(self, ni, nh, no):
        self.input_n = ni
        self.hidden_n = nh
        self.output_n = no
        self.input_weights = make_rand_mat(self.input_n, self.hidden_n)
        self.output_weights = make_rand_mat(self.hidden_n, self.output_n)
        self.hidden_weights = make_rand_mat(self.hidden_n, self.hidden_n)

    def predict(self, case, dim=0):
        guess = np.zeros(dim)
        hidden_layer_history = [np.zeros(self.hidden_n)]

        for position in range(dim):
            x = np.array([[c[dim - position - 1] for c in case]])

            hidden_layer = sigmoid(np.dot(x, self.input_weights) + np.dot(hidden_layer_history[-1], self.hidden_weights))
            output_layer = sigmoid(np.dot(hidden_layer, self.output_weights))
            guess[dim - position - 1] = np.round(output_layer[0][0])  # if you don't like int, change it

            hidden_layer_history.append(copy.deepcopy(hidden_layer))

        return guess

    def train(self, case, label, dim=0, learn=0.1):
        input_updates = np.zeros_like(self.input_weights)
        output_updates = np.zeros_like(self.output_weights)
        hidden_updates = np.zeros_like(self.hidden_weights)

        guess = np.zeros_like(label)
        error = 0

        output_deltas = []
        hidden_layer_history = [np.zeros(self.hidden_n)]

        for position in range(dim):
            x = np.array([[c[dim - position - 1] for c in case]])
            y = np.array([[label[dim - position - 1]]]).T

            hidden_layer = sigmoid(np.dot(x, self.input_weights) + np.dot(hidden_layer_history[-1], self.hidden_weights))
            output_layer = sigmoid(np.dot(hidden_layer, self.output_weights))

            output_error = y - output_layer
            output_deltas.append(output_error * sigmoid_derivative(output_layer))
            error += np.abs(output_error[0])

            guess[dim - position - 1] = np.round(output_layer[0][0])

            hidden_layer_history.append(copy.deepcopy(hidden_layer))

        future_layer_1_delta = np.zeros(self.hidden_n)
        for position in range(dim):
            x = np.array([[c[position] for c in case]])
            hidden_layer = hidden_layer_history[-position - 1]
            prev_layer_1 = hidden_layer_history[-position - 2]

            # error at output layer
            layer_2_delta = output_deltas[-position - 1]
            # error at hidden layer
            layer_1_delta = (future_layer_1_delta.dot(self.hidden_weights.T) +
                             layer_2_delta.dot(self.output_weights.T)) * sigmoid_derivative(hidden_layer)
            # let's update all our weights so we can try again
            output_updates += np.atleast_2d(hidden_layer).T.dot(layer_2_delta)
            hidden_updates += np.atleast_2d(prev_layer_1).T.dot(layer_1_delta)
            input_updates += x.T.dot(layer_1_delta)

            future_layer_1_delta = layer_1_delta

        self.input_weights += input_updates * learn
        self.output_weights += output_updates * learn
        self.hidden_weights += hidden_updates * learn

        return guess, error

    def test(self):
        self.setup(2, 16, 1)
        for i in range(20000):
            # generate a simple addition problem (a + b = c)
            a_int = int(rand(0, 127))
            a = int_to_bin(a_int, dim=8)
            a = np.array([int(t) for t in a])

            b_int = int(rand(0, 127))
            b = int_to_bin(b_int, dim=8)
            b = np.array([int(t) for t in b])

            # true answer
            c_int = a_int + b_int
            c = int_to_bin(c_int, dim=8)
            c = np.array([int(t) for t in c])

            guess, error = self.train([a, b], c, dim=8)

            if i % 1000 == 0:
                print("Error:" + str(error))
                print("Predict:" + str(guess))
                print("True:" + str(c))
                out = 0
                for index, x in enumerate(reversed(guess)):
                    out += x * pow(2, index)
                print str(a_int) + " + " + str(b_int) + " = " + str(out)

                result = str(self.predict([a, b], dim=8))
                print(result)

                print "==============="

if __name__ == '__main__':
    nn = LSTM()
    nn.test()
