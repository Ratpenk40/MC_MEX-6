#!/usr/bin/python
import sys, getopt
import numpy as np

from scipy import optimize
import os
import matplotlib.pyplot as plt

import module_2Dplotter as plotter2D
import module_2Dplotter_PLK1 as plotter2DPLK1
import module_2Dplotter_MEX6 as plotter2DMEX6
from datetime import datetime


class eloG:
    def __init__(self, filename):
        self.log_open(filename)
        self.name = filename

    def log_open(self, name):
        self.file = open(name, "w+")

    def log_open_append(self):
        self.file = open(self.name, "a+")

    def writeLine(self, string):
        self.file.write(string)
        self.file.write("\n")

    def writeListRow(self, lista):
        for item in lista:
            self.file.write(str(item))
            self.file.write("\t")
        self.file.write("\n")

    def writeListCol(self, lista):
        for item in lista:
            self.file.write(str(item))
            self.file.write("\n")

    def closeFile(self):
        self.file.close()


# Start here
def main(argv):
    print("Starting...")

    # define vel and k param
    v_mex5_fast = 0.0
    v_mex5_slow = 0.0
    v_plk1 = 0.0
    plk1_to_mex5 = 0.0

    if not os.path.exists("logs"):
        os.makedirs("logs")

    now = datetime.now()
    date_time = now.strftime("%d_%m_%Y_%H_%M_%S")
    print("Start time: ", date_time)

    if not os.path.exists("logs/" + date_time):
        os.makedirs("logs/" + date_time)

    # creating the different variables for the log files, maybe do a f"{}" here to create the filess
    # from a list with the name
    file_log_name = "logs/" + date_time + "/summary_parameter.txt"
    file_log_name_k_plk1 = "logs/" + date_time + "/log_k_plk1.txt"
    file_log_name_k_mex5 = "logs/" + date_time + "/log_k_mex5.txt"
    file_log_name_k_mex6 = "logs/" + date_time + "/log_k_mex6.txt"
    file_log_name_profile_mex5 = "logs/" + date_time + "/log_profileAP_mex5.txt"
    file_log_name_profile_mex6 = "logs/" + date_time + "/log_profileAP_mex6.txt"
    file_log_name_profile_plk1 = "logs/" + date_time + "/log_profileAP_plk1.txt"
    file_log_name_mex5_ratio_slow_fast = (
        "logs/" + date_time + "/log_mex5_ratio_slow_fast.txt"
    )
    file_log_name_mex6_ratio_slow_fast = (
        "logs/" + date_time + "/log_mex6_ratio_slow_fast.txt"
    )

    file_log_v_mex5 = "logs/" + date_time + "/log_v_mex5.txt"
    file_log_v_mex6 = "logs/" + date_time + "/log_v_mex6.txt"
    file_log_v_plk1 = "logs/" + date_time + "/log_v_plk1.txt"
    file_log_conc_id0_mex5 = "logs/" + date_time + "/conc_id0_mex5.txt"
    file_log_conc_id1_mex5 = "logs/" + date_time + "/conc_id1_mex5.txt"
    file_log_conc_id0_mex6 = "logs/" + date_time + "/conc_id0_mex6.txt"
    file_log_conc_id1_mex6 = "logs/" + date_time + "/conc_id1_mex6.txt"

    file_log_conc_id0_plk1 = "logs/" + date_time + "/conc_id0_plk1.txt"
    file_log_conc_id1_plk1 = "logs/" + date_time + "/conc_id1_plk1.txt"
    file_log_conc_id2_plk1 = "logs/" + date_time + "/conc_id2_plk1.txt"

    # initializing variables with default values
    particles = 0
    settings = ""
    bound = False
    plk1 = False
    mex6 = False
    threeD = False
    sliced = True
    drawMovie = False

    slice_depth = 0.0
    initial_slow = 0.0
    initial_fast = 0.0
    k_fast_slow_mex5 = 0.1
    k_slow_fast_low_mex5 = 0.02
    k_slow_fast_high_mex5 = 0.11

    k_plk1_attach_to_free = 0.0
    plk1_attach_to_mex_fast = 0
    plk1_attach_to_mex_slow = 1
    plk1_to_mex_multiplicator = 1
    plk1_detached_when_mex5_changes = 0

    plk1_delay_start_time = 0.0
    plk1_delay_end_time = 100.0

    # getting the arguments and options fromt the terminal command
    try:
        opts, args = getopt.getopt(
            argv,
            "hp:bfmds:",
            [
                "particles=",
                "bound",
                "mex6",
                "plk1",
                "threeD",
                "slice",
                "drawMovie",
                "settings=",
            ],
        )
    except getopt.GetoptError:
        print("test.py -p <particles>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("test.py -p <particles> ")  # do a better help output
            sys.exit()
        elif opt in ("-p", "--particles"):
            particles = int(arg)
        elif opt in ("-b", "--bound"):
            bound = True
        elif opt in ("--plk1"):
            plk1 = True
        elif opt in ("--mex6"):
            mex6 = True
        elif opt in ("--threeD"):
            threeD = True
        elif opt in ("--drawMovie"):
            drawMovie = True
        elif opt in ("s", "--settings"):
            settings = str(arg)
        elif opt in ("f", "--slice"):
            sliced = True

    assert settings != "", "A settings file is needed!"
    if sliced == True:
        assert threeD == True, "Impossible to use slice option without threeD set"

    # Reading and setting parameters from setting file
    f_sett = open(settings)
    lines = f_sett.readlines()
    temp_sett = []
    assert len(lines) == 24, "24 lines are expected"
    for line in lines:
        temp_sett.append(float(line.replace("\n", "").split("\t")[1]))
    f_sett.close()
    print(temp_sett)
    v_mex5_fast = temp_sett[0]
    v_mex5_slow = temp_sett[1]
    v_mex6_fast = temp_sett[2]
    v_mex6_slow = temp_sett[3]
    v_plk1 = temp_sett[4]
    plk1_to_mex5 = temp_sett[5]
    slice_depth = temp_sett[6]
    initial_slow_mex5 = temp_sett[7]
    initial_fast_mex5 = temp_sett[8]

    initial_slow_mex6 = temp_sett[9]
    initial_fast_mex6 = temp_sett[10]

    k_fast_slow_mex5 = temp_sett[11]
    k_slow_fast_low_mex5 = temp_sett[12]
    k_slow_fast_high_mex5 = temp_sett[13]

    k_fast_slow_mex6 = temp_sett[14]
    k_slow_fast_low_mex6 = temp_sett[15]
    k_slow_fast_high_mex6 = temp_sett[16]

    k_plk1_attach_to_free = temp_sett[17]
    plk1_attach_to_mex_slow = temp_sett[18]
    plk1_attach_to_mex_fast = temp_sett[19]
    plk1_to_mex_multiplicator = temp_sett[20]
    plk1_detached_when_mex5_changes = temp_sett[21]

    plk1_delay_start_time = temp_sett[22]
    plk1_delay_end_time = temp_sett[23]

    assert (
        v_mex5_fast != 0.0
        and v_mex5_slow != 0.0
        and v_plk1 != 0.0
        and plk1_to_mex5 != 0.0
    ), "something went wrong in reading the setting file"

    # Creating the log file with the summary of parameters
    log = eloG(file_log_name)
    log.writeLine("Starting simulation ")
    log.writeLine("N. particles " + str(particles))
    log.writeLine("bound " + str(bound))
    log.writeLine("mex6 " + str(mex6))
    log.writeLine("plk1 " + str(plk1))
    log.writeLine("threeD " + str(threeD))
    log.writeLine("slice " + str(sliced))
    log.writeLine("sliceDepth " + str(slice_depth))
    log.writeLine("setting file " + str(settings))
    log.writeLine("setting file " + str(settings))
    log.writeLine("v fast mex5 " + str(v_mex5_fast))
    log.writeLine("v slow mex5 " + str(v_mex5_slow))
    log.writeLine("v fast mex6 " + str(v_mex6_fast))
    log.writeLine("v slow mex6 " + str(v_mex6_slow))
    log.writeLine("v plk1 " + str(v_plk1))
    log.writeLine("plk1_to_mex5 " + str(plk1_to_mex5))
    log.writeLine("initial_slow_mex5 " + str(initial_slow_mex5))
    log.writeLine("initial_fast_mex5 " + str(initial_fast_mex5))
    log.writeLine("initial_slow_mex6 " + str(initial_slow_mex6))
    log.writeLine("initial_fast_mex6 " + str(initial_fast_mex6))
    log.writeLine("k_fast_slow_mex5 " + str(k_fast_slow_mex5))
    log.writeLine("k_slow_fast_low_mex5 " + str(k_slow_fast_low_mex5))
    log.writeLine("k_slow_fast_high_mex5 " + str(k_slow_fast_high_mex5))
    log.writeLine("k_fast_slow_mex6 " + str(k_fast_slow_mex6))
    log.writeLine("k_slow_fast_low_mex6 " + str(k_slow_fast_low_mex6))
    log.writeLine("k_slow_fast_high_mex6" + str(k_slow_fast_high_mex6))
    log.writeLine("k_plk1_attach_to_free " + str(k_plk1_attach_to_free))
    log.writeLine("plk1_attach_to_mex_fast " + str(plk1_attach_to_mex_fast))
    log.writeLine("plk1_attach_to_mex_slow " + str(plk1_attach_to_mex_slow))
    log.writeLine("plk1_to_mex_multiplicator " + str(plk1_to_mex_multiplicator))
    log.writeLine(
        "plk1_detached_when_mex5_changes " + str(plk1_detached_when_mex5_changes)
    )

    log.writeLine("plk1_delay_start_time " + str(plk1_delay_start_time))
    log.writeLine("plk1_delay_end_time " + str(plk1_delay_end_time))

    log.writeLine("log k mex5 " + str(file_log_name_k_mex5))
    log.writeLine("log k plk1 " + str(file_log_name_k_plk1))
    log.writeLine("log profile mex5 " + str(file_log_name_profile_mex5))
    log.writeLine("log profile plk1 " + str(file_log_name_profile_plk1))
    log.writeLine(
        "log profile ratio slow/fast " + str(file_log_name_mex5_ratio_slow_fast)
    )
    log.writeLine("log v mex5 " + str(file_log_v_mex5))
    log.writeLine("log v plk1 " + str(file_log_v_plk1))

    log.writeLine("log conc id0 mex5 " + str(file_log_conc_id0_mex5))
    log.writeLine("log conc id1 mex5 " + str(file_log_conc_id1_mex5))
    log.writeLine("log conc id0 plk1 " + str(file_log_conc_id0_plk1))
    log.writeLine("log conc id1 plk1 " + str(file_log_conc_id1_plk1))
    log.writeLine("log conc id2 plk1" + str(file_log_conc_id2_plk1))
    log.closeFile()

    # Limits of the embryo
    limits_particle = []
    limits = [[0, 0], [50, 30]]
    limits2 = [[0, 0], [50, 30]]
    limits3 = [[0, 50], [0, 50]]  # strange
    limits3D = [[0, 0, 0], [50, 30, 30]]

    if threeD:
        import particle3D_manager as pm
        import particle3D_managerPLK1 as pm_plk1
        import particle3D_managerMEX6 as pm_mex6

        limits_particle = [0, 0, 0, 50, 30, 30]

    else:  # 2D is deprecated
        import module_particle as particle_m
        import module_particle_plk1 as particle_plk1_m

        limits_particle = limits2

    # creating MEX-5 output files
    log_k_mex5 = eloG(file_log_name_k_mex5)
    log_profile_mex5 = eloG(file_log_name_profile_mex5)
    log_mex5_ratio_slow_fast = eloG(file_log_name_mex5_ratio_slow_fast)
    log_v_mex5 = eloG(file_log_v_mex5)
    log_conc_id0_mex5 = eloG(file_log_conc_id0_mex5)
    log_conc_id1_mex5 = eloG(file_log_conc_id1_mex5)

    log_k_mex5.closeFile()
    log_profile_mex5.closeFile()
    log_mex5_ratio_slow_fast.closeFile()
    log_v_mex5.closeFile()
    log_conc_id0_mex5.closeFile()
    log_conc_id1_mex5.closeFile()

    # creating MEX-6 output files
    if mex6:
        log_k_mex6 = eloG(file_log_name_k_mex6)
        log_profile_mex6 = eloG(file_log_name_profile_mex6)
        log_mex6_ratio_slow_fast = eloG(file_log_name_mex6_ratio_slow_fast)
        log_v_mex6 = eloG(file_log_v_mex6)
        log_conc_id0_mex6 = eloG(file_log_conc_id0_mex6)
        log_conc_id1_mex6 = eloG(file_log_conc_id1_mex6)

        log_k_mex6.closeFile()
        log_profile_mex6.closeFile()
        log_mex6_ratio_slow_fast.closeFile()
        log_v_mex6.closeFile()
        log_conc_id0_mex6.closeFile()
        log_conc_id1_mex6.closeFile()

    # creating PLK-1 output files
    if plk1:
        log_profile_plk1 = eloG(file_log_name_profile_plk1)
        log_k_plk1 = eloG(file_log_name_k_plk1)
        log_v_plk1 = eloG(file_log_v_plk1)
        log_conc_id0_plk1 = eloG(file_log_conc_id0_plk1)
        log_conc_id1_plk1 = eloG(file_log_conc_id1_plk1)
        log_conc_id2_plk1 = eloG(file_log_conc_id2_plk1)

        log_profile_plk1.closeFile()
        log_k_plk1.closeFile()
        log_v_plk1.closeFile()
        log_conc_id0_plk1.closeFile()
        log_conc_id1_plk1.closeFile()
        log_conc_id2_plk1.closeFile()

    # Fill the particle list
    particle_family = pm.particle3D_manager(particles)

    if mex6:
        particle_family_mex6 = pm_mex6.particle3D_managerMEX6(particles)

    if plk1:
        particle_family_plk1 = pm_plk1.particle3D_managerPLK1(particles)

    particle_family.SetSettings(
        initial_slow_mex5,
        initial_fast_mex5,
        k_fast_slow_mex5,
        k_slow_fast_low_mex5,
        k_slow_fast_high_mex5,
    )

    particle_family.Shuffle(limits_particle)

    if mex6:
        particle_family_mex6.SetSettings(
            initial_slow_mex6,
            initial_fast_mex6,
            k_fast_slow_mex6,
            k_slow_fast_low_mex6,
            k_slow_fast_high_mex6,
        )
        particle_family_mex6.Shuffle(limits_particle)

    if plk1:
        particle_family_plk1.SetSettings(
            plk1_attach_to_mex_slow,
            plk1_attach_to_mex_fast,
            k_plk1_attach_to_free,
            plk1_detached_when_mex5_changes,
            plk1_delay_start_time,
            plk1_delay_end_time,
        )
        particle_family_plk1.Shuffle(limits_particle)
        particle_family_plk1.Mex5SetSettings(
            k_fast_slow_mex5, k_slow_fast_low_mex5, k_slow_fast_high_mex5
        )

    plots = plotter2D.Plot2D(
        particles, limits3, limits, v_mex5_slow, v_mex5_fast, "logs/" + date_time
    )

    if mex6:
        plots_mex6 = plotter2DMEX6.Plot2D(
            particles, limits3, limits, v_mex6_slow, v_mex6_fast, "logs/" + date_time
        )

    if plk1:
        plots_plk1 = plotter2DPLK1.Plot2D(
            particles,
            limits3,
            limits,
            plk1_to_mex_multiplicator,
            v_plk1,
            v_mex5_slow,
            v_mex5_fast,
            "logs/" + date_time,
        )

    # Get info from cpp libraries
    X_list = list(particle_family.GetXpos())
    Y_list = list(particle_family.GetYpos())
    Z_list = list(particle_family.GetZpos())
    plots.UpdateCpp(X_list, Y_list, Z_list, sliced, slice_depth)

    if mex6:
        X_list_mex6 = list(particle_family_mex6.GetXpos())
        Y_list_mex6 = list(particle_family_mex6.GetYpos())
        Z_list_mex6 = list(particle_family_mex6.GetZpos())
        plots_mex6.UpdateCpp(X_list_mex6, Y_list_mex6, Z_list_mex6, sliced, slice_depth)

    if plk1:  # i think it should be particle_family_plk1
        X_list = list(particle_family.GetXpos())
        Y_list = list(particle_family.GetYpos())
        Z_list = list(particle_family.GetZpos())
        plots_plk1.UpdateCpp(X_list, Y_list, Z_list, sliced, slice_depth)

    for i in range(0, 1500):
        print("starting evt" + str(datetime.now().time()))  # time object

        particle_family.Move(v_mex5_slow, v_mex5_fast, 1, limits_particle, bound, i)

        X_list = list(particle_family.GetXpos())
        Y_list = list(particle_family.GetYpos())
        Z_list = list(particle_family.GetZpos())
        ID_list = list(particle_family.GetID())

        # concid0 = mex_5 slow; concid1 = mex_5 fast
        ratio, concid0, concid1, vel = plots.conc_calcCpp(
            X_list, Y_list, Z_list, ID_list
        )

        concid0 = (np.array(concid0) * plk1_to_mex_multiplicator).tolist()
        concid1 = (np.array(concid1) * plk1_to_mex_multiplicator).tolist()

        if mex6:
            particle_family_mex6.Move(
                v_mex6_slow, v_mex6_fast, 1, limits_particle, bound, i
            )

            X_list_mex6 = list(particle_family_mex6.GetXpos())
            Y_list_mex6 = list(particle_family_mex6.GetYpos())
            Z_list_mex6 = list(particle_family_mex6.GetZpos())
            ID_list_mex6 = list(particle_family_mex6.GetID())

            ratio_mex6, concid0_mex6, concid1_mex6, vel_mex6 = plots_mex6.conc_calcCpp(
                X_list, Y_list_mex6, Z_list_mex6, ID_list_mex6
            )

        if plk1:
            particle_family_plk1.Move(
                v_plk1,
                v_mex5_slow,
                v_mex5_fast,
                1,
                ratio,
                concid0,
                concid1,
                limits_particle,
                bound,
                i,
            )

            # it is defined as follow: v standard, v_fast, v_slow, k_probability, dt, limits, nobound

            X_list_plk1 = list(particle_family_plk1.GetXpos())
            Y_list_plk1 = list(particle_family_plk1.GetYpos())
            Z_list_plk1 = list(particle_family_plk1.GetZpos())
            ID_list_plk1 = list(particle_family_plk1.GetID())

            conc1, conc2, conc3, v_plk1_average = plots_plk1.conc_calcCpp(
                X_list_plk1, Y_list_plk1, Z_list_plk1, ID_list_plk1
            )

        if i != 0 and i % 10 == 0:
            X_list = list(
                particle_family.GetXpos()
            )  # this can be removed I think because declared before
            Y_list = list(particle_family.GetYpos())
            Z_list = list(particle_family.GetZpos())
            plots.UpdateCpp(X_list, Y_list, Z_list, sliced, slice_depth)

            if drawMovie:
                plots.FillDrawMovie()

            log_k_mex5.log_open_append()
            log_profile_mex5.log_open_append()
            log_mex5_ratio_slow_fast.log_open_append()
            log_v_mex5.log_open_append()
            log_conc_id0_mex5.log_open_append()
            log_conc_id1_mex5.log_open_append()

            log_k_mex5.writeLine(str(plots.klast))
            log_profile_mex5.writeListRow(plots.profilelast)
            log_mex5_ratio_slow_fast.writeListRow(ratio)
            log_v_mex5.writeListRow(vel)

            log_conc_id0_mex5.writeListRow(concid0)
            log_conc_id1_mex5.writeListRow(concid1)

            log_k_mex5.closeFile()
            log_profile_mex5.closeFile()
            log_mex5_ratio_slow_fast.closeFile()
            log_v_mex5.closeFile()

            log_conc_id0_mex5.closeFile()
            log_conc_id1_mex5.closeFile()

            if mex6:
                log_k_mex6.log_open_append()
                log_profile_mex6.log_open_append()
                log_mex6_ratio_slow_fast.log_open_append()
                log_v_mex6.log_open_append()
                log_conc_id0_mex6.log_open_append()
                log_conc_id1_mex6.log_open_append()

                log_k_mex6.writeLine(str(plots_mex6.klast))
                log_profile_mex6.writeListRow(plots_mex6.profilelast)
                log_mex6_ratio_slow_fast.writeListRow(ratio_mex6)
                log_v_mex6.writeListRow(vel_mex6)

                log_conc_id0_mex6.writeListRow(concid0_mex6)
                log_conc_id1_mex6.writeListRow(concid1_mex6)

                log_k_mex6.closeFile()
                log_profile_mex6.closeFile()
                log_mex6_ratio_slow_fast.closeFile()
                log_v_mex6.closeFile()

                log_conc_id0_mex6.closeFile()
                log_conc_id1_mex6.closeFile()

            if plk1:
                log_k_plk1.log_open_append()
                log_profile_plk1.log_open_append()
                log_v_plk1.log_open_append()
                log_conc_id0_plk1.log_open_append()
                log_conc_id1_plk1.log_open_append()
                log_conc_id2_plk1.log_open_append()

                plots_plk1.UpdateCpp(
                    X_list_plk1, Y_list_plk1, Z_list_plk1, sliced, slice_depth
                )

                log_conc_id0_plk1.writeListRow(conc3)
                log_conc_id1_plk1.writeListRow(conc1)
                log_conc_id2_plk1.writeListRow(conc2)

                log_k_plk1.writeLine(str(plots_plk1.klast))
                log_profile_plk1.writeListRow(plots_plk1.profilelast)
                log_v_plk1.writeListRow(v_plk1_average)

                log_k_plk1.closeFile()
                log_profile_plk1.closeFile()
                log_v_plk1.closeFile()

                log_conc_id0_plk1.closeFile()
                log_conc_id1_plk1.closeFile()
                log_conc_id2_plk1.closeFile()

                if drawMovie:
                    plots_plk1.FillDrawMovie()

    if drawMovie:
        plots.DrawMovie()
        if plk1:
            plots_plk1.DrawMovie()

    end_time = datetime.now()
    end_date_time = end_time.strftime("%d_%m_%Y_%H_%M_%S")
    print("Ending time: ", end_date_time)
    print("Finished!")


if __name__ == "__main__":
    main(sys.argv[1:])
