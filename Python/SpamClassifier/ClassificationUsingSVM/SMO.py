""" This file contains the method of basic simplified version of Sequential minimal optimization algo just for
    Learning purpose based on John platt's paper which is available at
https://www.microsoft.com/en-us/research/publication/sequential-minimal-optimization-a-fast-algorithm-for-training-support-vector-machines/
for real practice or product development, an individual/party should use built in libraries.
"""

"""In this simplified SMO instead of choosing pair of lagrange multipliers to optimize by heuristics we are going to
 Choose them randomly.
"""

import numpy as mat
import random
from ClassificationUsingSVM import GaussianKernel


class simplifiedSMO:
    def __init__(self, X, Y, C, kernel):
        """
        This method creates objects of SimplifiedSMO Class.

        :param X: Input matrix
        :param Y: Output matrix
        :param C: Trade-off parameter
        :param kernel: Vectorized data which user can get using either linear_kernel method or gaussian_kernel method
                       in SMO file.
        """
        self.X = X
        self.Y = Y
        self.C = C
        self.kernel = kernel
        self.alphas = mat.zeros((X.shape[0], 1))
        self.b = 0
        self.tol = 0
        self.error = mat.zeros((X.shape[0], 1))
        self.W = mat.zeros((X.shape[1], 1))
        self.sigma = 0


def linear_kernel(X):
    """
    This method calculate the inner product using dot product of input matrix.

    :param X: Input matrix
    :return: Vectorised  output
    """
    return mat.dot(X, X.transpose())


def gaussian_kernel(X, sigma):
    """
    This method projects the Input matrix to higher dimension using gaussian/RBF kernel using Vectorised implementation.

    :param X: Input matrix
    :param sigma: kernel parameter
    :return: Vectorised Higher dimension matrix
    """
    X2 = mat.c_[mat.sum(mat.power(X, 2), 1)]
    kernel = mat.dot(X, X.transpose()) * -2 + X2.transpose() + X2
    kernel = mat.power(GaussianKernel.gaussian_kernel(1, 0, sigma), kernel)
    return kernel


def execute_SMO(model, max_passes):
    """
    This method starts the SMO.

    :param model: SimplifiedSMO class object
    :param max_passes: maximum passes user wants to use
    :return: model (SimplifiedSMO object contains updated parameters like Lagrange multipliers, weights etc)
    """
    model.tol = pow(10, -3)
    m = model.X.shape[0]
    passes = 0

    print("Calculating", end=" ")
    print_dots = 0
    while passes < max_passes:
        # this code is for printing dots on run screen so that user can see algo is running
        if print_dots > 100:
            print_dots = 0
            print("\n")
        print(".", end="")

        num_changed_alpha = 0
        for i in range(m):

            # calculate error on ith example
            model.error[i] = (mat.sum(
                mat.multiply(mat.multiply(model.alphas, model.Y), mat.c_[model.kernel[:, i]])) - model.b) - model.Y[i]
            r2 = model.Y[i] * model.error[i]

            # check for KKT condition
            if (r2 < -model.tol and model.alphas[i] < model.C) or (r2 > model.tol and model.alphas[i] > 0):
                j = int(mat.round((m * random.random()))) - 1

                while j == i: # if both examples are same choose another one
                    j = int(mat.round((m * random.random()))) - 1

                # calculate error on jth example
                model.error[j] = (mat.sum(
                    mat.multiply(mat.multiply(model.alphas, model.Y), mat.c_[model.kernel[:, j]])) - model.b) - model.Y[
                                     j]

                # store old alphas
                alpha_i_old = mat.asscalar(model.alphas[i])
                alpha_j_old = mat.asscalar(model.alphas[j])

                # compute bounds L and H
                if model.Y[i] == model.Y[j]:
                    L = max(0, (model.alphas[i] + model.alphas[j] - model.C))
                    H = min(model.C, (model.alphas[i] + model.alphas[j]))
                else:
                    L = max(0, (model.alphas[j] - model.alphas[i]))
                    H = min(model.C, (model.C + model.alphas[j] - model.alphas[i]))

                if L == H:
                    # return 0 and choose another example
                    continue

                # compute eta
                eta = (2 * model.kernel[i, j]) - model.kernel[i, i] - model.kernel[j, j]

                if eta >= 0:
                    # return 0 and choose another example
                    continue

                # Compute alpha_j new
                model.alphas[j] = model.alphas[j] - (model.Y[j] * (model.error[i] - model.error[j])) / eta

                # store the new alpha_j according to bound conditions described in the paper.
                model.alphas[j] = min(H, model.alphas[j])
                model.alphas[j] = max(L, model.alphas[j])

                if abs(model.alphas[j] - alpha_j_old) < model.tol: # if new alpha is almost same as old don't change it
                    # continue to next i
                    model.alphas[j] = alpha_j_old
                    continue

                # compute alpha_i_new
                model.alphas[i] = model.alphas[i] + (model.Y[i] * model.Y[j] * (alpha_j_old - model.alphas[j]))

                # compute b1 and b2

                b1 = model.b + model.error[i] - (model.Y[i] * (model.alphas[i] - alpha_i_old) * model.kernel[i, j]) - (
                        model.Y[j] * (
                        model.alphas[j] - alpha_j_old) * model.kernel[i, j])
                b2 = model.b + model.error[i] - (model.Y[i] * (model.alphas[i] - alpha_i_old) * model.kernel[i, j]) - (
                        model.Y[j] * (
                        model.alphas[j] - alpha_j_old) * model.kernel[j, j])

                # compute b (threshold)

                if 0 < model.alphas[i] < model.C:
                    model.b = b1
                elif 0 < model.alphas[j] < model.C:
                    model.b = b2
                    # when lagrange multipliers at bound that means all threshold between b1 and b2 satisfy KKT
                    # condition choose an average value
                else:
                    model.b = (b1 + b2) / 2

                num_changed_alpha = num_changed_alpha + 1 # if alpha updated add 1 to changed alphas

        if num_changed_alpha == 0:
            passes = passes + 1
        else:
            passes = 0
        print_dots = print_dots + 1

    # calculate weight vector
    model.W = mat.dot(mat.multiply(model.alphas, model.Y).transpose(), model.X).transpose()

    print("\nSMO finises")
    return model
