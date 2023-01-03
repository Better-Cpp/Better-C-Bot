import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Rule:
    number: int
    rule: str
    content: Optional[str]
    subrules: list['Rule']

    def __str__(self) -> str:
        text = f"**Rule {self.number}: {self.rule}**"
        if self.content:
            text += f"\n{self.content}"
        return text


class Rules(dict[int, Rule]):
    def parse(self, text: str) -> None:
        matches = re.finditer(r"\*\*RULE (?P<number>\d+): (?P<rule>.*)\*\*\n"
                              r"(?P<content>(.|\s)*?)(?=[\n ]+(\*\*RULE)|$)",
                              text)
        for match in matches:
            number = int(match.group('number'))
            rule = match.group('rule')
            content = match.group('content')

            subrules = re.finditer(r"  ⦁  (?P<rule>.*)",
                                   content)
            self[number] = Rule(number,
                                rule,
                                content,
                                [subrule.group('rule') for subrule in subrules])
