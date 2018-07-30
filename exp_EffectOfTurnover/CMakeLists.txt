cmake_minimum_required(VERSION 2.8)

project(Turnover LANGUAGES NONE)
find_package(PythonInterp REQUIRED)

## Parameters
# Set these parameters run the model

set( RUN_TIME 100 )
set( DIFFUSION_DICT "{ 'x' : 1e-13, 'y' : 1e-13 }" )

set( PYSCRIPT_MODEL ${CMAKE_CURRENT_BINARY_DIR}/camkii_pp1_scheme.py)
set( PYSCRIPT_PARAMS ${CMAKE_CURRENT_BINARY_DIR}/params.py)
set( PYSCRIPT_ANALYZE ${CMAKE_CURRENT_BINARY_DIR}/../analyze.py)

message( STATUS "Timestamp ${TIMESTAMP}" )

add_custom_target( exp ALL )

# wihtout subunit-exchange
foreach( SE "ON" "OFF")
foreach( CAMKII 6 8 12 16 )

    if("${SE}" STREQUAL "OFF" )
        message( STATUS "subunit-exchange is OFF" )
        math(EXPR PP1 "${CAMKII}*8")
    else()
        message( STATUS "subunit-exchange is ON" )
        math(EXPR PP1 "${CAMKII}*13")
    endif()

    message(STATUS "- CaMKII=${CAMKII} and PP1=${PP1}" )
    foreach( _tr 30 20 10 5 2 1 0.5 0.1)
        set(_EXPR "print('%.15f' % eval(\"1.0/3600/${_tr}\"))" )
        execute_process( COMMAND ${PYTHON_EXECUTABLE} -c ${_EXPR} 
            OUTPUT_VARIABLE TURNOVER_RATE
            OUTPUT_STRIP_TRAILING_WHITESPACE
            )
        set(_exp_name "CaM${CAMKII}_turnover${_tr}_su${SE}" )
        set(OUTPUT_DATA_FILE "data_${_exp_name}.dat" )


        set( RUN_ARGS --camkii ${CAMKII} --pp1 ${PP1} 
            --simtime ${RUN_TIME} 
            --turnover-rate ${TURNOVER_RATE} 
            --record-dt 5
            -o ${OUTPUT_DATA_FILE}
            )

        if( ${SE} STREQUAL "ON" )
            set( RUN_ARGS ${RUN_ARGS} --enable-subunit-exchange 
                --diff-dict ${DIFFUSION_DICT}
                )
        endif()

        add_custom_target( ${_exp_name} DEPENDS ${OUTPUT_DATA_FILE} )
        add_custom_command( OUTPUT ${OUTPUT_DATA_FILE}
            COMMAND ${PYTHON_EXECUTABLE} ${PYSCRIPT_MODEL} ${RUN_ARGS}
            COMMAND ${PYTHON_EXECUTABLE} ${PYSCRIPT_ANALYZE} -i
                ${OUTPUT_DATA_FILE}
            COMMENT "Producing ${OUTPUT_DATA_FILE}"
            VERBATIM
            )
        message(STATUS "+ Experiment name ${_exp_name}" )
        add_dependencies( exp ${_exp_name} )
    endforeach( )
endforeach( )
endforeach( )
