import pandas as pd
from ortools.sat.python import cp_model


class SchedulerCPsat:
    """
    Clase que genera la planeación semanal o mensual de turnos
    usando el solver CP-SAT de Google OR-Tools.
    """

    def __init__(self, asesores, dias_laborales, permitir_restriccion_apertura=False):
        """
        asesores: lista de nombres de asesores
        dias_laborales: lista de strings con los días (ej: ["Lunes","Martes",...])
        permitir_restriccion_apertura: bool para activar punto 2 de la prueba
        """
        self.asesores = asesores
        self.dias = dias_laborales
        self.turnos = ["Apertura", "Intermedio", "Cierre"]
        self.restriccion_apertura = permitir_restriccion_apertura

    def planificar_semana(self):
        """
        Genera la planeación de 1 semana sin rotación mensual.
        """

        model = cp_model.CpModel()

        # Variables: turno[a][t]
        # turno[a][t] = 1 si el asesor a tiene el turno t
        turno = {}
        for a in self.asesores:
            for t in self.turnos:
                turno[(a, t)] = model.NewBoolVar(f"{a}_{t}")

        # 1) Cada asesor debe tener EXACTAMENTE 1 turno
        for a in self.asesores:
            model.Add(sum(turno[(a, t)] for t in self.turnos) == 1)

        # 2) No puede haber más de un asesor en el mismo turno
        for t in self.turnos:
            model.Add(sum(turno[(a, t)] for a in self.asesores) == 1)

        # 3) Restricción opcional: una asesora sólo puede apertura
        if self.restriccion_apertura:
            asesora_fija = self.asesores[0]  # puedes cambiar si lo deseas
            model.Add(turno[(asesora_fija, "Apertura")] == 1)
            model.Add(turno[(asesora_fija, "Intermedio")] == 0)
            model.Add(turno[(asesora_fija, "Cierre")] == 0)

        # Resolver
        solver = cp_model.CpSolver()
        solver.Solve(model)

        # Construcción de DataFrame replicando la semana completa
        rows = []
        for dia in self.dias:
            for a in self.asesores:
                for t in self.turnos:
                    if solver.Value(turno[(a, t)]) == 1:
                        rows.append([dia, a, t])

        df = pd.DataFrame(rows, columns=["Día", "Asesor", "Turno"])
        return df

