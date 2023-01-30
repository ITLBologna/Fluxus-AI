from dearpygui import dearpygui as dpg

from front_end import theme


def build_modal():
    with dpg.popup(dpg.last_item(), modal=True, tag='load_modal'):
        dpg.add_text('Start elaboration', tag='header_text')
        dpg.add_progress_bar(tag='prog_bar')
        dpg.set_value('prog_bar', 0.0)
        dpg.add_text('Progress: 0.00 %', tag='prog_txt')
        show_modal(False)

        t = theme.get_pop_theme()
        dpg.configure_item('load_modal', label='Elaboration')
        dpg.configure_item('load_modal', min_size=[330, 100])
        dpg.set_item_pos('load_modal', pos=[400, 200])
        dpg.bind_item_theme('load_modal', t)


def reset_modal():
    set_header('--')
    set_progress(0)
    show_modal(False)
    set_header('Start Elaboration')


def show_modal(show):
    dpg.configure_item('load_modal', show=show)


class ProgressBar(object):

    def __init__(self, done_callback):
        self.done_callback = done_callback
        self.prog_txt = 'Progress: $PERC %'


    def set_progress(self, progress):
        # type: (float) -> None
        """
        Set loading progress.

        :param progress: progress value in range [0, 1],
            where 0 is 0% and 1 is 100%
        """
        dpg.set_value('prog_bar', progress)
        __p = progress * 100

        txt = self.prog_txt.replace('$PERC', f'{__p:6.02f}')
        dpg.set_value('prog_txt', txt)

        if progress >= 1:
            self.done_callback()


def set_progress(progress):
    # type: (float) -> None
    """
    Set loading progress.

    :param progress: progress value in range [0, 1],
        where 0 is 0% and 1 is 100%
    """
    dpg.set_value('prog_bar', progress)
    __p = progress * 100
    dpg.set_value('prog_txt', f'Progress: {__p:6.02f} %')


def set_header(header):
    # type: (str) -> None
    """
    Set popup textual header (first line of the popup).

    :param header: text you want to set
    """
    dpg.set_value('header_text', header)
