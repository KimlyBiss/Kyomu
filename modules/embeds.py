from discord import Embed

class HelpEmbed(Embed):
    def __init__(self):
        super().__init__(
            title="🌸 Свиток Мудрости Кёму",
            description="*«Познай все возможности этого мира»*",
            color=0xA58FAA
        )
        self.set_footer(text="Используй команды с умом")

class BioEmbed(Embed):
    def __init__(self):
        super().__init__(
            title="🎴 Узнать о Кёму-тануки",
            color=0xE5D4C0
        )