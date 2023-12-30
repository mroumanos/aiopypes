from abc import ABC, abstractclassmethod

from random import random

from copy import deepcopy


class AbstractLoadBalancer(ABC):
    
    @abstractclassmethod
    def __init__(self, *args, **kwargs):
        pass
    
    @abstractclassmethod
    def balance(self, *args) -> list:
        pass

    def copy(self):
        """
        The function `copy` returns a deep copy of the object it is called on.
        
        Returns:
          The `copy` method is returning a deep copy of the object `self`.
        """
        return deepcopy(self)


class BroadcastLoadBalancer(AbstractLoadBalancer):

    def __init__(self):

        self.counter = 0
    
    def balance(self, output: list):
        """
        The function takes in a list as input and returns the same list as output.
            
        Args:
          output (list): The "output" parameter is a list that contains the elements to be balanced.
        
        Returns:
          the "output" list.
        """

        return output


class RoundRobinLoadBalancer(AbstractLoadBalancer):

    def __init__(self):

        self.counter = 0
    
    def balance(self, output: list):
        """
        The `balance` function returns a list containing one element from the `output` list based on the
        current value of the `counter` variable.
        
        Args:
          output (list): The `output` parameter is a list that contains some elements.
        
        Returns:
          a list containing the element at the current index in the "output" list.
        """

        index = self.counter % len(output) #  to ensure in range in case output length changes

        self.counter += 1

        return [output[index]]


class RandomizedLoadBalancer(AbstractLoadBalancer):

    def __init__(self):

        pass

    def balance(self, output: list):
        """
        The function randomly selects and returns one element from the given list.
        
        Args:
          output (list): The `output` parameter is a list of values.
        
        Returns:
          a list containing a randomly selected element from the input list "output".
        """

        index = int(random() * len(output))

        return [output[index]]


class CongestionLoadBalancer(AbstractLoadBalancer):

    def __init__(self):

        pass

    def balance(self, output: list):
        """
        The `balance` function takes a list of objects and returns the object with the smallest input queue
        size.
        
        Args:
          output (list): The `output` parameter is a list of objects. Each object in the list has an
        attribute `input` which is an object with a `queue` attribute. The `queue` attribute represents a
        queue and has a method `qsize()` which returns the size of the queue.
        
        Returns:
          a list containing the object with the smallest input queue size.
        """

        if len(output) < 1:
            return []

        min_q = output[0]
        min_qsize = min_q.input.queue.qsize()
        qsizes = []
        for o in output:
            qsizes.append(o.input.queue.qsize())
            if o.input.queue.qsize() < min_qsize:
                min_qsize = o.input.queue.qsize()
                min_q = o

        return [min_q]


DefaultLoadBalancer = BroadcastLoadBalancer