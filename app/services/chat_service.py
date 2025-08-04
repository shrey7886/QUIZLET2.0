from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, text
from datetime import datetime, timedelta
import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from app.models.chat import (
    ChatRoom, ChatMessage, ChatParticipant, StudyGroup,
    StudyGroupMember, ChatNotification, MessageType, ChatRoomType
)
from app.models.user import User
from app.schemas.chat import (
    ChatRoomCreate, ChatMessageCreate, TopicSuggestionCreate,
    StudyGroupCreate, ChatSearch, MessageSearch
)

class ChatService:
    
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.room_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a user to the WebSocket"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Disconnect a user from the WebSocket"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def connect_to_room(self, websocket: WebSocket, room_id: int):
        """Connect a user to a specific room"""
        await websocket.accept()
        
        if room_id not in self.room_connections:
            self.room_connections[room_id] = []
        self.room_connections[room_id].append(websocket)
    
    def disconnect_from_room(self, websocket: WebSocket, room_id: int):
        """Disconnect a user from a specific room"""
        if room_id in self.room_connections:
            self.room_connections[room_id].remove(websocket)
            if not self.room_connections[room_id]:
                del self.room_connections[room_id]
    
    async def send_personal_message(self, message: str, user_id: int):
        """Send a personal message to a specific user"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except:
                    # Remove dead connections
                    self.active_connections[user_id].remove(connection)
    
    async def broadcast_to_room(self, message: str, room_id: int):
        """Broadcast a message to all users in a room"""
        if room_id in self.room_connections:
            dead_connections = []
            for connection in self.room_connections[room_id]:
                try:
                    await connection.send_text(message)
                except:
                    dead_connections.append(connection)
            
            # Remove dead connections
            for dead_connection in dead_connections:
                self.room_connections[room_id].remove(dead_connection)
    
    @staticmethod
    async def create_chat_room(db: Session, user_id: int, room_data: ChatRoomCreate) -> ChatRoom:
        """Create a new chat room"""
        
        # Check if user can create rooms
        if room_data.room_type == ChatRoomType.GLOBAL:
            # Only allow one global room
            existing_global = db.query(ChatRoom).filter(
                and_(ChatRoom.room_type == ChatRoomType.GLOBAL, ChatRoom.is_active == True)
            ).first()
            if existing_global:
                raise ValueError("Global room already exists")
        
        room = ChatRoom(
            created_by=user_id,
            **room_data.dict()
        )
        
        db.add(room)
        db.commit()
        db.refresh(room)
        
        # Add creator as participant
        participant = ChatParticipant(
            user_id=user_id,
            room_id=room.id,
            role="admin"
        )
        db.add(participant)
        db.commit()
        
        return room
    
    @staticmethod
    async def join_room(db: Session, user_id: int, room_id: int) -> ChatParticipant:
        """Join a chat room"""
        
        # Check if room exists and is active
        room = db.query(ChatRoom).filter(
            and_(ChatRoom.id == room_id, ChatRoom.is_active == True)
        ).first()
        
        if not room:
            raise ValueError("Room not found or inactive")
        
        # Check if user is already a participant
        existing_participant = db.query(ChatParticipant).filter(
            and_(ChatParticipant.user_id == user_id, ChatParticipant.room_id == room_id)
        ).first()
        
        if existing_participant:
            if not existing_participant.is_active:
                existing_participant.is_active = True
                db.commit()
            return existing_participant
        
        # Check room capacity
        participant_count = db.query(ChatParticipant).filter(
            and_(ChatParticipant.room_id == room_id, ChatParticipant.is_active == True)
        ).count()
        
        if participant_count >= room.max_participants:
            raise ValueError("Room is at maximum capacity")
        
        # Add participant
        participant = ChatParticipant(
            user_id=user_id,
            room_id=room_id,
            role="member"
        )
        
        db.add(participant)
        db.commit()
        db.refresh(participant)
        
        return participant
    
    @staticmethod
    async def leave_room(db: Session, user_id: int, room_id: int):
        """Leave a chat room"""
        
        participant = db.query(ChatParticipant).filter(
            and_(ChatParticipant.user_id == user_id, ChatParticipant.room_id == room_id)
        ).first()
        
        if participant:
            participant.is_active = False
            db.commit()
    
    @staticmethod
    async def send_message(db: Session, user_id: int, message_data: ChatMessageCreate) -> ChatMessage:
        """Send a message to a chat room"""
        
        # Check if user is a participant in the room
        participant = db.query(ChatParticipant).filter(
            and_(
                ChatParticipant.user_id == user_id,
                ChatParticipant.room_id == message_data.room_id,
                ChatParticipant.is_active == True
            )
        ).first()
        
        if not participant:
            raise ValueError("You are not a participant in this room")
        
        # Create message
        message = ChatMessage(
            user_id=user_id,
            **message_data.dict()
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        
        # Update last read time for sender
        participant.last_read_at = datetime.now()
        db.commit()
        
        return message
    
    @staticmethod
    async def get_room_messages(
        db: Session,
        room_id: int,
        limit: int = 50,
        offset: int = 0,
        user_id: Optional[int] = None
    ) -> List[ChatMessage]:
        """Get messages from a chat room"""
        
        query = db.query(ChatMessage).filter(
            and_(ChatMessage.room_id == room_id, ChatMessage.is_deleted == False)
        ).order_by(desc(ChatMessage.created_at))
        
        messages = query.offset(offset).limit(limit).all()
        
        # Add user information
        for message in messages:
            user = db.query(User).filter(User.id == message.user_id).first()
            if user:
                message.username = user.username
        
        # Update last read time for user
        if user_id:
            participant = db.query(ChatParticipant).filter(
                and_(
                    ChatParticipant.user_id == user_id,
                    ChatParticipant.room_id == room_id
                )
            ).first()
            if participant:
                participant.last_read_at = datetime.now()
                db.commit()
        
        return messages
    
    # Temporarily disabled due to TopicSuggestion model issues
    # @staticmethod
    # async def create_topic_suggestion(
    #     db: Session,
    #     user_id: int,
    #     suggestion_data: TopicSuggestionCreate
    # ) -> TopicSuggestion:
    #     """Create a topic suggestion"""
    #     
    #     suggestion = TopicSuggestion(
    #         user_id=user_id,
    #         **suggestion_data.dict()
    #     )
    #     
    #     db.add(suggestion)
    #     db.commit()
    #     db.refresh(suggestion)
    #     
    #     return suggestion
    
    # @staticmethod
    # async def vote_on_suggestion(
    #     db: Session,
    #     user_id: int,
    #     suggestion_id: int,
    #     vote_type: str
    # ) -> TopicSuggestion:
    #     """Vote on a topic suggestion"""
    #     
    #     suggestion = db.query(TopicSuggestion).filter(TopicSuggestion.id == suggestion_id).first()
    #     if not suggestion:
    #         raise ValueError("Suggestion not found")
    #     
    #     if vote_type == "upvote":
    #         suggestion.upvotes += 1
    #     elif vote_type == "downvote":
    #         suggestion.downvotes += 1
    #     else:
    #         raise ValueError("Invalid vote type")
    #     
    #     db.commit()
    #     db.refresh(suggestion)
    #     
    #     return suggestion
    
    @staticmethod
    async def create_study_group(
        db: Session,
        user_id: int,
        group_data: StudyGroupCreate
    ) -> StudyGroup:
        """Create a study group"""
        
        group = StudyGroup(
            created_by=user_id,
            **group_data.dict()
        )
        
        db.add(group)
        db.commit()
        db.refresh(group)
        
        # Add creator as member
        member = StudyGroupMember(
            group_id=group.id,
            user_id=user_id,
            role="admin"
        )
        db.add(member)
        
        # Create chat room for the group
        room = ChatRoom(
            name=f"Study Group: {group.name}",
            description=f"Chat room for {group.name} study group",
            room_type=ChatRoomType.STUDY_GROUP,
            topic=group.topic,
            created_by=user_id,
            max_participants=group.max_members
        )
        db.add(room)
        db.commit()
        
        # Add creator to chat room
        participant = ChatParticipant(
            user_id=user_id,
            room_id=room.id,
            role="admin"
        )
        db.add(participant)
        db.commit()
        
        return group
    
    @staticmethod
    async def join_study_group(db: Session, user_id: int, group_id: int) -> StudyGroupMember:
        """Join a study group"""
        
        # Check if group exists and is public
        group = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
        if not group:
            raise ValueError("Study group not found")
        
        if not group.is_public:
            raise ValueError("This study group is private")
        
        # Check if user is already a member
        existing_member = db.query(StudyGroupMember).filter(
            and_(StudyGroupMember.group_id == group_id, StudyGroupMember.user_id == user_id)
        ).first()
        
        if existing_member:
            return existing_member
        
        # Check group capacity
        member_count = db.query(StudyGroupMember).filter(StudyGroupMember.group_id == group_id).count()
        if member_count >= group.max_members:
            raise ValueError("Study group is at maximum capacity")
        
        # Add member
        member = StudyGroupMember(
            group_id=group_id,
            user_id=user_id,
            role="member"
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        
        return member
    
    @staticmethod
    async def get_user_rooms(db: Session, user_id: int) -> List[ChatRoom]:
        """Get all rooms a user is participating in"""
        
        rooms = db.query(ChatRoom).join(ChatParticipant).filter(
            and_(
                ChatParticipant.user_id == user_id,
                ChatParticipant.is_active == True,
                ChatRoom.is_active == True
            )
        ).all()
        
        # Add participant count
        for room in rooms:
            room.participant_count = db.query(ChatParticipant).filter(
                and_(ChatParticipant.room_id == room.id, ChatParticipant.is_active == True)
            ).count()
        
        return rooms
    
    @staticmethod
    async def search_rooms(db: Session, search_data: ChatSearch) -> List[ChatRoom]:
        """Search for chat rooms"""
        
        query = db.query(ChatRoom).filter(ChatRoom.is_active == True)
        
        if search_data.query:
            query = query.filter(
                or_(
                    ChatRoom.name.ilike(f"%{search_data.query}%"),
                    ChatRoom.description.ilike(f"%{search_data.query}%")
                )
            )
        
        if search_data.room_type:
            query = query.filter(ChatRoom.room_type == search_data.room_type)
        
        if search_data.topic:
            query = query.filter(ChatRoom.topic.ilike(f"%{search_data.topic}%"))
        
        rooms = query.offset(search_data.offset).limit(search_data.limit).all()
        
        # Add participant count
        for room in rooms:
            room.participant_count = db.query(ChatParticipant).filter(
                and_(ChatParticipant.room_id == room.id, ChatParticipant.is_active == True)
            ).count()
        
        return rooms
    
    @staticmethod
    async def search_messages(db: Session, search_data: MessageSearch) -> List[ChatMessage]:
        """Search for messages"""
        
        query = db.query(ChatMessage).filter(ChatMessage.is_deleted == False)
        
        if search_data.query:
            query = query.filter(ChatMessage.content.ilike(f"%{search_data.query}%"))
        
        if search_data.message_type:
            query = query.filter(ChatMessage.message_type == search_data.message_type)
        
        if search_data.user_id:
            query = query.filter(ChatMessage.user_id == search_data.user_id)
        
        if search_data.start_date:
            query = query.filter(ChatMessage.created_at >= search_data.start_date)
        
        if search_data.end_date:
            query = query.filter(ChatMessage.created_at <= search_data.end_date)
        
        messages = query.order_by(desc(ChatMessage.created_at)).offset(search_data.offset).limit(search_data.limit).all()
        
        # Add user information
        for message in messages:
            user = db.query(User).filter(User.id == message.user_id).first()
            if user:
                message.username = user.username
        
        return messages
    
    @staticmethod
    async def create_notification(
        db: Session,
        user_id: int,
        room_id: int,
        notification_type: str,
        content: str,
        message_id: Optional[int] = None
    ) -> ChatNotification:
        """Create a chat notification"""
        
        notification = ChatNotification(
            user_id=user_id,
            room_id=room_id,
            message_id=message_id,
            notification_type=notification_type,
            content=content
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        return notification
    
    @staticmethod
    async def get_user_notifications(
        db: Session,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[ChatNotification]:
        """Get notifications for a user"""
        
        notifications = db.query(ChatNotification).filter(
            ChatNotification.user_id == user_id
        ).order_by(desc(ChatNotification.created_at)).offset(offset).limit(limit).all()
        
        return notifications
    
    @staticmethod
    async def mark_notification_read(db: Session, notification_id: int, user_id: int):
        """Mark a notification as read"""
        
        notification = db.query(ChatNotification).filter(
            and_(ChatNotification.id == notification_id, ChatNotification.user_id == user_id)
        ).first()
        
        if notification:
            notification.is_read = True
            db.commit()
    
    @staticmethod
    async def get_chat_stats(db: Session) -> Dict[str, Any]:
        """Get chat statistics"""
        
        total_messages = db.query(ChatMessage).filter(ChatMessage.is_deleted == False).count()
        total_rooms = db.query(ChatRoom).filter(ChatRoom.is_active == True).count()
        
        # Active participants (users who sent messages in last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        active_participants = db.query(ChatMessage.user_id).filter(
            ChatMessage.created_at >= yesterday
        ).distinct().count()
        
        # Messages today
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        messages_today = db.query(ChatMessage).filter(
            ChatMessage.created_at >= today
        ).count()
        
        # Popular topics (rooms with most messages)
        popular_topics = db.query(
            ChatRoom.topic,
            func.count(ChatMessage.id).label('message_count')
        ).join(ChatMessage).filter(
            and_(ChatRoom.topic.isnot(None), ChatMessage.is_deleted == False)
        ).group_by(ChatRoom.topic).order_by(desc(text('message_count'))).limit(10).all()
        
        return {
            "total_messages": total_messages,
            "total_rooms": total_rooms,
            "active_participants": active_participants,
            "messages_today": messages_today,
            "popular_topics": [{"topic": t.topic, "count": t.message_count} for t in popular_topics]
        }
    
    @staticmethod
    async def get_room_stats(db: Session, room_id: int) -> Dict[str, Any]:
        """Get statistics for a specific room"""
        
        total_messages = db.query(ChatMessage).filter(
            and_(ChatMessage.room_id == room_id, ChatMessage.is_deleted == False)
        ).count()
        
        active_participants = db.query(ChatParticipant).filter(
            and_(ChatParticipant.room_id == room_id, ChatParticipant.is_active == True)
        ).count()
        
        # Messages today
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        messages_today = db.query(ChatMessage).filter(
            and_(ChatMessage.room_id == room_id, ChatMessage.created_at >= today)
        ).count()
        
        return {
            "room_id": room_id,
            "total_messages": total_messages,
            "active_participants": active_participants,
            "messages_today": messages_today
        }

# Global chat service instance
chat_service = ChatService() 