cmake_minimum_required(VERSION 2.6)
project(Validation LANGUAGES)

find_package(PythonInterp REQUIRED)

# Run the experiment.
set( MODEL_FILE ${CMAKE_CURRENT_SOURCE_DIR}/camkii_pp1_scheme.py )
set( PARAM_FILE ${CMAKE_CURRENT_SOURCE_DIR}/params.py )
set( ANALYSIS_FILE ${CMAKE_CURRENT_SOURCE_DIR}/analyze.py )
set( RUN_TIME 100 )
set( RECORD_DT 30 )

# Parameters: CaMKII
set( ENABLE_DIFFUSION ON )

# This should be a python dictionary.
if( ENABLE_DIFFUSION )
    set( DIFF_DICT  "{ 'x' : 1e-13, 'y' : 1e-13, 'PP1' : 1e-13 }" )
else( )
    set( DIFF_DICT "{}" )
endif( ENABLE_DIFFUSION )

# Archival With timestamp.
string(TIMESTAMP STAMP "%Y%m%d-%H%H%S")
set(DATA_DIR ${CMAKE_CURRENT_SOURCE_DIR}/_data/${STAMP})
file(MAKE_DIRECTORY ${DATA_DIR})
message(STATUS "Data directory is ${DATA_DIR}")
set(ARCHIVAL_SCRIPT ${CMAKE_CURRENT_SOURCE_DIR}/../archive.sh)

# copy the mode file into current dir.
file( COPY ${MODEL_FILE} DESTINATION ${CMAKE_CURRENT_SOURCE_DIR} )

################################################################################
# Run experiment to generate data. 

add_custom_target( exp )
set( CAMKII_LIST 80 )
foreach(ENABLE_SUBUNIT_EXCHANGE ON OFF)
    foreach( NUM_VOXELS 1 2 3)
        foreach(_camkii ${CAMKII_LIST})
            math( EXPR CAMKII_N "${_camkii}*${NUM_VOXELS}" )
            math( EXPR PP1_MIN "${_camkii} * 1" )
            math( EXPR PP1_MAX "${_camkii} * 4" )
            foreach( _pp1 RANGE ${PP1_MIN} ${PP1_MAX} 20)
                # We want to include diffusion dictionary in the name of datafile. To do
                # so, we remove all the whitespace from the dictionary.
                string( REPLACE " " "" DIFF_DICT "${DIFF_DICT}" )
                string( REGEX REPLACE " |'|:|{|}|," "-" _diff_dict "${DIFF_DICT}" )

                # Set params.
                set( _params ${_params} --pp1 ${_pp1} --camkii ${CAMKII_N} )
                set( _params ${_params} --record-dt ${RECORD_DT} )
                set( _params ${_params} --num-voxels ${NUM_VOXELS}  --simtime ${RUN_TIME} )

                if(ENABLE_SUBUNIT_EXCHANGE)
                    set( _params ${_params} --enable-subunit-exchange )
                else()
                    set(ENABLE_DIFFUSION OFF)
                endif()

                if(ENABLE_DIFFUSION)
                    set( _params ${_params} --diff-dict ${DIFF_DICT} )
                endif(ENABLE_DIFFUSION)

                set( TARGET_NAME
                    camk${_camkii}_pp${_pp1}_voxel${NUM_VOXELS}_diff${_diff_dict}_su${ENABLE_SUBUNIT_EXCHANGE} 
                    )
                # Set datafile which can be produced by running this script.

                set(DATA_FILE "${DATA_DIR}/${TARGET_NAME}.dat" )
                set(PLOT_FILE "${DATA_FILE}.png" )

                add_custom_target( ${TARGET_NAME} DEPENDS ${DATA_FILE})
                add_custom_target( ${TARGET_NAME}.plot DEPENDS ${PLOT_FILE} )

                add_custom_command( 
                    OUTPUT ${DATA_FILE}
                    COMMAND ${PYTHON_EXECUTABLE} camkii_pp1_scheme.py ${_params} -o ${DATA_FILE}
                    COMMENT "Executing model to generate data"
                    VERBATIM 
                    )

                add_custom_command( OUTPUT ${PLOT_FILE} DEPENDS ${DATA_FILE}
                    COMMAND ${PYTHON_EXECUTABLE} ${ANALYSIS_FILE} -i ${DATA_FILE}
                    COMMENT "Converting datafile to plot file"
                    VERBATIM
                    )
                add_dependencies( exp ${TARGET_NAME}.plot )
            endforeach( )
        endforeach( )
    endforeach( )
endforeach( )

################################################################################
# Generate figures and labnote.
# First we process the files with given number of voxels.

set(PANDOC pandoc --number-sections --standalone -F pandoc-crossref -F pandoc-citeproc )
add_custom_target(labnote 
    DEPENDS ${CMAKE_SOURCE_DIR}/labnote.pandoc
    COMMAND pandoc2pdf.sh ${CMAKE_SOURCE_DIR}/labnote.pandoc 
    COMMAND pandoc2html.py ${CMAKE_SOURCE_DIR}/labnote.pandoc
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMENT "Generating pdf/html"
    )

add_custom_target( analyzedat )
set(ALL_DATA_TGTS "")
foreach( _camkii ${CAMKII_LIST} )
    foreach( _voxels 1 2 3 )
        file(GLOB_RECURSE _datafile_${_camkii}_${_voxels} 
            "./_data/*camk${_camkii}*voxel${_voxels}*.dat"
            )

        set(TGT_NAME analyse_${_camkii}_${_voxels} )
        set(DATAFILE _data_camkii${_camkii}_voxel${_voxels} )
        set(OUTFILES ${DATAFILE}_su.dat ${DATAFILE}_wsu.dat )


        add_custom_target( ${TGT_NAME} DEPENDS ${OUTFILES} )
        add_custom_command( OUTPUT ${OUTFILES}
            COMMAND ${PYTHON_EXECUTABLE} ./generate_figure.py 
                --camkii ${_camkii} --voxels ${_voxels}
                --outfile ${DATAFILE}
            DEPENDS ${_datafile_${_camkii}_${_voxels}}
            WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
            COMMENT "Analysing data"
            VERBATIM
            )
        list( APPEND ALL_DATA_TGTS ${TGT_NAME} )
        add_dependencies( analyzedat ${TGT_NAME} )
    endforeach( )
endforeach( )

# Convert each tex to pdf.
add_custom_target( figures )

################################################################################
# Convert figure_*.tex to PDF and PNG files.
################################################################################
file(GLOB TEX_SRC figure*.tex )
foreach( _tex ${TEX_SRC} )
    get_filename_component(_tgt_name ${_tex} NAME_WE)
    set(OUTFILEPDF "${CMAKE_SOURCE_DIR}/${_tgt_name}.pdf" )
    add_custom_target( ${_tgt_name} DEPENDS ${OUTFILEPDF} )
    add_custom_command( OUTPUT ${OUTFILEPDF}
        COMMAND lualatex --shell-escape ${_tex}
        DEPENDS ${_tex} 
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        COMMENT "Generating pdf from ${_tex}"
        VERBATIM
        )
    add_dependencies( ${_tgt_name} analyzedat )
    add_dependencies( figures ${_tgt_name} )
endforeach( )
add_dependencies( labnote figures )
