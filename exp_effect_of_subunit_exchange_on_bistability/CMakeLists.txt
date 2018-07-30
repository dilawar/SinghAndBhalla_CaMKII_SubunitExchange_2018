# This experiment generates data to plot N vs stability or residence time.
cmake_minimum_required(VERSION 2.6)
project(EFFECT_OF_SUBUNIT_EXCHANGE LANGUAGES)

find_package(PythonInterp REQUIRED)

# Run the experiment.
set( MODEL_FILE ${CMAKE_CURRENT_SOURCE_DIR}/camkii_pp1_scheme.py )
set( PARAM_FILE ${CMAKE_CURRENT_SOURCE_DIR}/params.py )
set( ANALYSIS_FILE ${CMAKE_CURRENT_SOURCE_DIR}/analyze.py )
set( NUM_VOXELS 1 )
set( DIFF_DICT "{}" )

# Parameters: CaMKII
set(ENABLE_DIFFUSION OFF)
# This should be a python dictionary.
if( ENABLE_DIFFUSION )
    set( DIFF_DICT  "{ 'PP1' : 1e-13 }" )
    set( NUM_VOXELS 2 )
endif( ENABLE_DIFFUSION )

# copy the mode file into current dir.
file( COPY ${MODEL_FILE} DESTINATION ${CMAKE_CURRENT_SOURCE_DIR} )

# Run many targets.
add_custom_target( exp1 ALL )
set(_CAMKIIS 5 10 15 20)
set(_PP1S 80 180 260 350)
set(_SIMTIMES 10 30 50 100)
foreach(_i RANGE 0 3)
    list(GET _CAMKIIS ${_i} _camkii)
    list(GET _PP1S ${_i} _pp1)
    list(GET _SIMTIMES ${_i} _simtime)
    message( STATUS "CaMKII ${_camkii}, PP1 ${_pp1} for ${_simtime}" )
    # We want to include diffusion dictionary in the name of datafile. To do
    # so, we remove all the whitespace from the dictionary.
    string( REPLACE " " "" DIFF_DICT "${DIFF_DICT}" )
    string( REGEX REPLACE " |'|:|{|}" "-" _diff_dict "${DIFF_DICT}" )

    # Set params.
    set( _params --pp1 ${_pp1} --camkii ${_camkii} )
    set( _params ${_params} --enable-subunit-exchange --simtime ${_simtime} )

    if(ENABLE_DIFFUSION)
        set( _params ${_params} --diff-dict ${DIFF_DICT} )
    endif(ENABLE_DIFFUSION)

    set( TARGET_NAME camk${_camkii}_pp${_pp1}_voxel${NUM_VOXELS}_diff${_diff_dict} )
    # Set datafile which can be produced by running this script.

    set(DATA_FILE "${CMAKE_CURRENT_SOURCE_DIR}/${TARGET_NAME}.dat" )
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
        COMMAND ${ANALYSIS_FILE} -i ${DATA_FILE}
        COMMENT "Converting datafile to plot file"
        VERBATIM
        )
    add_dependencies( exp1 ${TARGET_NAME}.plot )
endforeach( )

## Find all 7zip files and decompress them
#file(GLOB ARCHIVED_DATA_DILES "${CMAKE_CURRENT_SOURCE_DIR}/*.7z")
#set(_uncompressed)
#foreach(DATA_FILE ${ARCHIVED_DATA_DILES})
    #get_filename_component(_NAME "${DATA_FILE}" NAME_WE)
    #set(OUTFILEPATH ${CMAKE_CURRENT_SOURCE_DIR}/${_NAME}.dat)
    #add_custom_command( OUTPUT ${OUTFILEPATH}
        #COMMAND 7z x -y ${DATA_FILE}
        #DEPENDS ${DATA_FILE}
        #COMMENT "Decompressing ${DATA_FILE}"
        #VERBATIM
        #)
    #list(APPEND _uncompressed ${OUTFILEPATH})
#endforeach( )

#add_custom_target(decompress DEPENDS ${_uncompressed} )

## Now once decompression is done. Lauch a gnuplot/python script to plot the data
## the way we like.
#set(_tables)
#foreach( DATAFILE ${_uncompressed} )
    #message( STATUS "Ploting and creating table out of ${DATAFILE}" )
    #set(OUTTABLE_PATH "${DATAFILE}.table" )
    #add_custom_command( OUTPUT ${OUTTABLE_PATH} 
        #COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/analyze.py ${DATAFILE}
        #DEPENDS ${DATAFILE} ${CMAKE_CURRENT_SOURCE_DIR}/analyze.py
        #COMMENT "${DATAFILE} - generating table and plot"
        #VERBATIM 
        #)
    #list(APPEND _tables ${OUTTABLE_PATH} )
#endforeach( )

#add_custom_target(plots DEPENDS ${_tables} )


