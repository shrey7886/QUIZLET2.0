from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class MessageType(enum.Enum):
    TEXT = "text"
    TOPIC_SHARE = "topic_share"
    QUIZ_SHARE = "quiz_share"
    RESULT_SHARE = "result_share"
    SUGGESTION = "suggestion"
    SYSTEM = "system"

class ChatRoomType(enum.Enum):
    GLOBAL = "global"
    TOPIC_BASED = "topic_based"
    STUDY_GROUP = "study_group"
    PRIVATE = "private"

class ChatRoom(Base):
    __tablename__ = "chat_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    room_type = Column(Enum(ChatRoomType), nullable=False)
    topic = Column(String, nullable=True)  # For topic-based rooms
    is_active = Column(Boolean, default=True)
    max_participants = Column(Integer, default=100)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="created_rooms")
    participants = relationship("ChatParticipant", back_populates="room")
    messages = relationship("ChatMessage", back_populates="room")

class ChatParticipant(Base):
    __tablename__ = "chat_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    role = Column(String, default="member")  # member, moderator, admin
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    last_read_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="chat_participations")
    room = relationship("ChatRoom", back_populates="participants")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message_type = Column(Enum(MessageType), nullable=False, default=MessageType.TEXT)
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, default=dict)  # For topic shares, quiz shares, etc.
    reply_to_id = Column(Integer, ForeignKey("chat_messages.id"), nullable=True)
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    room = relationship("ChatRoom", back_populates="messages")
    user = relationship("User", back_populates="chat_messages")
    reply_to = relationship("ChatMessage", remote_side=[id])
    replies = relationship("ChatMessage", back_populates="reply_to")

# Temporarily disabled to fix database relationship issues
# class TopicSuggestion(Base):
#     __tablename__ = "topic_suggestions"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     topic = Column(String, nullable=False)
#     description = Column(Text, nullable=True)
#     difficulty = Column(String, nullable=True)  # Easy, Medium, Hard
#     category = Column(String, nullable=True)
#     upvotes = Column(Integer, default=0)
#     downvotes = Column(Integer, default=0)
#     status = Column(String, default="pending")  # pending, approved, rejected
#     approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
#     approved_at = Column(DateTime(timezone=True), nullable=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     
#     # Relationships
#     user = relationship("User", back_populates="topic_suggestions")
#     approver = relationship("User", foreign_keys=[approved_by])

class StudyGroup(Base):
    __tablename__ = "study_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    topic = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    max_members = Column(Integer, default=20)
    is_public = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="created_study_groups")
    members = relationship("StudyGroupMember", back_populates="group")

class StudyGroupMember(Base):
    __tablename__ = "study_group_members"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("study_groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, default="member")  # member, moderator, admin
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    group = relationship("StudyGroup", back_populates="members")
    user = relationship("User", back_populates="study_group_memberships")

class ChatNotification(Base):
    __tablename__ = "chat_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    message_id = Column(Integer, ForeignKey("chat_messages.id"), nullable=True)
    notification_type = Column(String, nullable=False)  # message, mention, topic_share, etc.
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_notifications")
    room = relationship("ChatRoom")
    message = relationship("ChatMessage") 