from src.imaging.processing import ImageProcessor
from src.imaging.scanning import ImageScanner
from src.data.bank import DataBank
from src.models.management import Manager


class ImageManager(Manager):
    def __init__(self):
        super().__init__()
        self.im_processor = ImageProcessor()
        self.im_scanner = ImageScanner()
        self.data_bank = DataBank()

    def process_images(self):
        self.im_processor.process_images()
        output_image = self.im_processor.get_image_process("main output").get_main_image()
        self.im_scanner.rolling_scan()
        for tracker in self.im_scanner.trackers:
            if tracker.matched:
                tracker.draw_match(output_image)
