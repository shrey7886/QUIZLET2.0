from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    TEXT = "text"
    TOPIC_SHARE = "topic_share"
    QUIZ_SHARE = "quiz_share"
    RESULT_SHARE = "result_share"
    SUGGESTION = "suggestion"
    SYSTEM = "system"

class ChatRoomType(str, Enum):
    GLOBAL = "global"
    TOPIC_BASED = "topic_based"
    STUDY_GROUP = "study_group"
    PRIVATE = "private"

# Chat Room Schemas
class ChatRoomBase(BaseModel):
    name: str = Field(..., description="Room name")
    description: Optional[str] = Field(None, description="Room description")
    room_type: ChatRoomType = Field(..., description="Type of chat room")
    topic: Optional[str] = Field(None, description="Topic for topic-based rooms")
    max_participants: int = Field(default=100, ge=1, le=1000)

class ChatRoomCreate(ChatRoomBase):
    pass

class ChatRoomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    topic: Optional[str] = None
    max_participants: Optional[int] = Field(None, ge=1, le=1000)

class ChatRoom(ChatRoomBase):
    id: int
    created_by: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Chat Participant Schemas
class ChatParticipantBase(BaseModel):
    role: str = Field(default="member", description="member, moderator, admin")

class ChatParticipant(ChatParticipantBase):
    id: int
    user_id: int
    room_id: int
    joined_at: datetime
    last_read_at: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True

# Chat Message Schemas
class ChatMessageBase(BaseModel):
    message_type: MessageType = Field(default=MessageType.TEXT)
    content: str = Field(..., description="Message content")
    message_metadata: Dict[str, Any] = Field(default_factory=dict)
    reply_to_id: Optional[int] = Field(None, description="ID of message being replied to")

class ChatMessageCreate(ChatMessageBase):
    room_id: int

class ChatMessageUpdate(BaseModel):
    content: str

class ChatMessage(ChatMessageBase):
    id: int
    room_id: int
    user_id: int
    is_edited: bool
    edited_at: Optional[datetime] = None
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Topic Suggestion Schemas
class TopicSuggestionBase(BaseModel):
    topic: str = Field(..., description="Suggested topic")
    description: Optional[str] = Field(None, description="Topic description")
    difficulty: Optional[str] = Field(None, description="Easy, Medium, Hard")
    category: Optional[str] = Field(None, description="Topic category")

class TopicSuggestionCreate(TopicSuggestionBase):
    pass

class TopicSuggestionUpdate(BaseModel):
    description: Optional[str] = None
    difficulty: Optional[str] = None
    category: Optional[str] = None

class TopicSuggestion(TopicSuggestionBase):
    id: int
    user_id: int
    upvotes: int
    downvotes: int
    status: str
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Study Group Schemas
class StudyGroupBase(BaseModel):
    name: str = Field(..., description="Group name")
    description: Optional[str] = Field(None, description="Group description")
    topic: str = Field(..., description="Study topic")
    difficulty: str = Field(..., description="Difficulty level")
    max_members: int = Field(default=20, ge=1, le=100)
    is_public: bool = Field(default=True, description="Public or private group")

class StudyGroupCreate(StudyGroupBase):
    pass

class StudyGroup(StudyGroupBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Study Group Member Schemas
class StudyGroupMemberBase(BaseModel):
    role: str = Field(default="member", description="member, moderator, admin")

class StudyGroupMember(StudyGroupMemberBase):
    id: int
    group_id: int
    user_id: int
    joined_at: datetime
    last_active: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Chat Notification Schemas
class ChatNotificationBase(BaseModel):
    notification_type: str = Field(..., description="message, mention, topic_share, etc.")
    content: str = Field(..., description="Notification content")

class ChatNotification(ChatNotificationBase):
    id: int
    user_id: int
    room_id: int
    message_id: Optional[int] = None
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Search and List Schemas
class ChatSearch(BaseModel):
    query: Optional[str] = None
    room_type: Optional[ChatRoomType] = None
    topic: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

class MessageSearch(BaseModel):
    query: Optional[str] = None
    message_type: Optional[MessageType] = None
    user_id: Optional[int] = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

class ChatRoomList(BaseModel):
    rooms: List[ChatRoom]
    total_count: int
    has_more: bool

class ChatMessageList(BaseModel):
    messages: List[ChatMessage]
    total_count: int
    has_more: bool

# Statistics Schemas
class ChatStats(BaseModel):
    total_rooms: int
    total_messages: int
    active_users: int
    messages_today: int
    topics_discussed: List[str]

class RoomStats(BaseModel):
    room_id: int
    total_messages: int
    active_participants: int
    messages_today: int
    average_messages_per_day: float 