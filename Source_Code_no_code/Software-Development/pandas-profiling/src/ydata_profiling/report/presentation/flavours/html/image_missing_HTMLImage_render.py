from ydata_profiling.report.presentation.core import Image



class HTMLImage(Image):
    def render(self) -> str:
        """Render the HTML content of an image. It uses a template file called "diagram.html" and passes the content of the image as arguments to the template.
        Input-Output Arguments
        :param self: HTMLImage. An instance of the HTMLImage class.
        :return: str. The rendered HTML content of the image.
        """