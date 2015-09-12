# Written by Ilias Bilionis
"""
Test if hyperparameters in models are properly transformed.
"""


import unittest
import numpy as np
import scipy.stats as st
import GPy

class TestModel(GPy.core.Model):
    """
    A simple GPy model with one parameter.
    """
    def __init__(self, name):
        GPy.core.Model.__init__(self, name)
        theta = GPy.core.Param('theta', 1.)
        self.link_parameter(theta)

    def log_likelihood(self):
        return 0.


class RVTransformationTestCase(unittest.TestCase):

    def _test_trans(self, trans, kde=True):
        m = TestModel(trans.__class__.__name__)
        prior = GPy.priors.LogGaussian(.5, 0.1)
        m.theta.set_prior(prior)
        m.theta.unconstrain()
        m.theta.constrain(trans)
        theta_s = prior.rvs(1e5)
        if kde:
            # The PDF of the transformed variables
            p_phi = lambda phi : np.exp(-m._objective_grads(phi)[0])
            # To the empirical PDF of:
            phi_s = trans.finv(theta_s)
            # which is essentially a kernel density estimation
            kde = st.gaussian_kde(phi_s)
            # We will compare the PDF here:
            phi = np.linspace(phi_s.min(), phi_s.max(), 100)
            # The transformed PDF of phi should be this:
            pdf_phi = np.array([p_phi(p) for p in phi])
            # The following test cannot be very accurate
            self.assertTrue(np.linalg.norm(pdf_phi - kde(phi)) / np.linalg.norm(kde(phi)) <= 1e-1)
        # UNCOMMENT TO SEE GRAPHICAL COMPARISON
        #import matplotlib.pyplot as plt
        #fig, ax = plt.subplots()
        #ax.hist(phi_s, normed=True, bins=100, alpha=0.25, label='Histogram')
        #ax.plot(phi, kde(phi), '--', linewidth=2, label='Kernel Density Estimation')
        #ax.plot(phi, pdf_phi, ':', linewidth=2, label='Transformed PDF')
        #ax.set_xlabel(r'transformed $\theta$', fontsize=16)
        #ax.set_ylabel('PDF', fontsize=16)
        #plt.legend(loc='best')
        #plt.show(block=True)
        # END OF PLOT
        # Check the gradients at a few random points
        np.random.seed(5)
        for i in range(5):
            #m.theta = theta_s[i]
            m.randomize()
            self.assertTrue(m.checkgrad(verbose=True))

    def test_Logexp(self):
        self._test_trans(GPy.constraints.Logexp())
    
    def test_Exponent(self):
        self._test_trans(GPy.constraints.Exponent())

    # def test_Logexpneg(self):
    #     self._test_trans(GPy.constraints.LogexpNeg(False))

    # def test_neglogexp(self):
    #     self._test_trans(GPy.constraints.NegativeLogexp(False))

    # def test_logexpclipped(self):
    #     self._test_trans(GPy.constraints.LogexpClipped())

    # def test_NegExp(self):
    #     self._test_trans(GPy.constraints.NegativeExponent(False))

    # def test_logexpNeg(self):
    #     self._test_trans(GPy.constraints.LogexpNeg(False))

    # def test_Square(self):
    #     self._test_trans(GPy.constraints.Square(False))

    # def test_logistic(self):
    #     self._test_trans(GPy.constraints.Logistic(False))

if __name__ == '__main__':
    unittest.main()
    quit()
    m = TestModel()
    prior = GPy.priors.LogGaussian(0., .9)
    m.theta.set_prior(prior)

    # The following should return the PDF in terms of the transformed quantities
    p_phi = lambda phi : np.exp(-m._objective_grads(phi)[0])

    # Let's look at the transformation phi = log(exp(theta - 1))
    trans = GPy.constraints.Exponent()
    m.theta.constrain(trans)
    # Plot the transformed probability density
    phi = np.linspace(-8, 8, 100)
    fig, ax = plt.subplots()
    # Let's draw some samples of theta and transform them so that we see
    # which one is right
    theta_s = prior.rvs(10000)
    # Transform it to the new variables
    phi_s = trans.finv(theta_s)
    # And draw their histogram
    ax.hist(phi_s, normed=True, bins=100, alpha=0.25, label='Empirical')
    # This is to be compared to the PDF of the model expressed in terms of these new
    # variables
    ax.plot(phi, [p_phi(p) for p in phi], label='Transformed PDF', linewidth=2)
    ax.set_xlim(-3, 10)
    ax.set_xlabel(r'transformed $\theta$', fontsize=16)
    ax.set_ylabel('PDF', fontsize=16)
    plt.legend(loc='best')
    # Now let's test the gradients
    m.checkgrad(verbose=True)
    # And show the plot
    plt.show(block=True)
