class Person():
    """
    Enhanced personificaton 
    """

    def __init__(self, name, age=18, pay=0, job=None, *args, **kwargs):
        """
        Person initialization
        """
        self.name = name
        self.age = age
        self.pay = pay
        self.job = job

    def lastName(self):
        return self.name.split()[-1]

    def giveRaise(self, percent):
        self.pay *= (1.0 + percent)

    def __str__(self):
        return ('<%s => %s: %s y.o. // %s , %s>' %
                (self.__class__.__name__, self.name, self.age,
                 self.job, self.pay))
