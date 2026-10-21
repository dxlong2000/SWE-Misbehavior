from ydata_profiling.report.presentation.core import FrequencyTable



class HTMLFrequencyTable(FrequencyTable):
    def render(self) -> str:
        """This function renders an HTML frequency table based on the content provided. It checks if the content is a list of rows or a single row, and then uses a template to generate the HTML code for the frequency table.
        Input-Output Arguments
        :param self: HTMLFrequencyTable. An instance of the HTMLFrequencyTable class.
        :return: str. The rendered HTML code for the frequency table.
        """