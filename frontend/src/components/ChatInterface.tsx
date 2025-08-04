import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { chatAPI } from '../services/api';
import Header from './Header';

interface ChatRoom {
  id: number;
  name: string;
  description?: string;
  room_type: string;
  topic?: string;
  participant_count: number;
  created_at: string;
}

interface ChatMessage {
  id: number;
  room_id: number;
  user_id: number;
  content: string;
  message_type: string;
  metadata: any;
  username: string;
  created_at: string;
  is_edited: boolean;
  reply_to_message?: ChatMessage;
}

interface TopicSuggestion {
  id: number;
  topic: string;
  description?: string;
  difficulty?: string;
  category?: string;
  upvotes: number;
  downvotes: number;
  status: string;
  username: string;
  created_at: string;
}

interface StudyGroup {
  id: number;
  name: string;
  description?: string;
  topic: string;
  difficulty: string;
  max_members: number;
  is_public: boolean;
  member_count: number;
  creator_username: string;
  created_at: string;
}

const ChatInterface: React.FC = () => {
  const { user } = useAuth();
  const [rooms, setRooms] = useState<ChatRoom[]>([]);
  const [selectedRoom, setSelectedRoom] = useState<ChatRoom | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [activeTab, setActiveTab] = useState('chat');
  const [suggestions, setSuggestions] = useState<TopicSuggestion[]>([]);
  const [studyGroups, setStudyGroups] = useState<StudyGroup[]>([]);
  const [showCreateRoom, setShowCreateRoom] = useState(false);
  const [showCreateSuggestion, setShowCreateSuggestion] = useState(false);
  const [showCreateGroup, setShowCreateGroup] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [typingUsers, setTypingUsers] = useState<string[]>([]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    loadRooms();
    loadSuggestions();
    loadStudyGroups();
  }, []);

  useEffect(() => {
    if (selectedRoom) {
      loadMessages();
      connectWebSocket();
    }
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [selectedRoom]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadRooms = async () => {
    try {
      setLoading(true);
      const response = await chatAPI.getUserRooms();
      setRooms(response.data);
      
      // Auto-select first room if none selected
      if (response.data.length > 0 && !selectedRoom) {
        setSelectedRoom(response.data[0]);
      }
    } catch (err: any) {
      setError('Failed to load chat rooms');
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async () => {
    if (!selectedRoom) return;
    
    try {
      const response = await chatAPI.getRoomMessages(selectedRoom.id);
      setMessages(response.data.reverse()); // Reverse to show newest first
    } catch (err: any) {
      setError('Failed to load messages');
    }
  };

  const loadSuggestions = async () => {
    try {
      const response = await chatAPI.getTopicSuggestions();
      setSuggestions(response.data);
    } catch (err: any) {
      console.error('Failed to load suggestions:', err);
    }
  };

  const loadStudyGroups = async () => {
    try {
      const response = await chatAPI.getStudyGroups();
      setStudyGroups(response.data);
    } catch (err: any) {
      console.error('Failed to load study groups:', err);
    }
  };

  const connectWebSocket = () => {
    if (!selectedRoom || !user) return;

    const ws = new WebSocket(`ws://localhost:8000/api/chat/ws/room/${selectedRoom.id}/${user.id}`);
    
    ws.onopen = () => {
      console.log('Connected to chat room');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'message') {
        setMessages(prev => [...prev, data.message]);
      } else if (data.type === 'typing') {
        if (data.is_typing) {
          setTypingUsers(prev => Array.from(new Set([...prev, data.username])));
        } else {
          setTypingUsers(prev => prev.filter(u => u !== data.username));
        }
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
      console.log('Disconnected from chat room');
    };
    
    wsRef.current = ws;
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedRoom) return;

    try {
      const messageData = {
        room_id: selectedRoom.id,
        content: newMessage,
        message_type: 'text'
      };
      
      const response = await chatAPI.sendMessage(messageData);
      setNewMessage('');
      
      // Add message to local state
      setMessages(prev => [...prev, response.data]);
      
      // Send typing indicator
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'typing',
          room_id: selectedRoom.id,
          user_id: user?.id,
          username: user?.username,
          is_typing: false
        }));
      }
    } catch (err: any) {
      setError('Failed to send message');
    }
  };

  const handleTyping = () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    
    if (!isTyping) {
      setIsTyping(true);
      wsRef.current.send(JSON.stringify({
        type: 'typing',
        room_id: selectedRoom?.id,
        user_id: user?.id,
        username: user?.username,
        is_typing: true
      }));
      
      // Stop typing indicator after 3 seconds
      setTimeout(() => {
        setIsTyping(false);
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({
            type: 'typing',
            room_id: selectedRoom?.id,
            user_id: user?.id,
            username: user?.username,
            is_typing: false
          }));
        }
      }, 3000);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const shareTopic = async (topic: string, difficulty: string) => {
    if (!selectedRoom) return;

    try {
      const messageData = {
        room_id: selectedRoom.id,
        content: `Shared topic: ${topic}`,
        message_type: 'topic_share',
        metadata: { topic, difficulty }
      };
      
      await chatAPI.sendMessage(messageData);
    } catch (err: any) {
      setError('Failed to share topic');
    }
  };

  const shareQuizResult = async (quizData: any) => {
    if (!selectedRoom) return;

    try {
      const messageData = {
        room_id: selectedRoom.id,
        content: `Just completed a quiz on ${quizData.topic} with ${quizData.score}% score!`,
        message_type: 'result_share',
        metadata: quizData
      };
      
      await chatAPI.sendMessage(messageData);
    } catch (err: any) {
      setError('Failed to share quiz result');
    }
  };

  const voteOnSuggestion = async (suggestionId: number, voteType: 'upvote' | 'downvote') => {
    try {
      await chatAPI.voteOnSuggestion(suggestionId, voteType);
      loadSuggestions(); // Reload to get updated votes
    } catch (err: any) {
      setError('Failed to vote on suggestion');
    }
  };

  const joinStudyGroup = async (groupId: number) => {
    try {
      await chatAPI.joinStudyGroup(groupId);
      loadStudyGroups(); // Reload to get updated member count
    } catch (err: any) {
      setError('Failed to join study group');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8 animate-fade-in">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">
            Community Chat
          </h1>
          <p className="text-xl text-slate-600">
            Connect with other learners, share topics, and collaborate on your learning journey
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-8">
          <nav className="flex space-x-1 bg-white rounded-xl p-1 shadow-sm">
            {[
              { id: 'chat', label: 'Chat', icon: '💬' },
              { id: 'suggestions', label: 'Topic Suggestions', icon: '💡' },
              { id: 'groups', label: 'Study Groups', icon: '👥' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-blue-100 text-blue-700 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {error && (
          <div className="card mb-8 bg-red-50 border-red-200">
            <div className="flex items-center space-x-2 text-red-700">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="font-medium">{error}</span>
            </div>
          </div>
        )}

        {/* Content */}
        <div className="animate-slide-up">
          {activeTab === 'chat' && (
            <ChatTab
              rooms={rooms}
              selectedRoom={selectedRoom}
              setSelectedRoom={setSelectedRoom}
              messages={messages}
              newMessage={newMessage}
              setNewMessage={setNewMessage}
              sendMessage={sendMessage}
              handleTyping={handleTyping}
              typingUsers={typingUsers}
              messagesEndRef={messagesEndRef}
              formatTime={formatTime}
              shareTopic={shareTopic}
              shareQuizResult={shareQuizResult}
              loading={loading}
            />
          )}
          
          {activeTab === 'suggestions' && (
            <SuggestionsTab
              suggestions={suggestions}
              voteOnSuggestion={voteOnSuggestion}
              showCreateSuggestion={showCreateSuggestion}
              setShowCreateSuggestion={setShowCreateSuggestion}
            />
          )}
          
          {activeTab === 'groups' && (
            <StudyGroupsTab
              studyGroups={studyGroups}
              joinStudyGroup={joinStudyGroup}
              showCreateGroup={showCreateGroup}
              setShowCreateGroup={setShowCreateGroup}
            />
          )}
        </div>
      </div>
    </div>
  );
};

// Chat Tab Component
const ChatTab: React.FC<{
  rooms: ChatRoom[];
  selectedRoom: ChatRoom | null;
  setSelectedRoom: (room: ChatRoom) => void;
  messages: ChatMessage[];
  newMessage: string;
  setNewMessage: (message: string) => void;
  sendMessage: () => void;
  handleTyping: () => void;
  typingUsers: string[];
  messagesEndRef: React.RefObject<HTMLDivElement>;
  formatTime: (dateString: string) => string;
  shareTopic: (topic: string, difficulty: string) => void;
  shareQuizResult: (quizData: any) => void;
  loading: boolean;
}> = ({
  rooms, selectedRoom, setSelectedRoom, messages, newMessage, setNewMessage,
  sendMessage, handleTyping, typingUsers, messagesEndRef, formatTime,
  shareTopic, shareQuizResult, loading
}) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Room List */}
      <div className="lg:col-span-1">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-slate-900">Chat Rooms</h3>
            <button className="btn-primary text-sm px-3 py-1">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              New
            </button>
          </div>
          
          <div className="space-y-2">
            {rooms.map((room) => (
              <button
                key={room.id}
                onClick={() => setSelectedRoom(room)}
                className={`w-full text-left p-3 rounded-lg transition-all duration-200 ${
                  selectedRoom?.id === room.id
                    ? 'bg-blue-100 border-blue-300'
                    : 'hover:bg-slate-50 border-transparent'
                } border`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-slate-900">{room.name}</h4>
                    <p className="text-sm text-slate-600">{room.topic || room.description}</p>
                  </div>
                  <div className="text-xs text-slate-500">
                    {room.participant_count} online
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="lg:col-span-3">
        {selectedRoom ? (
          <div className="card h-[600px] flex flex-col">
            {/* Room Header */}
            <div className="border-b border-slate-200 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold text-slate-900">{selectedRoom.name}</h3>
                  <p className="text-sm text-slate-600">{selectedRoom.participant_count} participants</p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => shareTopic('Python Basics', 'Easy')}
                    className="btn-secondary text-sm px-3 py-1"
                  >
                    Share Topic
                  </button>
                  <button
                    onClick={() => shareQuizResult({ topic: 'JavaScript', score: 85 })}
                    className="btn-secondary text-sm px-3 py-1"
                  >
                    Share Result
                  </button>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
              {messages.map((message) => (
                <div key={message.id} className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-white font-semibold text-sm">
                      {message.username.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="font-medium text-slate-900">{message.username}</span>
                      <span className="text-xs text-slate-500">{formatTime(message.created_at)}</span>
                      {message.is_edited && (
                        <span className="text-xs text-slate-400">(edited)</span>
                      )}
                    </div>
                    <div className="bg-white border border-slate-200 rounded-lg p-3">
                      {message.message_type === 'topic_share' ? (
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                          <div className="flex items-center space-x-2 text-blue-700 mb-2">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                            <span className="font-medium">Shared Topic</span>
                          </div>
                          <p className="text-blue-800">{message.content}</p>
                          {message.metadata && (
                            <div className="mt-2 text-sm text-blue-600">
                              Difficulty: {message.metadata.difficulty}
                            </div>
                          )}
                        </div>
                      ) : message.message_type === 'result_share' ? (
                        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                          <div className="flex items-center space-x-2 text-green-700 mb-2">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span className="font-medium">Quiz Result</span>
                          </div>
                          <p className="text-green-800">{message.content}</p>
                        </div>
                      ) : (
                        <p className="text-slate-900">{message.content}</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {typingUsers.length > 0 && (
                <div className="flex items-center space-x-2 text-sm text-slate-500">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span>{typingUsers.join(', ')} {typingUsers.length === 1 ? 'is' : 'are'} typing...</span>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <div className="border-t border-slate-200 p-4">
              <div className="flex space-x-3">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      sendMessage();
                    } else {
                      handleTyping();
                    }
                  }}
                  placeholder="Type your message..."
                  className="flex-1 input-field"
                />
                <button
                  onClick={sendMessage}
                  disabled={!newMessage.trim()}
                  className="btn-primary px-6 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Send
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="card h-[600px] flex items-center justify-center">
            <div className="text-center">
              <svg className="w-16 h-16 text-slate-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <h3 className="text-lg font-medium text-slate-900 mb-2">Select a Chat Room</h3>
              <p className="text-slate-600">Choose a room to start chatting with other learners</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Suggestions Tab Component
const SuggestionsTab: React.FC<{
  suggestions: TopicSuggestion[];
  voteOnSuggestion: (id: number, voteType: 'upvote' | 'downvote') => void;
  showCreateSuggestion: boolean;
  setShowCreateSuggestion: (show: boolean) => void;
}> = ({ suggestions, voteOnSuggestion, showCreateSuggestion, setShowCreateSuggestion }) => {
  const [newSuggestion, setNewSuggestion] = useState({
    topic: '',
    description: '',
    difficulty: 'Medium',
    category: ''
  });

  const createSuggestion = async () => {
    try {
      await chatAPI.createTopicSuggestion(newSuggestion);
      setNewSuggestion({ topic: '', description: '', difficulty: 'Medium', category: '' });
      setShowCreateSuggestion(false);
      // Reload suggestions
    } catch (err: any) {
      console.error('Failed to create suggestion:', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-slate-900">Topic Suggestions</h2>
        <button
          onClick={() => setShowCreateSuggestion(true)}
          className="btn-primary"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Suggest Topic
        </button>
      </div>

      {showCreateSuggestion && (
        <div className="card">
          <h3 className="text-lg font-bold text-slate-900 mb-4">Create Topic Suggestion</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Topic</label>
              <input
                type="text"
                value={newSuggestion.topic}
                onChange={(e) => setNewSuggestion({ ...newSuggestion, topic: e.target.value })}
                className="input-field"
                placeholder="Enter topic name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Description</label>
              <textarea
                value={newSuggestion.description}
                onChange={(e) => setNewSuggestion({ ...newSuggestion, description: e.target.value })}
                className="input-field"
                rows={3}
                placeholder="Describe the topic"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Difficulty</label>
                <select
                  value={newSuggestion.difficulty}
                  onChange={(e) => setNewSuggestion({ ...newSuggestion, difficulty: e.target.value })}
                  className="input-field"
                >
                  <option value="Easy">Easy</option>
                  <option value="Medium">Medium</option>
                  <option value="Hard">Hard</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Category</label>
                <input
                  type="text"
                  value={newSuggestion.category}
                  onChange={(e) => setNewSuggestion({ ...newSuggestion, category: e.target.value })}
                  className="input-field"
                  placeholder="e.g., Programming, Math"
                />
              </div>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={createSuggestion}
                disabled={!newSuggestion.topic.trim()}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Submit Suggestion
              </button>
              <button
                onClick={() => setShowCreateSuggestion(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="grid gap-4">
        {suggestions.map((suggestion) => (
          <div key={suggestion.id} className="card">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <h3 className="font-semibold text-slate-900">{suggestion.topic}</h3>
                  <span className={`badge ${
                    suggestion.difficulty === 'Easy' ? 'badge-success' :
                    suggestion.difficulty === 'Medium' ? 'badge-warning' : 'badge-error'
                  }`}>
                    {suggestion.difficulty}
                  </span>
                  {suggestion.category && (
                    <span className="badge badge-secondary">{suggestion.category}</span>
                  )}
                </div>
                {suggestion.description && (
                  <p className="text-slate-600 mb-3">{suggestion.description}</p>
                )}
                <div className="flex items-center space-x-4 text-sm text-slate-500">
                  <span>Suggested by {suggestion.username}</span>
                  <span>{new Date(suggestion.created_at).toLocaleDateString()}</span>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => voteOnSuggestion(suggestion.id, 'upvote')}
                  className="flex items-center space-x-1 text-green-600 hover:text-green-700"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                  </svg>
                  <span>{suggestion.upvotes}</span>
                </button>
                <button
                  onClick={() => voteOnSuggestion(suggestion.id, 'downvote')}
                  className="flex items-center space-x-1 text-red-600 hover:text-red-700"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                  <span>{suggestion.downvotes}</span>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Study Groups Tab Component
const StudyGroupsTab: React.FC<{
  studyGroups: StudyGroup[];
  joinStudyGroup: (id: number) => void;
  showCreateGroup: boolean;
  setShowCreateGroup: (show: boolean) => void;
}> = ({ studyGroups, joinStudyGroup, showCreateGroup, setShowCreateGroup }) => {
  const [newGroup, setNewGroup] = useState({
    name: '',
    description: '',
    topic: '',
    difficulty: 'Medium',
    max_members: 20,
    is_public: true
  });

  const createGroup = async () => {
    try {
      await chatAPI.createStudyGroup(newGroup);
      setNewGroup({ name: '', description: '', topic: '', difficulty: 'Medium', max_members: 20, is_public: true });
      setShowCreateGroup(false);
      // Reload groups
    } catch (err: any) {
      console.error('Failed to create group:', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-slate-900">Study Groups</h2>
        <button
          onClick={() => setShowCreateGroup(true)}
          className="btn-primary"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Create Group
        </button>
      </div>

      {showCreateGroup && (
        <div className="card">
          <h3 className="text-lg font-bold text-slate-900 mb-4">Create Study Group</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Group Name</label>
              <input
                type="text"
                value={newGroup.name}
                onChange={(e) => setNewGroup({ ...newGroup, name: e.target.value })}
                className="input-field"
                placeholder="Enter group name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Description</label>
              <textarea
                value={newGroup.description}
                onChange={(e) => setNewGroup({ ...newGroup, description: e.target.value })}
                className="input-field"
                rows={3}
                placeholder="Describe the study group"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Topic</label>
                <input
                  type="text"
                  value={newGroup.topic}
                  onChange={(e) => setNewGroup({ ...newGroup, topic: e.target.value })}
                  className="input-field"
                  placeholder="Study topic"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Difficulty</label>
                <select
                  value={newGroup.difficulty}
                  onChange={(e) => setNewGroup({ ...newGroup, difficulty: e.target.value })}
                  className="input-field"
                >
                  <option value="Easy">Easy</option>
                  <option value="Medium">Medium</option>
                  <option value="Hard">Hard</option>
                </select>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={createGroup}
                disabled={!newGroup.name.trim() || !newGroup.topic.trim()}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Create Group
              </button>
              <button
                onClick={() => setShowCreateGroup(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="grid gap-4">
        {studyGroups.map((group) => (
          <div key={group.id} className="card">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <h3 className="font-semibold text-slate-900">{group.name}</h3>
                  <span className={`badge ${
                    group.difficulty === 'Easy' ? 'badge-success' :
                    group.difficulty === 'Medium' ? 'badge-warning' : 'badge-error'
                  }`}>
                    {group.difficulty}
                  </span>
                  {!group.is_public && (
                    <span className="badge badge-secondary">Private</span>
                  )}
                </div>
                {group.description && (
                  <p className="text-slate-600 mb-3">{group.description}</p>
                )}
                <div className="flex items-center space-x-4 text-sm text-slate-500">
                  <span>Topic: {group.topic}</span>
                  <span>{group.member_count}/{group.max_members} members</span>
                  <span>Created by {group.creator_username}</span>
                </div>
              </div>
              <button
                onClick={() => joinStudyGroup(group.id)}
                className="btn-secondary"
              >
                Join Group
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChatInterface; 