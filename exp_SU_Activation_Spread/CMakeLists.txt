# In this experiment, we put N camkii in 18 camkii in 18 voxles. Every 2 hours,
# we give a slightly elevated Calcium pulse (150nM) to the system for 10 sec and
# observe how is the CaMKII activation profile.
cmake_minimum_required(VERSION 2.8)
project(CaMKII_PP1_Switch LANGUAGES NONE)
find_package(PythonInterp REQUIRED)

## Parameters
set(PYSCRIPT_MODEL ${CMAKE_CURRENT_BINARY_DIR}/camkii_pp1_scheme.py)
set(PYSCRIPT_PARAMS ${CMAKE_CURRENT_BINARY_DIR}/params.py)
set(PYSCRIPT_ANALYZE ${CMAKE_CURRENT_BINARY_DIR}/../analyze.py)
message(STATUS "Timestamp ${TIMESTAMP}")

set(NUMBER_OF_CAMKII 18)
set(COMPARMETN_LENGTH_IN_NM 540)
set(NVOXEL 18)

# Since concentration is always with relative to compartment volume and not to
# voxel volume; make sure to divide each of them by number of compartment.
math(EXPR CA_CONC_IN_NM "80/${NVOXEL}")
math(EXPR CA_STIM_IN_NM "160/${NVOXEL}")
set(_ca_basal "${CA_CONC_IN_NM}e-6")
set(_ca_stim "${CA_STIM_IN_NM}e-6")

MATH(EXPR VOXEL_LENGTH_IN_NM "${COMPARMETN_LENGTH_IN_NM}/${NVOXEL}")
set(VOXEL_LENGTH ${VOXEL_LENGTH_IN_NM}e-9)
set(_SU ON)

add_custom_target( exp ALL )

set(LIST_OF_DATA_FILES "")

set(RUN_TIME 0.2)

# set the PP1 diff-const to a fixed value.
set(PP1_DIFF_CONST 5e-13)

foreach(CA_CONC_IN_NM 70 80 90 100 120) 
    math(EXPR _ca_basal "${CA_CONC_IN_NM}/${NVOXEL}")
    set(_ca_basal "${_ca_basal}e-6")
    set(DATA_DIR "DATA_CA_BASAL_${CA_CONC_IN_NM}NM")
    file(MAKE_DIRECTORY ${DATA_DIR})
    foreach(NUMBER_OF_PP1 
            1000.01 1000.11 1000.21 1000.31 1000.41 1000.51 1000.61 1000.71 1000.81 1000.91
            1000.02 1000.12 1000.22 1000.32 1000.42 1000.52 1000.62 1000.72 1000.82 1000.92
            1000.03 1000.13 1000.23 1000.33 1000.43 1000.53 1000.63 1000.73 1000.83 1000.93
            1000.04 1000.14 1000.24 1000.34 1000.44 1000.54 1000.64 1000.74 1000.84 1000.94
            )
        foreach(_D 0e0 1e-20 1e-19 1e-18 1e-17 1e-16 1e-15 1e-14 1e-13 1e-12)
            # set(CAEXPR "fmod(t,3600)<20?${_ca_stim}:((fmod(t,4)<2)?${_ca_basal}:(${_ca_basal}*(1+0.5*rand(-1))))")
            # set(CAEXPR "(fmod(t,4)<2)?${_ca_basal}:(${_ca_basal}*(1.5+0.5*rand(-1)))")
            set(CAEXPR "${_ca_basal}")
            set(DIFFUSION_DICT "{'x':${_D},'y':${_D},'PP1':${PP1_DIFF_CONST}, 'PP1.x':${_D}, 'PP1.y' : ${_D} }")

            # Set experiment name.
            set(EXP_NAME "CaM-${NUMBER_OF_CAMKII}+PP-${NUMBER_OF_PP1}")
            set(EXP_NAME "${EXP_NAME}+D-${DIFFUSION_DICT}+N-${NVOXEL}" )

            # generate a sane target name.
            string(REPLACE " " "" EXP_NAME ${EXP_NAME})
            string(REGEX REPLACE "[{},':]" "" TARGET_NAME ${EXP_NAME})
            string(REGEX REPLACE "[,]" "--" EXP_NAME ${EXP_NAME})
            string(REGEX REPLACE "[:]" "++" EXP_NAME ${EXP_NAME})

            # append ca basal level to target name.
            set(TARGET_NAME "${TARGET_NAME}_ca_${CA_CONC_IN_NM}")

            # Add target
            set(DATAFILE "${DATA_DIR}/${EXP_NAME}.dat")
            set(PLOTFILE "${DATA_DIR}/${EXP_NAME}.png")

            add_custom_target( ${TARGET_NAME} DEPENDS ${DATAFILE})
            add_custom_target( ${TARGET_NAME}.plot DEPENDS ${PLOTFILE} ${DATAFILE} )

            set(ARGS --camkii ${NUMBER_OF_CAMKII} --pp1 ${NUMBER_OF_PP1}
                --diff-dict "${DIFFUSION_DICT}" --outfile ${DATAFILE}
                --ca-expr ${CAEXPR} 
                --simtime ${RUN_TIME} 
                --num-voxels ${NVOXEL}
                --record-dt 2
                --voxel-length ${VOXEL_LENGTH}
                )

            if(_SU)
                list(APPEND ARGS --enable-subunit-exchange)
            endif(_SU)

            # Command to run the experiment.
            add_custom_command(OUTPUT ${DATAFILE}
                COMMAND ${PYTHON_EXECUTABLE} ${PYSCRIPT_MODEL} ${ARGS}
                MAIN_DEPENDENCY ${PYSCRIPT_MODEL} 
                DEPENDS ${PYSCRIPT_PARAMS}
                COMMENT "Running ${TARGET_NAME}"
                VERBATIM
                )

            add_custom_command( OUTPUT ${PLOTFILE}
                COMMAND ${PYTHON_EXECUTABLE} ${PYSCRIPT_ANALYZE} -i ${DATAFILE} 
                MAIN_DEPENDENCY ${DATAFILE}
                DEPENDS ${PYSCRIPT_ANALYZE}
                COMMENT "Plotting ${TARGET_NAME}"
                VERBATIM
                )
            add_dependencies( exp ${TARGET_NAME}.plot )
            set(LIST_OF_DATA_FILES "${LIST_OF_DATA_FILES} ${EXP_NAME}.dat_processed.dat")
            message(STATUS "Added target: ${TARGET_NAME}")
        endforeach()
    endforeach()
endforeach()

message(STATUS "Files to analyze ${LIST_OF_DATA_FILES}")
add_custom_target(summary ALL
    DEPENDS exp
    COMMAND bash -c ./generate_summary.sh
    COMMENT "Generating experiment"
    )
