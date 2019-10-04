from collections import namedtuple

# This is a sketch of the interfaces that each backend is expected to
# implement.
#
# Each backend makes use of a backend specific type called `ps`. For
# the pyro/numpyro backends this is torch tensors/numpy arrays
# respectively. (Note that we don't assume that this type will be
# iterable.)
#
#
# The `prior`, `nuts` & `svi` methods on `Backend` are all expected to
# return a `fit.Samples` instance. A `Samples` instance has the
# following methods:
#
# `Samples#raw_samples`
#
# The raw samples collected by inference. Not currently used.
#
# `Samples#get_param` :: string -> ps
#
# This returns all of the samples collected for a particular parameter
# (of the given name) as an instance of (backend specific) type `ps`.
# By parameter we mean something like "b", the vector of all
# population level coefficients. (The function `model.parameter_names`
# describes the set of parameters implied by a given model.
# `get_param` should support all of the parameter names returned by
# `model.parameter_names` for the current model.) e.g. For the Pyro
# backend this returns a torch tensor with shape number of samples by
# length of parameter.
#
# `Samples#location` :: dict string ps -> ps
#
# This take as argument a data set D (assumed to be compatible with
# the model and stored in the backend specific representation) and
# returns the value of `mu` (the output of the model before applying
# any inverse link function) for each combination of sample and
# element (data point) of D. (D may or may not be the data on which
# inference was performed.) For Pyro, this would return a torch tensor
# with shape number of samples by len(D).
#
#
# The methods `from_numpy` and `to_numpy` on `Backend` convert
# instances of the backend specific type `ps` from and to numpy
# arrays.
#
# Backend#from_numpy :: ndarray -> ps
# Backend#to_numpy :: ps -> ndarray
#
#
# The method `gen` on `Backend` takes a `model.ModelDesc` and produces
# a `Model` instance. A `Model` instance has the following methods:
#
# `fn`
#
# This is the method generated by the backend to represent the model.
# This isn't strictly part of the public interface, rather the backend
# will use this internally to perform inference. (However it's useful
# to be able to get at this for debugging.)
#
# `inv_link_fn` :: ps -> ps
#
# A method implementing the model's inverse link function. This is
# used by `fitted` to map (element-wise) the output of
# `fit.Samples#location` to the location parameter of the response
# distribution.
#
# `expected_response_fn` :: (ps, ps, ...) -> ps
#
#
# TODO: Explain the order of the arguments.
#
# A method that computes (element-wise) the mean of the response
# distribution of the model. It is expected that callers will ensure
# that one of the arguments will be a number of samples by number of
# data points collection of model outputs. (e.g. The output of
# `Samples#location`.) The expectation is that (internally) this will
# be passed through the inverse link function and used as the location
# parameter of the response distribution. For each of the remaining
# parameters of the response distribution the caller should also pass
# a number of samples by 1 collection of sampled parameter values.
# (The shapes differ because only the location parameter can depend on
# the data at present.) This method is used internally by `fitted`.
#
#
# `samples_response_fn`
#
# This is analogous to `expected_response_fn` but returning a sample
# rather than the expected value.


Backend = namedtuple('Backend', 'name gen prior nuts svi from_numpy to_numpy')

# Map `from_numpy` over a dict of numpy arrays, (As produced by e.g.
# `makedata`.)
def data_from_numpy(backend, data):
    assert type(backend) == Backend
    assert type(data) == dict
    return {k: backend.from_numpy(arr) for k, arr in data.items()}

# We could have a class that wraps a (function, code) pair, making the
# code available via a code property and the function available via
# __call__. `Model` could also be callable. Too cute?
Model = namedtuple('Model', [
    'fn', 'code',
    'inv_link_fn', 'inv_link_code',
    'expected_response_fn', 'expected_response_code',
    'sample_response_fn', 'sample_response_code',
])

def apply_default_hmc_args(iter, warmup, num_chains):
    iter = 10 if iter is None else iter
    warmup = iter // 2 if warmup is None else warmup
    num_chains = 1 if num_chains is None else num_chains
    return iter, warmup, num_chains
