export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
}

export interface QuizConfig {
  topic: string;
  difficulty: string;
  num_questions: number;
  time_limit: number;
}

export interface Question {
  question: string;
  options: string[];
  correct_answer: string;
  explanation: string;
}

export interface QuizResponse {
  quiz: Question[];
}

export interface Quiz {
  id: number;
  user_id: number;
  topic: string;
  difficulty: string;
  num_questions: number;
  time_limit: number;
  score?: number;
  accuracy?: number;
  completed_at?: string;
  created_at: string;
}

export interface UserAnswer {
  question_id: number;
  selected_answer: string;
  time_taken?: number;
}

export interface QuizResult {
  quiz_id: number;
  score: number;
  accuracy: number;
  total_questions: number;
  correct_answers: number;
  time_taken: number;
  completed_at: string;
}

export interface ChatMessage {
  id?: number;
  message: string;
  context?: string;
  isUser?: boolean;
  timestamp?: Date;
}

export interface UserStats {
  total_quizzes: number;
  total_questions: number;
  total_answers: number;
  correct_answers: number;
  overall_accuracy: number;
  average_score: number;
}

export interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
} 