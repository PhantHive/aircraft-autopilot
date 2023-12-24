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
    TqDm_tf = short_period.compute_tf_q()
    # --------------------------------------------------------

    # ------------------- Phugoid Response -------------------
    phugoid = Phugoid(A, B)
    print(phugoid.__str__())
    phugoid.plot()
    # --------------------------------------------------------

    # ------------------- Auto Pilot -------------------
    auto_pilot = AutoPilot(A, B)

    # q feedback
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        Aq, Bq, Cq, Dq, eigen_q, damping_q, freq_q, closed_tf_ss_q = auto_pilot.compute_q_feedback()

    auto_pilot.plot_q_feedback(closed_tf_ss_q)
    auto_pilot.plot_q_open_closed_loop(TqDm_tf)

    # 𝛾 feedback
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        Ag, Bg, Cg, Dg, eigen_g, damping_g, freq_g, closed_tf_ss_g = auto_pilot.compute_gamma_feedback(Aq, Bq, Cq, Dq)

    auto_pilot.plot_gamma_feedback(closed_tf_ss_g)

    # z feedback
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        Az, Bz, Cz, Dz, eigen_z, damping_z, freq_z, closed_tf_ss_z = auto_pilot.compute_z_feedback(Ag, Bg, Cg, Dg)

    auto_pilot.plot_z_feedback(closed_tf_ss_z)

    # ------------------- Generate report -------------------
    write = GenerateReport(Aq, Bq, Cq, Dq, eigen_q, damping_q, freq_q)
    write.write("q-feedback")

    write = GenerateReport(Ag, Bg, Cg, Dg, eigen_g, damping_g, freq_g)
    write.write("gamma-feedback")

    write = GenerateReport(Az, Bz, Cz, Dz, eigen_z, damping_z, freq_z)
    write.write("z-feedback")
    # --------------------------------------------------------

    getParams = aircraft.get_params()
    auto_pilot.compute_gamma_max(Ag, Bg, Cg, Dg, alpha_eq, getParams['alpha_0']['value'])




