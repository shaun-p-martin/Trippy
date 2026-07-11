const API_BASE = "/api";

export type TripmateRole = "viewer" | "commenter" | "contributor" | "administrator";

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export type Traveler = {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  display_name: string | null;
  preferred_currency: string;
};

export type TripSummary = {
  id: string;
  name: string;
  description: string | null;
  start_date: string | null;
  end_date: string | null;
  is_archived: boolean;
  my_role: TripmateRole;
  created_at: string;
  updated_at: string;
};

export type TripDetail = TripSummary & {
  created_by_id: string;
};

export type TripStop = {
  id: string;
  trip_id: string;
  location_name: string;
  sort_order: number;
  earliest_arrival: string | null;
  latest_departure: string | null;
};

export type Tripmate = {
  id: string;
  trip_id: string;
  traveler_id: string | null;
  role: TripmateRole;
  invite_email: string | null;
  invite_status: "pending" | "accepted" | "revoked";
  joined_at: string | null;
  traveler_display: string | null;
};

export type IdeaType =
  | "dining"
  | "entertainment_dining"
  | "tour"
  | "guided_activity"
  | "unguided_activity"
  | "sightseeing_landmark"
  | "shopping"
  | "supplies_provisions"
  | "other";

export type Idea = {
  id: string;
  trip_id: string;
  name: string;
  description: string | null;
  location_text: string | null;
  apple_maps_url: string | null;
  google_maps_url: string | null;
  idea_types: IdeaType[];
  official_website: string | null;
  contact_phone: string | null;
  contact_email: string | null;
  created_by_id: string;
  created_by_display: string | null;
  reaction_count: number;
  comment_count: number;
  reacted_by_me: boolean;
  created_at: string;
  updated_at: string;
};

export type IdeaInput = {
  name: string;
  description?: string;
  location_text?: string;
  apple_maps_url?: string;
  google_maps_url?: string;
  idea_types?: IdeaType[];
  official_website?: string;
  contact_phone?: string;
  contact_email?: string;
};

export type Comment = {
  id: string;
  idea_id: string;
  parent_id: string | null;
  content: string;
  created_by_id: string;
  created_by_display: string | null;
  created_at: string;
  updated_at: string;
};

export type ReactionToggle = {
  idea_id: string;
  reaction_type: "like";
  reacted: boolean;
  reaction_count: number;
};

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("trippy_access_token");
}

export function setTokens(tokens: TokenResponse) {
  localStorage.setItem("trippy_access_token", tokens.access_token);
  localStorage.setItem("trippy_refresh_token", tokens.refresh_token);
}

export function clearTokens() {
  localStorage.removeItem("trippy_access_token");
  localStorage.removeItem("trippy_refresh_token");
}

export function isLoggedIn(): boolean {
  return Boolean(getAccessToken());
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (!headers.has("Content-Type") && init.body) {
    headers.set("Content-Type", "application/json");
  }
  const token = getAccessToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetch(`${API_BASE}${path}`, { ...init, headers });
  if (res.status === 204) {
    return undefined as T;
  }

  const text = await res.text();
  const data = text ? JSON.parse(text) : null;

  if (!res.ok) {
    const detail =
      typeof data?.detail === "string"
        ? data.detail
        : Array.isArray(data?.detail)
          ? data.detail.map((d: { msg?: string }) => d.msg).join(", ")
          : res.statusText;
    throw new ApiError(res.status, detail || "Request failed");
  }

  return data as T;
}

export const api = {
  register: (body: {
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
    display_name?: string;
  }) =>
    request<TokenResponse>("/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  login: (body: { email: string; password: string }) =>
    request<TokenResponse>("/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  me: () => request<Traveler>("/v1/travelers/me"),

  listTrips: () => request<TripSummary[]>("/v1/trips"),

  createTrip: (body: {
    name: string;
    description?: string;
    start_date?: string;
    end_date?: string;
  }) =>
    request<TripDetail>("/v1/trips", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  getTrip: (id: string) => request<TripDetail>(`/v1/trips/${id}`),

  listStops: (tripId: string) => request<TripStop[]>(`/v1/trips/${tripId}/stops`),

  createStop: (tripId: string, body: { location_name: string; sort_order?: number }) =>
    request<TripStop>(`/v1/trips/${tripId}/stops`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  listTripmates: (tripId: string) => request<Tripmate[]>(`/v1/trips/${tripId}/tripmates`),

  inviteTripmate: (tripId: string, body: { email: string; role: TripmateRole }) =>
    request<{ tripmate: Tripmate; invite_token: string }>(
      `/v1/trips/${tripId}/tripmates/invite`,
      {
        method: "POST",
        body: JSON.stringify(body),
      },
    ),

  acceptInvite: (token: string) =>
    request<Tripmate>(`/v1/invites/${token}/accept`, { method: "POST" }),

  listIdeas: (tripId: string, ideaType?: IdeaType) => {
    const q = ideaType ? `?idea_type=${ideaType}` : "";
    return request<Idea[]>(`/v1/trips/${tripId}/ideas${q}`);
  },

  createIdea: (tripId: string, body: IdeaInput) =>
    request<Idea>(`/v1/trips/${tripId}/ideas`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  updateIdea: (tripId: string, ideaId: string, body: Partial<IdeaInput>) =>
    request<Idea>(`/v1/trips/${tripId}/ideas/${ideaId}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  deleteIdea: (tripId: string, ideaId: string) =>
    request<void>(`/v1/trips/${tripId}/ideas/${ideaId}`, { method: "DELETE" }),

  listIdeaComments: (tripId: string, ideaId: string) =>
    request<Comment[]>(`/v1/trips/${tripId}/ideas/${ideaId}/comments`),

  createIdeaComment: (
    tripId: string,
    ideaId: string,
    body: { content: string; parent_id?: string },
  ) =>
    request<Comment>(`/v1/trips/${tripId}/ideas/${ideaId}/comments`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  deleteIdeaComment: (tripId: string, ideaId: string, commentId: string) =>
    request<void>(`/v1/trips/${tripId}/ideas/${ideaId}/comments/${commentId}`, {
      method: "DELETE",
    }),

  toggleIdeaReaction: (tripId: string, ideaId: string) =>
    request<ReactionToggle>(`/v1/trips/${tripId}/ideas/${ideaId}/reactions`, {
      method: "POST",
    }),
};
