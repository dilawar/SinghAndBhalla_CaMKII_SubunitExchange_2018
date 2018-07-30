cmake_minimum_required(VERSION 2.8)
project(CaMKII_PP1_Switch LANGUAGES NONE)
find_package(PythonInterp REQUIRED)

## Parameters
set(PYSCRIPT_MODEL ${CMAKE_CURRENT_BINARY_DIR}/camkii_pp1_scheme.py)
set(PYSCRIPT_PARAMS ${CMAKE_CURRENT_BINARY_DIR}/params.py)
set(PYSCRIPT_ANALYZE ${CMAKE_CURRENT_BINARY_DIR}/../analyze.py)
message( STATUS "Timestamp ${TIMESTAMP}" )

# For CaMKII=4, PP1=300
# For CaMKII=6, PP1=420 
#    Given good bistable behaviour.
set(NUMBER_OF_CAMKII 6)
set(NVOXEL 6)
set(NUMBER_OF_PP1 420)

# Since concentration is always with relative to compartment volume and not to
# voxel volume; make sure to divide each of them by number of compartment.
math(EXPR CA_CONC_IN_UM "80/${NVOXEL}")
set(_ca_basal "${CA_CONC_IN_UM}e-6")

set(COMPARMENT_LENGTH_IN_NM 400)
math(EXPR VOXEL_LENGTH_IN_NM "${COMPARMENT_LENGTH_IN_NM}/${NVOXEL}")
set(VOXEL_LENGTH "${VOXEL_LENGTH_IN_NM}e-9")
set(_SU ON)

add_custom_target( exp ALL )
set(LIST_OF_DATA_FILES "")

set(RUN_TIME 10)

# reference run. Syntem in 1 voxel.
set(EXP_NAME "base_run_CaM${NUMBER_OF_CAMKII}_PP${NUMBER_OF_PP1}_in_1_voxel" )
set(DATAFILE "${EXP_NAME}.dat")
set(PLOTFILE "${EXP_NAME}.dat.png")
add_custom_target( reference DEPENDS ${DATAFILE})
add_custom_target( reference.plot DEPENDS ${PLOTFILE} ${DATAFILE} )

set(CAEXPR "(fmod(t,4)<2)?80e-6:80e-6*(1+0.5*rand(-1))")

# No diffusion in this case.
set(ARGS --camkii ${NUMBER_OF_CAMKII} --pp1 ${NUMBER_OF_PP1}
    --outfile ${DATAFILE}
    --ca-expr ${CAEXPR} 
    --simtime ${RUN_TIME} 
    --num-voxels 1
    --voxel-length ${COMPARMENT_LENGTH_IN_NM}e-9
    --enable-subunit-exchange
    )

# Command to run the experiment.
add_custom_command( OUTPUT ${DATAFILE}
    COMMAND ${PYTHON_EXECUTABLE} ${PYSCRIPT_MODEL} ${ARGS}
    MAIN_DEPENDENCY ${PYSCRIPT_MODEL} 
    DEPENDS ${PYSCRIPT_PARAMS}
    COMMENT "Running ${TARGET_NAME}"
    VERBATIM
    )

add_custom_command( OUTPUT ${PLOTFILE}
    COMMAND ${PYTHON_EXECUTABLE} ${PYSCRIPT_ANALYZE} -i ${DATAFILE} 
    MAIN_DEPENDENCY ${DATAFILE}
    DEPENDS ${PYSCRIPT_ANALYZE} ${DATAFILE}
    COMMENT "Plotting ${TARGET_NAME}"
    VERBATIM
    )
add_dependencies(exp reference.plot)

# set(PP1_DIFF_CONST 1e-12)
foreach(_D 0e0 1e-15 5e-15 1e-14 5e-14 1e-13 5e-13 1e-12 5e-12 1e-11)
foreach(PP1_DIFF_CONST 0e0 1e-15 5e-15 1e-14 5e-14 1e-13 5e-13 1e-12 5e-12)
    set(CAEXPR "(fmod(t,4)<2)?${_ca_basal}:(${_ca_basal}*(1+0.5*rand(-1)))")
    set(DIFFUSION_DICT "{'x':${_D},'y':${_D},'PP1':${PP1_DIFF_CONST}}")

    # Set experiment name.
    set(EXP_NAME "CaM-${NUMBER_OF_CAMKII}+PP-${NUMBER_OF_PP1}")
    set(EXP_NAME "${EXP_NAME}+D-${DIFFUSION_DICT}+N-${NVOXEL}" )

    # generate a sane target name.
    string(REPLACE " " "" EXP_NAME ${EXP_NAME})
    string(REGEX REPLACE "[{},':]" "" TARGET_NAME ${EXP_NAME})
    string(REGEX REPLACE "[,]" "--" EXP_NAME ${EXP_NAME})
    string(REGEX REPLACE "[:]" "++" EXP_NAME ${EXP_NAME})

    # Add target
    set(DATAFILE "${EXP_NAME}.dat")
    set(PLOTFILE "${EXP_NAME}.png")

    add_custom_target( ${TARGET_NAME} DEPENDS ${DATAFILE})
    add_custom_target( ${TARGET_NAME}.plot DEPENDS ${PLOTFILE} ${DATAFILE} )

    set(ARGS --camkii ${NUMBER_OF_CAMKII} --pp1 ${NUMBER_OF_PP1}
        --diff-dict "${DIFFUSION_DICT}" --outfile ${DATAFILE}
        --ca-expr ${CAEXPR} 
        --simtime ${RUN_TIME} 
        --num-voxels ${NVOXEL}
        --voxel-length ${VOXEL_LENGTH}
        )

    if(_SU)
        list(APPEND ARGS --enable-subunit-exchange)
    endif()

    # Command to run the experiment.
    add_custom_command( OUTPUT ${DATAFILE}
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

message(STATUS "Files to analyze ${LIST_OF_DATA_FILES}")
add_custom_target(summary ALL
    DEPENDS exp
    COMMAND ./analyze_exp.py 
    COMMENT "Generating experiment"
    )
