export type User = {
  id: number;
  email: string;
  full_name: string;
  role: string;
};

export type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
};

export type AuthResponse = {
  user: User;
  tokens: TokenPair;
};

export type SalaryPredictionRequest = {
  years_experience: number;
  degree_level: string;
  location: string;
  industry: string;
  company_size: string;
  title: string;
  skills: string[];
  resume_id?: number | null;
};

export type FeatureContribution = {
  feature: string;
  value: number;
  contribution: number;
};

export type Explanation = {
  base_value: number;
  predicted_value: number;
  features: FeatureContribution[];
  waterfall: FeatureContribution[];
};

export type SalaryPredictionResponse = {
  prediction_id: number;
  predicted_salary: number;
  currency: string;
  lower_bound: number | null;
  upper_bound: number | null;
  confidence: number | null;
  model_name: string;
  model_version: string;
  explanation: Explanation | null;
  input_features: Record<string, unknown>;
  created_at: string;
};

export type ParsedResumeData = {
  name?: string | null;
  email?: string | null;
  phone?: string | null;
  summary?: string | null;
  experience?: { [key: string]: unknown }[];
  education?: { [key: string]: unknown }[];
  projects?: string[];
  certifications?: string[];
  technologies?: string[];
  languages?: string[];
  skills?: string[];
  years_of_experience?: number;
};

export type Resume = {
  id: number;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  parse_status: string;
  error_message: string | null;
  parsed_data: ParsedResumeData | Record<string, never>;
  created_at: string;
};

export type ResumeUploadResponse = {
  resume: Resume;
  skills: string[];
};

export type ResumeListItem = {
  id: number;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  parse_status: string;
  created_at: string;
};

export type Page<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
};

export type MissingSkill = {
  skill: string;
  category: string;
  priority_score: number;
  importance: string;
};

export type SkillGapResponse = {
  skill_match_percentage: number;
  matched_skills: string[];
  missing_skills: MissingSkill[];
  recommendation_priority: string;
};

export type LearningResource = {
  id: number;
  skill_name: string;
  title: string;
  provider: string;
  url: string;
  resource_type: string;
  difficulty: string;
  estimated_hours: number;
  rating: number | null;
};

export type RoadmapStep = {
  skill: string;
  priority: number;
  estimated_hours: number;
  resources: LearningResource[];
};

export type LearningRoadmapResponse = {
  total_estimated_hours: number;
  estimated_weeks: number;
  steps: RoadmapStep[];
};

export type SkillOut = {
  id: number;
  name: string;
  category: string;
  weight: number;
};

export type Job = {
  id: number;
  title: string;
  company: string;
  location: string;
  salary_min: number | null;
  salary_max: number | null;
  currency: string;
  source_url: string;
  created_at: string;
};

export type JobMatchResult = {
  job: Job;
  similarity: number;
  matched_skills: string[];
  missing_skills: string[];
};

export type JobMatchResponse = {
  query: string;
  top_k: number;
  results: JobMatchResult[];
};

export type AnalyticsResponse = {
  total_predictions: number;
  average_salary: number;
  salary_trend: { date: string; value: number }[];
  salary_by_location: { label: string; average_salary: number; count: number }[];
  salary_by_industry: { label: string; average_salary: number; count: number }[];
  salary_by_experience: { date: string; value: number }[];
  top_skills: { skill: string; count: number }[];
  most_missing_skills: { skill: string; count: number }[];
};

export type PredictionHistoryItem = {
  id: number;
  predicted_salary: number;
  lower_bound: number | null;
  upper_bound: number | null;
  model_name: string;
  created_at: string;
};
