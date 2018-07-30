cmake_minimum_required(VERSION 2.8)
project(paperFigures LANGUAGES)

set( TEX_SRC
    ${CMAKE_CURRENT_SOURCE_DIR}/model_sbgn_pd.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/model_sbgn_pd_autolayout.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/model_schematic.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/simple_bistable_switch.tex
    #${CMAKE_CURRENT_SOURCE_DIR}/synapse_signalling_summary.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/camkii_subunit_exchage.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/camkii_pp1_switch_summary.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/camkii_pp1_switch_level1_detail.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/camk2_slow_activation.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/camk2_fast_activation.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/camkii_interaction.tex
    )
message( STATUS "Found TeX image source : ${TEX_SRC}" )

set( TEX_SRC_2 
    # make sure of dependencies of following files. They depend on files above.
    ${CMAKE_CURRENT_SOURCE_DIR}/mm_figure_a.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/figure_1.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/figure_validation_178mm.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/figure_2.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/figure_3.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/figure_sync_spread_178mm.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/figure_sync_spread_114mm.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/figure_sync_87mm.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/figure_effect_of_pp1_87mm.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/figure_pp_tolerance_178mm.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/figure_4.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/figure_5.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/figure_discussion_1.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/figure_camkii_activation.tex
    # ${CMAKE_CURRENT_SOURCE_DIR}/table.tex
    )

add_custom_target( figures ALL )

add_custom_target( primary_figures )
add_custom_target( secondary_figures )


foreach(_tex_src ${TEX_SRC})
    message( STATUS "Converting ${_tex_src} to PDF" )
    get_filename_component( TGT_NAME "${_tex_src}" NAME_WE )
    set(OUTPUT_FILE "${TGT_NAME}.pdf" )
    add_custom_target( ${TGT_NAME} DEPENDS ${OUTPUT_FILE} )
    add_custom_command( 
        OUTPUT ${OUTPUT_FILE} 
        COMMAND latexmk --shell-escape -lualatex ${_tex_src}
        MAIN_DEPENDENCY ${_tex_src}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMENT "Compiling ${_tex_src} in ${CMAKE_CURRENT_SOURCE_DIR}"
        VERBATIM
        )
    add_dependencies( primary_figures ${TGT_NAME} )
endforeach( )

foreach(_tex_src ${TEX_SRC_2})
    message( STATUS "Converting ${_tex_src} to PDF" )
    get_filename_component( TGT_NAME "${_tex_src}" NAME_WE )
    set(OUTPUT_FILE "${TGT_NAME}.pdf" )

    add_custom_target(${TGT_NAME} DEPENDS ${OUTPUT_FILE})
    add_custom_command(OUTPUT ${OUTPUT_FILE} 
        COMMAND latexmk --shell-escape -lualatex ${_tex_src}
        MAIN_DEPENDENCY ${_tex_src} 
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMENT "Compiling ${_tex_src} in ${CMAKE_CURRENT_SOURCE_DIR}"
        VERBATIM
        )

    add_dependencies( secondary_figures ${TGT_NAME} )
    add_dependencies( ${TGT_NAME} primary_figures )
endforeach( )

add_dependencies( figures secondary_figures )

## # SBGN mode in dot file. This does not work very well and has been commented
## # out.
## set(SBGN_DOT_FILE ${CMAKE_CURRENT_SOURCE_DIR}/model_sbgn_pd.dot)
## set(SBGN_DOT_M4_SCRIPT ${CMAKE_CURRENT_SOURCE_DIR}/model_sbgn_pd.dot.m4)
## 
## # Generate PNG file.
## set(MODEL_PNG_FILE "${SBGN_DOT_FILE}.png")
## add_custom_target( sbgn DEPENDS ${SBGN_DOT_FILE} )
## add_custom_command( OUTPUT ${SBGN_DOT_FILE} 
##     DEPENDS ${SBGN_DOT_M4_SCRIPT} 
##     COMMAND m4 ${SBGN_DOT_M4_SCRIPT} > ${SBGN_DOT_FILE}
##     COMMAND dot -Tpng ${SBGN_DOT_FILE} -o ${MODEL_PNG_FILE}
##     COMMENT "Generating model file in PNG format"
##     VERBATIM 
##     )
## add_dependencies( figures sbgn )
