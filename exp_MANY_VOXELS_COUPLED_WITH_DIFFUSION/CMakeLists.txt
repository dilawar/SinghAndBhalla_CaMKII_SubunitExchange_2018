cmake_minimum_required(VERSION 2.8)
project(CaMKII_PP1_Switch LANGUAGES NONE)
find_package(PythonInterp REQUIRED)

## Parameters
# Set these parameters run the model

set( NUMBER_OF_CAMKII 15 )
set( NUMBER_OF_PP1 180 )
# Run time in days.
set( RUN_TIME 10 )
set( VOXEL_LENGTH 125e-9 )
set( NUM_VOXELS 3 )
set( DIFFUSION_DICT "{ 'x' : 1e-13, 'y' : 1e-13 }" )

# Move all python files into current directory.
file( GLOB MY_PYTHON_SCRIPTS "${CMAKE_CURRENT_SOURCE_DIR}/*.py" )
file( COPY ${MY_PYTHON_SCRIPTS} DESTINATION ${CMAKE_CURRENT_BINARY_DIR} )

# ARCHIVAL: Move only valid data to this directory.
set( ARCHIVE_DIR ${CMAKE_BINARY_DIR}/_data_archive )
file( MAKE_DIRECTORY ${ARCHIVE_DIR} )

file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/camkii_pp1_scheme.py" 
    DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}
    )
set( PYSCRIPT_MODEL ${CMAKE_CURRENT_BINARY_DIR}/camkii_pp1_scheme.py)
set( PYSCRIPT_PARAMS ${CMAKE_CURRENT_BINARY_DIR}/params.py)
set( PYSCRIPT_ANALYZE ${CMAKE_CURRENT_BINARY_DIR}/analyze.py)

message( STATUS "Timestamp ${TIMESTAMP}" )

# For tikzexternalize macro.
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/_tikz)

###############################################################################
# EXPERIMENT:
# We have NUM_VOXELS voxels each is coupled with diffusive subunits x and y. How
# the whole system behave under diffusion on subunit i.e. what effect subunit
# exchange has when subunits are allowed to diffuse.
###############################################################################

add_custom_target( exp )

# NOTE: 1e-11 is very high value of simulation to show any progress.
foreach( _diff_const 1e-12 1e-13 1e-14 1e-15 1e-16)
    # EXPERIMENT 1: Cause LTP by a calcium pulse and wait for CaMKII activity to go
    # down. See what subunit exchange does to this.
    set( DIFFUSION_DICT "{ 'x':${_diff_const}, 'y':${_diff_const}, 'PP1':1e-13 }")
    set(EXPERIMENT_NAME 
        "CaMKII-${NUMBER_OF_CAMKII}+PP1-${NUMBER_OF_PP1}+L-${VOXEL_LENGTH}+N-${NUM_VOXELS}"
        )
    set(EXPERIMENT_NAME  "${EXPERIMENT_NAME}+diff-${_diff_const}" )

    set(DATAFILE "${EXPERIMENT_NAME}.dat")
    set(DATAFILE_SUMMARY "${DATAFILE}_processed.dat")
    set(PLOTFILE "${EXPERIMENT_NAME}.png")

    add_custom_target( ${EXPERIMENT_NAME} DEPENDS  ${DATAFILE_SUMMARY} )
    add_custom_target( ${EXPERIMENT_NAME}.plot DEPENDS ${PLOTFILE} )

    # Command to run the experiment.
    add_custom_command( OUTPUT ${DATAFILE}
        COMMAND ${PYTHON_EXECUTABLE} ${PYSCRIPT_MODEL} 
                --camkii ${NUMBER_OF_CAMKII} 
                --pp1 ${NUMBER_OF_PP1}
                --diff-dict "${DIFFUSION_DICT}"
                --enable-subunit-exchange
                --outfile ${DATAFILE}
                --simtime ${RUN_TIME}
        # Also create archive
        COMMAND ${CMAKE_BINARY_DIR}/archive.sh ${DATAFILE} ${ARCHIVE_DIR}
        MAIN_DEPENDENCY ${PYSCRIPT_MODEL} 
        DEPENDS ${PYSCRIPT_PARAMS}
        COMMENT "Running ${EXPERIMENT_NAME}"
        VERBATIM
        )

    add_custom_command( OUTPUT ${PLOTFILE} ${DATAFILE_SUMMARY}
        COMMAND ${PYTHON_EXECUTABLE} ${PYSCRIPT_ANALYZE} -i ${DATAFILE} 
        COMMAND ${CMAKE_BINARY_DIR}/archive.sh ${DATAFILE_SUMMARY} ${ARCHIVE_DIR}
        MAIN_DEPENDENCY ${DATAFILE}
        DEPENDS ${PYSCRIPT_ANALYZE}
        COMMENT "Plotting ${EXPERIMENT_NAME}"
        VERBATIM
        )
    add_dependencies( ${EXPERIMENT_NAME}.plot ${EXPERIMENT_NAME} )
    add_dependencies( exp ${EXPERIMENT_NAME}.plot )

endforeach( )

set( EXP_SUMMARY_FILE
    ${CMAKE_CURRENT_SOURCE_DIR}/decay_of_intermediate_states.png.dat
    )

add_custom_target( exp_summary ALL
    DEPENDS exp ${EXP_SUMMARY_FILE}
    COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/experiment_summary.py
    COMMENT "Generate experimental summary"
    VERBATIM
    )

# Generate labnote out of TeX file.
add_custom_target( labnote 
    DEPENDS labnote.tex
    COMMAND lualatex --shell-escape labnote.tex
    COMMENT "Generating pdf"
    VERBATIM 
    )
