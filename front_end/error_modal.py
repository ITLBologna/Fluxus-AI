from dearpygui import dearpygui as dpg

from front_end import theme


def build_modal():
    with dpg.popup(dpg.last_item(), modal=True, tag='error_modal'):
        dpg.add_text('Unknown error occurred', tag='t1', wrap=300)
        dpg.add_button(label='Continue', callback=lambda _: show_modal(False))
        show_modal(False)

        t = theme.get_pop_theme()
        dpg.configure_item('error_modal', label='Error')
        dpg.configure_item('error_modal', min_size=[330, 100])
        dpg.set_item_pos('error_modal', pos=[400, 200])
        dpg.bind_item_theme('error_modal', t)


def reset_modal():
    set_header('--')
    show_modal(False)
    set_header('Start elaboration')


def show_modal(show):
    dpg.configure_item('error_modal', show=show)


def set_header(header):
    # type: (str) -> None
    """
    Set popup textual header (first line of the popup).

    :param header: text you want to set
    """
    dpg.set_value(f't1', header)
