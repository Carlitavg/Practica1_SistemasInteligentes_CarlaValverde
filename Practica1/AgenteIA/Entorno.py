class Entorno:

    def __init__(self):
        self.agentes = []

    def get_percepciones(self, agente):
        raise Exception("Se debe implementar el metodo")

    def ejecutar(self, agente):
        raise Exception("Se debe implementar el metodo")

    def finalizado(self):
        return not any(agente.habilitado for agente in self.agentes)

    def avanzar(self):
        for agente in self.agentes:
            self.get_percepciones(agente)
            self.ejecutar(agente)

    def run(self):
        while not self.finalizado():
            self.avanzar()

    def insertar(self, a):
        self.agentes.append(a)