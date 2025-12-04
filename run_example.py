from scheduler import SchedulerCPsat

if __name__ == "__main__":
    asesores = ["Ana", "Luis", "Carlos"]
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]

    scheduler = SchedulerCPsat(
        asesores=asesores,
        dias_laborales=dias,
        permitir_restriccion_apertura=False
    )

    df = scheduler.planificar_semana()
    print(df)

