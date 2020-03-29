class PhysicsFloat(float):
    def __repr__(self):
        return f'{self.__class__.__name__}<{self.real}>'

    def __str__(self):
        return f'{self.__class__.__name__}<{self.real}>'

class Acceleration(PhysicsFloat):
    pass

class Mass(PhysicsFloat):
    pass

class Force(PhysicsFloat):
    def __truediv__(self, value):
        divvalue = self.real / value
        if value.__class__ == Mass:
            return Acceleration(divvalue)

        return divvalue


