cmake_minimum_required(VERSION 2.8)
project(CaMKII_PP1_Switch LANGUAGES NONE)
find_package(PythonInterp REQUIRED)

# Parameters. See ./reference_system_in_1_voxel.sh for paramters used in
# reference system which is well mixed.
set( NUMBER_OF_CAMKII 6 )
set( NUM_VOXELS 3 )
set( NUMBER_OF_PP1 160 )

# Each camkii is 30nm away. 2 CaMKII in 1 voxels means length is 60nm.
set( VOXEL_LENGTH 60e-9 )

# Run time in days.
set( RUN_TIME 20 )

# ARCHIVAL: Move only valid data to this directory.
set( ARCHIVE_DIR ${CMAKE_BINARY_DIR}/_data_archive )
file( MAKE_DIRECTORY ${ARCHIVE_DIR} )

set( PYSCRIPT_MODEL ${CMAKE_CURRENT_BINARY_DIR}/../camkii_pp1_scheme.py)
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
foreach( _diff_const_pp1 1e-14 2e-14 5e-14 1e-13 2e-13 5e-13 1e-12)
foreach( _diff_const 1e-15 3e-15 1e-14 3e-14 1e-13 3e-13 1e-12)
    # EXPERIMENT 1: Cause LTP by a calcium pulse and wait for CaMKII activity to go
    # down. See what subunit exchange does to this.
    set( DIFFUSION_DICT "{ 'x':${_diff_const}, 'y':${_diff_const}, 'PP1':${_diff_const_pp1} }")
    set(EXPERIMENT_NAME "Dsub-${_diff_const}+Dpp-${_diff_const_pp1}")
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
                --num-voxels ${NUM_VOXELS}
                --voxel-length ${VOXEL_LENGTH}
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
endforeach()
endforeach()

add_custom_target( exp_summary ALL
    DEPENDS exp 
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
