class Agente:

    def __init__(self):
        self.percepcion = None
        self.acciones = None
        self.habilitado = True

    def esta_habilitado(self):
        return self.habilitado

    def programa(self):
        raise Exception("Se debe implementar la funcion")