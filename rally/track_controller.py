import dataclasses
import enum
from typing import Optional, Union, Tuple
from yaml import safe_load

from .models import TrackElementGroupAnswer, Group
from .qr_code import generate_qr_code_text


@dataclasses.dataclass
class Coordinates:
    latitude: float
    longitude: float


class TrackElementType(enum.Enum):
    MANDATORY_QUESTION = "mandatory_question"
    OPTIONAL_QUESTION = "optional_question"
    QR_CODE = "qr_code"
    STORY = "story"
    START = "start"
    END = "end"


@dataclasses.dataclass
class TrackElement:
    id: str
    type: TrackElementType
    text: str
    hint: Optional[str] = None
    internal_comment: Optional[str] = None
    location: Optional[Coordinates] = None


class TrackController:

    def __init__(self):
        config = safe_load(open("data/track.yaml", "rb"))

        self.qr_salt = config["qr_salt"]
        self.start_track_element = TrackElement(
            id="start",
            type=TrackElementType.START,
            text=config.get("start_message")
        )

        self.end_track_element = TrackElement(
            id="end",
            type=TrackElementType.END,
            text=config.get("end_message")
        )
        self.track_elements = [TrackElement(
            id=element["id"],
            type=TrackElementType(element["type"]),
            text=element.get("text"),
            internal_comment=element.get("internal_comment"),
            hint=element.get("hint"),
            location=Coordinates(element["location"]["latitude"], element["location"]["longitude"]) if element.get(
                "location") else None,
        ) for element in config["elements"]]

        self.track_element_indexes = {element.id: index for index, element in enumerate(self.track_elements)}

    def get_current_element(self, group: Group) -> Optional[Tuple[Optional[int], TrackElement]]:
        current_element_id = group.current_element_id
        if current_element_id == self.start_track_element.id:
            return None, self.start_track_element
        elif current_element_id == self.end_track_element.id:
            return None, self.end_track_element
        else:
            current_element_index = self.track_element_indexes.get(current_element_id)
            if current_element_index is None:
                return None
            return current_element_index, self.track_elements[current_element_index]

    def process_answer(self, element_id: str, group: Group, answer: Optional[str]) -> Union[TrackElement, str]:
        current_element_index, current_element = self.get_current_element(group)
        if element_id != current_element.id:
            return "Duplicate. Bitte neuladen."

        if current_element.type == TrackElementType.MANDATORY_QUESTION or \
                current_element.type == TrackElementType.OPTIONAL_QUESTION:
            if answer is None:
                return "Keine Antwort angegeben."
            else:
                TrackElementGroupAnswer(group=group,
                                        element_id=current_element.id,
                                        answer=answer).save()
        elif current_element.type == TrackElementType.QR_CODE:
            if answer is None:
                return "QR-Code nicht gescannt."
            elif answer != generate_qr_code_text(self.qr_salt, current_element.id):
                return "Falscher QR-Code."
            else:
                TrackElementGroupAnswer(group=group,
                                        element_id=current_element.id).save()
        else:
            if current_element.type == TrackElementType.END:
                return "Ende"
            TrackElementGroupAnswer(group=group,
                                    element_id=current_element.id).save()

        if current_element == self.start_track_element:
            next_element =  self.track_elements[self.track_element_indexes[group.starting_element_id]]
        else:
            next_track_element_index = (current_element_index + 1) % len(self.track_elements)
            next_element = self.track_elements[next_track_element_index]
            if next_element.id == group.starting_element_id:
                next_element = self.end_track_element
        group.current_element_id = next_element.id
        group.save()
        return next_element

    def get_progress(self, group: Group) -> float:
        if group.current_element_id == self.start_track_element.id:
            return 0
        elif group.current_element_id == self.end_track_element.id:
            return 1
        else:
            current_index = self.track_element_indexes.get(group.current_element_id)
            if current_index is None:
                return -1
            offset = self.track_element_indexes[group.starting_element_id]
            if current_index < offset:
                current_index += len(self.track_elements)
            return (current_index - offset) / len(self.track_elements)



track_controller = TrackController()
