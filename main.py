import warnings
from src.aircraft.aircraft import AircraftStability, StateSpaceModel
from src.flight_dynamics.Phugoid import Phugoid
from src.flight_dynamics.ShortPeriod import ShortPeriod
from src.autopilot.autopilot import AutoPilot
from src.misc.report_generator import GenerateReport

if __name__ == '__main__':
    aircraft = AircraftStability()
    alpha_eq = aircraft.compute_equilibrium()

    model = StateSpaceModel(aircraft)
    A, B, C, D, eigen_values = model.model()

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        sys, damping = model.control()



    # ------------------- Generate report -------------------
    write = GenerateReport(A, B, C, D, eigen_values, damping, sys)
    write.write("aircraft-report")
    # --------------------------------------------------------

    # ------------------- Short Period Response -------------------
    short_period = ShortPeriod(A, B)
    print(short_period.__str__())
    short_period.plot()
    # --------------------------------------------------------

    # ------------------- Phugoid Response -------------------
    phugoid = Phugoid(A, B)
    print(phugoid.__str__())
    phugoid.plot()
    # --------------------------------------------------------

    # ------------------- Auto Pilot -------------------
    auto_pilot = AutoPilot(A, B)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        Aq, Bq, Cq, Dq, eigen_q, damping_q, freq_q, closed_tf_ss_q = auto_pilot.compute_q_feedback()

    auto_pilot.plot_q_feedback(closed_tf_ss_q)

    # ------------------- Generate report -------------------
    write = GenerateReport(Aq, Bq, Cq, Dq, eigen_q, damping_q, freq_q)
    write.write("q-feedback")



