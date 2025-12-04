# scheduler.py
from ortools.sat.python import cp_model
import pandas as pd
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
import traceback

SHIFT_MAP = {1: "Apertura", 2: "Intermedio", 3: "Cierre"}

class SchedulerError(Exception):
    pass

class SchedulerCPsat:
    """
    Scheduler mejorado que genera una planeación semanal (o multi-semana)
    usando OR-Tools CP-SAT.
    """

    def __init__(self, asesores, dias_laborales=None, permitir_restriccion_apertura=False):
        if len(asesores) != 3:
            raise ValueError("Este implemento asume exactamente 3 asesores.")
        self.asesores = list(asesores)
        # dias_laborales puede usarse solo para etiquetar filas si se desea,
        # pero el scheduler trabajará con fechas reales al usar start_date.
        self.dias_laborales = dias_laborales or ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado"]
        self.restriccion_apertura = permitir_restriccion_apertura

    def _week_dates(self, start_date, weeks, holidays):
        """
        Genera lista de semanas. Cada semana es lista de fechas (excluye domingos y feriados).
        start_date: date object
        weeks: int
        holidays: set of date objects
        """
        result = []
        current = start_date
        for w in range(weeks):
            week_dates = []
            for d in range(7):
                dt = current + timedelta(days=d)
                # Excluir domingos (weekday()==6)
                if dt.weekday() == 6:
                    continue
                if dt in holidays:
                    continue
                week_dates.append(dt)
            result.append(week_dates)
            current = current + timedelta(days=7)
        return result

    def planificar_semanas(self,
                          start_date=None,
                          weeks=1,
                          holidays=None,
                          enforce_open_only_for=None,
                          enforce_open_only_flag=False,
                          rotation_between_weeks=False,
                          solver_time_limit_seconds=10):
        """
        Genera planificación para `weeks` semanas empezando desde `start_date`.
        - start_date: string 'YYYY-MM-DD' o datetime.date. Si None -> hoy.
        - holidays: list of 'YYYY-MM-DD' strings o datetime.date objects.
        - enforce_open_only_for: nombre del asesor que sólo puede Apertura (si enciendes flag).
        - rotation_between_weeks: si True, impide que un asesor repita su mismo turno semana a semana.
        Retorna pandas.DataFrame con columnas: Week, Date, Advisor, ShiftId, ShiftName
        """
        try:
            if start_date is None:
                start = datetime.today().date()
            elif isinstance(start_date, str):
                start = parse_date(start_date).date()
            else:
                start = start_date

            if holidays is None:
                holidays_set = set()
            else:
                parsed = []
                for h in holidays:
                    if isinstance(h, str):
                        parsed.append(parse_date(h).date())
                    else:
                        parsed.append(h)
                holidays_set = set(parsed)

            # Preparar fechas por semana (excluye domingos/feriados)
            weeks_dates = self._week_dates(start, weeks, holidays_set)

            # Modelo CP-SAT
            model = cp_model.CpModel()

            # Variables: shift for each (week, advisor) as IntVar 1..3
            shift_vars = {}
            for w in range(weeks):
                for a_idx in range(len(self.asesores)):
                    v = model.NewIntVar(1, 3, f"w{w}_a{a_idx}_shift")
                    shift_vars[(w, a_idx)] = v
                # Cobertura: los 3 asesores deben cubrir los 3 turnos (todos diferentes)
                model.AddAllDifferent([shift_vars[(w, ai)] for ai in range(len(self.asesores))])

            # Restricción: asesora que solo puede Apertura (si aplica)
            if enforce_open_only_flag:
                if enforce_open_only_for is None:
                    raise SchedulerError("Flag de apertura activada pero no se proporcionó nombre del asesor.")
                if enforce_open_only_for not in self.asesores:
                    raise SchedulerError(f"Asesor '{enforce_open_only_for}' no pertenece a la lista de asesores.")
                a_idx = self.asesores.index(enforce_open_only_for)
                for w in range(weeks):
                    model.Add(shift_vars[(w, a_idx)] == 1)  # 1 -> Apertura

            # Rotación entre semanas (si aplica)
            if rotation_between_weeks and weeks > 1:
                for w in range(weeks - 1):
                    for a_idx in range(len(self.asesores)):
                        model.Add(shift_vars[(w, a_idx)] != shift_vars[(w + 1, a_idx)])

            # Parámetros del solver
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = solver_time_limit_seconds
            solver.parameters.num_search_workers = 8

            status = solver.Solve(model)
            if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                raise SchedulerError("No se encontró solución factible con las restricciones dadas.")

            # Construir DataFrame: cada fecha de la semana recibe el mismo turno (por requerimiento)
            rows = []
            for w_idx, week_dates in enumerate(weeks_dates):
                for dt in week_dates:
                    for a_idx, a_name in enumerate(self.asesores):
                        shift_id = int(solver.Value(shift_vars[(w_idx, a_idx)]))
                        rows.append({
                            "Week": w_idx + 1,
                            "Date": dt.isoformat(),
                            "Advisor": a_name,
                            "ShiftId": shift_id,
                            "ShiftName": SHIFT_MAP[shift_id]
                        })

            df = pd.DataFrame(rows)
            # ordenar por Week, Date, Advisor
            df = df.sort_values(by=["Week", "Date", "Advisor"]).reset_index(drop=True)
            return df

        except Exception as e:
            tb = traceback.format_exc()
            raise SchedulerError(f"Error en planificar_semanas: {e}\n{tb}") from e


