import dearpygui.dearpygui as dpg
from dearpygui.demo import show_demo

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

dpg.show_style_editor()
show_demo()

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
