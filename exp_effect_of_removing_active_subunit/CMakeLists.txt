cmake_minimum_required(VERSION 2.8)
project(CaMKII_PP1_Switch LANGUAGES NONE)
find_package(PythonInterp REQUIRED)

## Parameters
# Set these parameters run the model

set( NUMBER_OF_CAMKII 6 )
set( NUMBER_OF_PP1 26 )
# Run time in days.
set( RUN_TIME 100 )
set( NUMBER_OF_SWITCHES 1 )
#set( VOXEL_LENGTH 125e-9 )
set( VOXEL_LENGTH 125e-9 )
set( NUM_VOXELS 1 )
set( DIFFUSION_COEFF 0)

configure_file( ${CMAKE_CURRENT_SOURCE_DIR}/params.py.in ${CMAKE_BINARY_DIR}/params.py)
configure_file( 
    ${CMAKE_CURRENT_SOURCE_DIR}/camkii_pp1_scheme.py 
    ${CMAKE_BINARY_DIR}/camkii_pp1_scheme.py 
    )

# Move all python files into current directory.
file( GLOB MY_PYTHON_SCRIPTS "${CMAKE_CURRENT_SOURCE_DIR}/*.py" )
file( COPY ${MY_PYTHON_SCRIPTS} DESTINATION ${CMAKE_CURRENT_BINARY_DIR} )

set( PYSCRIPT_MODEL ${CMAKE_CURRENT_BINARY_DIR}/camkii_pp1_scheme.py)
set( PYSCRIPT_PARAMS ${CMAKE_CURRENT_BINARY_DIR}/params.py)
set( PYSCRIPT_ANALYZE ${CMAKE_CURRENT_BINARY_DIR}/analyze.py)

string( TIMESTAMP TIMESTAMP "%Y-%m-%d_%H:%M")
message( STATUS "Timestamp ${TIMESTAMP}" )

###############################################################################
# EXPERIMENT:
# We have NUM_VOXELS voxels each is coupled with diffusive subunits x and y. How
# the whole system behave under diffusion on subunit i.e. what effect subunit
# exchange has when subunits are allowed to diffuse.
###############################################################################

add_custom_target( exp ALL  )

message(STATUS "Diffusion coefficient is ${DIFFUSION_COEFF}" )
set(DIFFUSION_DICT "{ 'x' : ${DIFFUSION_COEFF}, 'y' : ${DIFFUSION_COEFF} }")
set(EXPERIMENT_NAME 
    "CaMKII-${NUMBER_OF_CAMKII}+PP1-${NUMBER_OF_PP1}+L-${VOXEL_LENGTH}+N-${NUM_VOXELS}"
    )
set(EXPERIMENT_NAME  "${EXPERIMENT_NAME}+diff-${DIFFUSION_COEFF}" )

# NOTE: make sure the formatting of number is same to sort it later.
set( XTOXSKF "1" )
foreach( _x2xskb 0.001 0.005 0.01 0.05 0.1 0.5 1 5 10 50 100 500 1000 5000)
    set(XTOXSKB "${_x2xskb}")
    set(SUBEXP_NAME "${EXPERIMENT_NAME}_removal_kf${XTOXSKF}kb${XTOXSKB}" )
    set(DATAFILE "${SUBEXP_NAME}.dat")
    set(PLOTFILE "${SUBEXP_NAME}.png")

    add_custom_target( ${SUBEXP_NAME} 
        DEPENDS ${DATAFILE} 
        COMMENT "Running experiment to generate data"
        )

    # Command to run the experiment.
    add_custom_command( OUTPUT ${DATAFILE}
        COMMAND ${PYTHON_EXECUTABLE} ${PYSCRIPT_MODEL} 
        --camkii ${NUMBER_OF_CAMKII} 
        --pp1 ${NUMBER_OF_PP1}
        --diff-dict "${DIFFUSION_DICT}"
        --enable-subunit-exchange
        --outfile ${DATAFILE}
        --xtoxsKf ${XTOXSKF}
        --xtoxsKb ${XTOXSKB}
        --simtime ${RUN_TIME}
        COMMAND ${PYTHON_EXECUTABLE} ${PYSCRIPT_ANALYZE} -i ${DATAFILE} 
        MAIN_DEPENDENCY ${PYSCRIPT_MODEL} 
        DEPENDS ${PYSCRIPT_PARAMS}
        COMMENT "Running ${SUBEXP_NAME}"
        VERBATIM
        )

    add_custom_target( ${SUBEXP_NAME}_plot 
        DEPENDS ${PLOTFILE}
        COMMENT "Plotting data"
        )

    add_custom_command( OUTPUT ${PLOTFILE}
        COMMAND ${PYTHON_EXECUTABLE} ${PYSCRIPT_ANALYZE} -i ${DATAFILE} 
        MAIN_DEPENDENCY ${DATAFILE}
        DEPENDS ${PYSCRIPT_ANALYZE}
        COMMENT "Plotting ${SUBEXP_NAME}"
        VERBATIM
        )
    add_dependencies( ${SUBEXP_NAME}_plot ${SUBEXP_NAME} )
    add_dependencies( exp ${SUBEXP_NAME}_plot )
endforeach( )

# Generate summary plot
set( ANALYZE_SCRIPT ${CMAKE_CURRENT_SOURCE_DIR}/analyze_exp.py )
add_custom_target( summary_plot ALL
    DEPENDS ${ANALYZE_SCRIPT} exp
    COMMAND python ${ANALYZE_SCRIPT}
    COMMENT "Generating summary plots"
    VERBATIM 
    )

# Generate labnote out of TeX file.
add_custom_target( labnote 
    DEPENDS labnote.md 
    COMMAND markdown_to_pdf.sh labnote.md 
    #COMMAND lualatex --shell-escape labnote.md.tex
    COMMENT "Generating pdf"
    VERBATIM 
    )
