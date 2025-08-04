from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from datetime import datetime
import json

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.chat import ChatRoom, ChatMessage, ChatParticipant, StudyGroup, StudyGroupMember, ChatNotification
from app.services.chat_service import chat_service, ChatService
from app.schemas.chat import (
    ChatRoomCreate, ChatRoomUpdate, ChatRoom as ChatRoomSchema, ChatMessageCreate, ChatMessageUpdate, ChatMessage as ChatMessageSchema,
    TopicSuggestionCreate, TopicSuggestionUpdate, TopicSuggestion as TopicSuggestionSchema, StudyGroupCreate, StudyGroup as StudyGroupSchema,
    ChatNotification as ChatNotificationSchema, ChatSearch, MessageSearch, ChatRoomList, ChatMessageList, ChatStats, RoomStats
)

router = APIRouter()

# WebSocket endpoint for real-time chat
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await chat_service.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages
            message_data = json.loads(data)
            
            if message_data["type"] == "message":
                # Broadcast message to room
                await chat_service.broadcast_to_room(data, message_data["room_id"])
            elif message_data["type"] == "typing":
                # Broadcast typing indicator
                await chat_service.broadcast_to_room(data, message_data["room_id"])
                
    except WebSocketDisconnect:
        chat_service.disconnect(websocket, user_id)

# WebSocket endpoint for room-specific chat
@router.websocket("/ws/room/{room_id}/{user_id}")
async def room_websocket_endpoint(websocket: WebSocket, room_id: int, user_id: int):
    await chat_service.connect_to_room(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle room-specific messages
            await chat_service.broadcast_to_room(data, room_id)
    except WebSocketDisconnect:
        chat_service.disconnect_from_room(websocket, room_id)

# Chat Room Management
@router.post("/rooms", response_model=ChatRoomSchema)
async def create_chat_room(
    room_data: ChatRoomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat room"""
    try:
        room = await ChatService.create_chat_room(db, current_user.id, room_data)
        return room
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/rooms", response_model=List[ChatRoomSchema])
async def get_user_rooms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all rooms the current user is participating in"""
    try:
        rooms = await ChatService.get_user_rooms(db, current_user.id)
        return rooms
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load rooms: {str(e)}")

@router.get("/rooms/search", response_model=List[ChatRoomSchema])
async def search_rooms(
    search_data: ChatSearch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for chat rooms"""
    try:
        rooms = await ChatService.search_rooms(db, search_data)
        return rooms
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/rooms/{room_id}", response_model=ChatRoomSchema)
async def get_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific chat room"""
    try:
        room = db.query(ChatRoom).filter(
            and_(ChatRoom.id == room_id, ChatRoom.is_active == True)
        ).first()
        
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        # Add participant count
        room.participant_count = db.query(ChatParticipant).filter(
            and_(ChatParticipant.room_id == room_id, ChatParticipant.is_active == True)
        ).count()
        
        return room
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load room: {str(e)}")

@router.put("/rooms/{room_id}", response_model=ChatRoomSchema)
async def update_room(
    room_id: int,
    room_data: ChatRoomUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a chat room (admin only)"""
    try:
        room = db.query(ChatRoom).filter(
            and_(ChatRoom.id == room_id, ChatRoom.created_by == current_user.id)
        ).first()
        
        if not room:
            raise HTTPException(status_code=404, detail="Room not found or access denied")
        
        for field, value in room_data.dict(exclude_unset=True).items():
            setattr(room, field, value)
        
        db.commit()
        db.refresh(room)
        return room
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update room: {str(e)}")

@router.post("/rooms/{room_id}/join")
async def join_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a chat room"""
    try:
        participant = await ChatService.join_room(db, current_user.id, room_id)
        return {"message": "Successfully joined room", "participant": participant}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/rooms/{room_id}/leave")
async def leave_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Leave a chat room"""
    try:
        await ChatService.leave_room(db, current_user.id, room_id)
        return {"message": "Successfully left room"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Chat Messages
@router.post("/messages", response_model=ChatMessageSchema)
async def send_message(
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to a chat room"""
    try:
        message = await ChatService.send_message(db, current_user.id, message_data)
        
        # Add user information
        message.username = current_user.username
        
        # Broadcast to room via WebSocket
        await chat_service.broadcast_to_room(
            json.dumps({
                "type": "message",
                "message": message.__dict__,
                "room_id": message.room_id
            }),
            message.room_id
        )
        
        return message
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/rooms/{room_id}/messages", response_model=List[ChatMessageSchema])
async def get_room_messages(
    room_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages from a chat room"""
    try:
        messages = await ChatService.get_room_messages(
            db, room_id, limit, offset, current_user.id
        )
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load messages: {str(e)}")

@router.put("/messages/{message_id}", response_model=ChatMessageSchema)
async def edit_message(
    message_id: int,
    message_data: ChatMessageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Edit a message (only by the author)"""
    try:
        message = db.query(ChatMessage).filter(
            and_(ChatMessage.id == message_id, ChatMessage.user_id == current_user.id)
        ).first()
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found or access denied")
        
        message.content = message_data.content
        message.is_edited = True
        message.edited_at = datetime.now()
        
        db.commit()
        db.refresh(message)
        return message
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to edit message: {str(e)}")

@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a message (only by the author or admin)"""
    try:
        message = db.query(ChatMessage).filter(
            and_(ChatMessage.id == message_id, ChatMessage.user_id == current_user.id)
        ).first()
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found or access denied")
        
        message.is_deleted = True
        message.deleted_at = datetime.now()
        
        db.commit()
        return {"message": "Message deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete message: {str(e)}")

@router.get("/messages/search", response_model=List[ChatMessageSchema])
async def search_messages(
    search_data: MessageSearch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for messages"""
    try:
        messages = await ChatService.search_messages(db, search_data)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Topic Suggestions
# Temporarily disabled due to TopicSuggestion model issues
# @router.post("/suggestions", response_model=TopicSuggestionSchema)
# async def create_topic_suggestion(
#     suggestion_data: TopicSuggestionCreate,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Create a topic suggestion"""
#     try:
#         suggestion = await ChatService.create_topic_suggestion(db, current_user.id, suggestion_data)
#         return suggestion
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @router.get("/suggestions", response_model=List[TopicSuggestionSchema])
# async def get_topic_suggestions(
#     status: Optional[str] = Query(None),
#     limit: int = Query(20, ge=1, le=100),
#     offset: int = Query(0, ge=0),
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Get topic suggestions"""
#     try:
#         query = db.query(TopicSuggestion)
#         
#         if status:
#             query = query.filter(TopicSuggestion.status == status)
#         
#         suggestions = query.order_by(desc(TopicSuggestion.created_at)).offset(offset).limit(limit).all()
#         
#         # Add user information
#         for suggestion in suggestions:
#             user = db.query(User).filter(User.id == suggestion.user_id).first()
#             if user:
#                 suggestion.username = user.username
#         
#         return suggestions
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to load suggestions: {str(e)}")

# @router.post("/suggestions/{suggestion_id}/vote")
# async def vote_on_suggestion(
#     suggestion_id: int,
#     vote_type: str = Query(..., regex="^(upvote|downvote)$"),
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Vote on a topic suggestion"""
#     try:
#         suggestion = await ChatService.vote_on_suggestion(db, current_user.id, suggestion_id, vote_type)
#         return suggestion
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# Study Groups
@router.post("/study-groups", response_model=StudyGroupSchema)
async def create_study_group(
    group_data: StudyGroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a study group"""
    try:
        group = await ChatService.create_study_group(db, current_user.id, group_data)
        return group
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/study-groups", response_model=List[StudyGroupSchema])
async def get_study_groups(
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get study groups"""
    try:
        query = db.query(StudyGroup).filter(StudyGroup.is_public == True)
        
        if topic:
            query = query.filter(StudyGroup.topic.ilike(f"%{topic}%"))
        
        if difficulty:
            query = query.filter(StudyGroup.difficulty == difficulty)
        
        groups = query.order_by(desc(StudyGroup.created_at)).offset(offset).limit(limit).all()
        
        # Add member count and creator info
        for group in groups:
            group.member_count = db.query(StudyGroupMember).filter(StudyGroupMember.group_id == group.id).count()
            creator = db.query(User).filter(User.id == group.created_by).first()
            if creator:
                group.creator_username = creator.username
        
        return groups
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load study groups: {str(e)}")

@router.post("/study-groups/{group_id}/join")
async def join_study_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a study group"""
    try:
        member = await ChatService.join_study_group(db, current_user.id, group_id)
        return {"message": "Successfully joined study group", "member": member}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Notifications
@router.get("/notifications", response_model=List[ChatNotificationSchema])
async def get_notifications(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notifications"""
    try:
        notifications = await ChatService.get_user_notifications(db, current_user.id, limit, offset)
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load notifications: {str(e)}")

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    try:
        await ChatService.mark_notification_read(db, notification_id, current_user.id)
        return {"message": "Notification marked as read"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Statistics
@router.get("/stats", response_model=ChatStats)
async def get_chat_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat statistics"""
    try:
        stats = await ChatService.get_chat_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load stats: {str(e)}")

@router.get("/rooms/{room_id}/stats", response_model=RoomStats)
async def get_room_stats(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics for a specific room"""
    try:
        stats = await ChatService.get_room_stats(db, room_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load room stats: {str(e)}") 