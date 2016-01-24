class Person:

    def __init__(self, name, age, pay=0, job=None):
        self.name = name
        self.age = age
        self.pay = pay
        self.job = job

    def __str__(self):
        return '<%s => %s>' % (self.__class__.__name__, self.name)

    def lastName(self):
        return self.name.split()[-1]

    def giveRaise(self, percent):
        self.pay *= (1.0 + percent)


class Manager(Person):

    def giveRaise(self, percent, bonus=0.1):
        Person.giveRaise(self, percent + bonus)


if __name__ == '__main__':
    bob = Person('Bob Smith', 42, 30000, 'software')
    sue = Person('Sue Jones', 45, 40000, 'hardware')
    print(bob.name, sue.pay)

    print(bob.name.split()[-1])
    sue.pay *= 1.10
    print(sue.pay)
