from typing import Tuple

import dearpygui.dearpygui as dpg

from conf import cnf


# shades of dark grey (background color)
B0 = (14, 16, 20, 255)
B1 = (22, 24, 28, 255)
B2 = (33, 36, 45, 255)

# shades of blue (accent color)
A0 = (65, 98, 150, 255)
A1 = (76, 114, 176, 255)
A2 = (87, 131, 201, 255)

# almost white (text)
T0 = (211, 217, 231, 255)


def get_theme_and_font(just_theme=False):
    # type: (bool) -> Tuple[str, str]
    """

    :return:
    """

    if not just_theme:
        with dpg.font_registry():
            font_path = cnf.res_path / 'OpenSans' / 'OpenSans-Medium.ttf'
            font = dpg.add_font(font_path, 18, tag='ttf-font')
    else:
        font = None

    with dpg.theme() as main_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 20, 20)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 4)
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, B0)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, B1)
            dpg.add_theme_color(dpg.mvThemeCol_Border, B2)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, B2)
            dpg.add_theme_color(dpg.mvThemeCol_Separator, B2)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, A0)
            dpg.add_theme_color(dpg.mvThemeCol_Button, A1)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, A2)
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, A2)
            dpg.add_theme_color(dpg.mvThemeCol_Text, T0)
            dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 6, 4)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 6, 4)
    return main_theme, font


def get_pop_theme():
    # type: () -> str

    with dpg.theme() as pop_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 20, 20)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 4)
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, B0)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, B1)
            dpg.add_theme_color(dpg.mvThemeCol_Border, A0)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, A0)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, A0)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, B2)
            dpg.add_theme_color(dpg.mvThemeCol_Separator, B2)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, A0)
            dpg.add_theme_color(dpg.mvThemeCol_Button, A1)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, A2)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, A0)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, A0)
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, A2)
            dpg.add_theme_color(dpg.mvThemeCol_Text, T0)
            dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 6, 4)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 6, 4)
    return pop_theme
