from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union

class TimedEventRequest(BaseModel):
	time: float
	type: str 
	predicate: Optional[str] = None
	fluent: Optional[str] = None
	args: Optional[List[str]] = None
	value: Optional[float] = None

class InitRequest(BaseModel):
	fluents: Dict[str, Union[Dict[str, Any], int, float, bool]]
	timed_events: List[TimedEventRequest]

class GoalPredicateRequest(BaseModel):
	predicate: str
	args: Optional[List[str]] = None

class GoalRequest(BaseModel):
	predicates: List[GoalPredicateRequest]

class ObjectsRequest(BaseModel):
	rooms: List[str]
	air_conditioners: List[str]
	lights: List[str]
	slots: Optional[List[str]] = None

class EnvironmentRequest(BaseModel):
	name: str
	domain: str
	objects: ObjectsRequest
	init: InitRequest
	goal: GoalRequest
	metric: Optional[str] = None
	device_map: Optional[Dict[str, str]] = None