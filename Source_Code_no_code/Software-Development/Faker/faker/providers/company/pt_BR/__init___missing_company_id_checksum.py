from typing import List

from .. import Provider as CompanyProvider


def company_id_checksum(digits: List[int]) -> List[int]:
    """Calculate the checksum of the company ID based on the given digits. It first calculates the checksum based on the weights and digits, and then appends the calculated checksum to the input digits. The weights of check digits is [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2].
    Input-Output Arguments
    :param digits: List of integers. The list of digits representing the company ID.
    :return: List of integers. The calculated checksum digits.
    """


class Provider(CompanyProvider):
    formats = (
        "{{last_name}} {{company_suffix}}",
        "{{last_name}} {{last_name}} {{company_suffix}}",
        "{{last_name}}",
        "{{last_name}}",
    )

    catch_phrase_formats = ("{{catch_phrase_noun}} {{catch_phrase_verb}} {{catch_phrase_attribute}}",)

    nouns = (
        "a segurança",
        "o prazer",
        "o conforto",
        "a simplicidade",
        "a certeza",
        "a arte",
        "o poder",
        "o direito",
        "a possibilidade",
        "a vantagem",
        "a liberdade",
    )

    verbs = (
        "de conseguir",
        "de avançar",
        "de evoluir",
        "de mudar",
        "de inovar",
        "de ganhar",
        "de atingir seus objetivos",
        "de concretizar seus projetos",
        "de realizar seus sonhos",
    )

    attributes = (
        "de maneira eficaz",
        "mais rapidamente",
        "mais facilmente",
        "simplesmente",
        "com toda a tranquilidade",
        "antes de tudo",
        "naturalmente",
        "sem preocupação",
        "em estado puro",
        "com força total",
        "direto da fonte",
        "com confiança",
    )

    company_suffixes = ("S/A", "S.A.", "Ltda.", "- ME", "- EI", "e Filhos")

    def catch_phrase_noun(self) -> str:
        """
        Returns a random catch phrase noun.
        """
        return self.random_element(self.nouns)

    def catch_phrase_attribute(self) -> str:
        """
        Returns a random catch phrase attribute.
        """
        return self.random_element(self.attributes)

    def catch_phrase_verb(self) -> str:
        """
        Returns a random catch phrase verb.
        """
        return self.random_element(self.verbs)

    def catch_phrase(self) -> str:
        """
        :example: 'a segurança de evoluir sem preocupação'
        """
        pattern: str = self.random_element(self.catch_phrase_formats)
        catch_phrase = self.generator.parse(pattern)
        catch_phrase = catch_phrase[0].upper() + catch_phrase[1:]
        return catch_phrase

    def company_id(self) -> str:
        digits: List[int] = list(self.random_sample(range(10), 8))
        digits += [0, 0, 0, 1]
        digits += company_id_checksum(digits)
        return "".join(str(d) for d in digits)

    def cnpj(self) -> str:
        digits = self.company_id()
        return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"