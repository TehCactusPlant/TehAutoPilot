from Client.models.core import Reference
from Client.models.image_process import HSVImageProcess
from Client.ui.widgets.sub_panels.image_panels import ImageProcessHSVAdjuster, ContourMatchingPanel
from Client.ui.widgets.sub_panels.sub_panel import SubPanel


class HSVContourPanel(SubPanel):
    def __init__(self, parent, im_proc: HSVImageProcess, reference: Reference):
        super().__init__(parent)

        self.current_reference = reference
        self.current_im_proc = im_proc

        self.main_hsv_adjuster = ImageProcessHSVAdjuster(self, im_proc)
        self.main_save_contours_panel = ContourMatchingPanel(self, im_proc)
        self.main_save_contours_panel.current_contour = reference
        self.main_hsv_adjuster.grid(row=0, column=0)
        self.main_save_contours_panel.grid(row=0, column=1, sticky='n')
