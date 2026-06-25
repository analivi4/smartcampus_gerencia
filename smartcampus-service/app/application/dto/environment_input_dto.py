from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class DeviceInputDTO:
  id: str
  type: str

@dataclass
class RoomInputDTO:
  name: str
  type: str
  occupancy: int
  devices: List[DeviceInputDTO]

@dataclass
class EnvironmentInputDTO:
  name: str
  rooms: List[RoomInputDTO]

@dataclass
class TimedEventDTO:
  time: float
  type: str
  predicate: Optional[str] = None
  fluent: Optional[str] = None
  args: Optional[List[str]] = None
  value: Optional[int] = None

@dataclass
class InitDTO:
  fluents: Dict[str, Any]
  timed_events: List[TimedEventDTO]

@dataclass
class GoalPredicateDTO:
  predicate: str
  args: Optional[List[str]] = None

@dataclass
class GoalDTO:
  predicates: List[GoalPredicateDTO]

@dataclass
class ObjectsDTO:
  rooms: List[str]
  air_conditioners: List[str]
  lights: List[str]
  slots: Optional[List[str]] = None

@dataclass
class ProblemDefinitionDTO:
  name: str
  domain: str
  objects: ObjectsDTO
  init: InitDTO
  goal: GoalDTO
  metric: Optional[str] = None
  device_map: Optional[Dict[str, str]] = None