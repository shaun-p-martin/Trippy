"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import {
  ApiError,
  Comment,
  Idea,
  IdeaType,
  TripmateRole,
  api,
} from "@/lib/api";

const IDEA_TYPE_OPTIONS: { value: IdeaType; label: string }[] = [
  { value: "dining", label: "Dining" },
  { value: "entertainment_dining", label: "Entertainment & Dining" },
  { value: "tour", label: "Tour" },
  { value: "guided_activity", label: "Guided Activity" },
  { value: "unguided_activity", label: "Unguided Activity" },
  { value: "sightseeing_landmark", label: "Sightseeing / Landmark" },
  { value: "shopping", label: "Shopping" },
  { value: "supplies_provisions", label: "Supplies & Provisions" },
  { value: "other", label: "Other" },
];

function typeLabel(t: IdeaType): string {
  return IDEA_TYPE_OPTIONS.find((o) => o.value === t)?.label ?? t;
}

const ROLE_RANK: Record<TripmateRole, number> = {
  viewer: 1,
  commenter: 2,
  contributor: 3,
  administrator: 4,
};

type Props = {
  tripId: string;
  myRole: TripmateRole;
  myTravelerId: string;
};

export function IdeasPanel({ tripId, myRole, myTravelerId }: Props) {
  const [ideas, setIdeas] = useState<Idea[]>([]);
  const [filter, setFilter] = useState<IdeaType | "">("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [commentText, setCommentText] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Idea | null>(null);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [locationText, setLocationText] = useState("");
  const [googleMapsUrl, setGoogleMapsUrl] = useState("");
  const [appleMapsUrl, setAppleMapsUrl] = useState("");
  const [website, setWebsite] = useState("");
  const [selectedTypes, setSelectedTypes] = useState<IdeaType[]>([]);

  const canContribute = ROLE_RANK[myRole] >= ROLE_RANK.contributor;
  const canComment = ROLE_RANK[myRole] >= ROLE_RANK.commenter;

  const loadIdeas = useCallback(async () => {
    const list = await api.listIdeas(tripId, filter || undefined);
    setIdeas(list);
  }, [tripId, filter]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        await loadIdeas();
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.detail : "Failed to load ideas");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [loadIdeas]);

  const selected = useMemo(
    () => ideas.find((i) => i.id === selectedId) ?? null,
    [ideas, selectedId],
  );

  useEffect(() => {
    if (!selectedId) {
      setComments([]);
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const list = await api.listIdeaComments(tripId, selectedId);
        if (!cancelled) setComments(list);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.detail : "Failed to load comments");
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [tripId, selectedId]);

  function resetForm() {
    setName("");
    setDescription("");
    setLocationText("");
    setGoogleMapsUrl("");
    setAppleMapsUrl("");
    setWebsite("");
    setSelectedTypes([]);
    setEditing(null);
    setShowForm(false);
  }

  function startEdit(idea: Idea) {
    setEditing(idea);
    setName(idea.name);
    setDescription(idea.description || "");
    setLocationText(idea.location_text || "");
    setGoogleMapsUrl(idea.google_maps_url || "");
    setAppleMapsUrl(idea.apple_maps_url || "");
    setWebsite(idea.official_website || "");
    setSelectedTypes(idea.idea_types);
    setShowForm(true);
  }

  function toggleType(t: IdeaType) {
    setSelectedTypes((prev) =>
      prev.includes(t) ? prev.filter((x) => x !== t) : [...prev, t],
    );
  }

  function canEditIdea(idea: Idea): boolean {
    if (myRole === "administrator") return true;
    return canContribute && idea.created_by_id === myTravelerId;
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setError(null);
    const body = {
      name: name.trim(),
      description: description.trim() || undefined,
      location_text: locationText.trim() || undefined,
      google_maps_url: googleMapsUrl.trim() || undefined,
      apple_maps_url: appleMapsUrl.trim() || undefined,
      official_website: website.trim() || undefined,
      idea_types: selectedTypes,
    };
    try {
      if (editing) {
        await api.updateIdea(tripId, editing.id, body);
      } else {
        await api.createIdea(tripId, body);
      }
      resetForm();
      await loadIdeas();
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Could not save idea");
    }
  }

  async function onDelete(idea: Idea) {
    if (!confirm(`Delete “${idea.name}”?`)) return;
    setError(null);
    try {
      await api.deleteIdea(tripId, idea.id);
      if (selectedId === idea.id) setSelectedId(null);
      await loadIdeas();
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Could not delete idea");
    }
  }

  async function onToggleLike(idea: Idea) {
    setError(null);
    try {
      const res = await api.toggleIdeaReaction(tripId, idea.id);
      setIdeas((prev) =>
        prev.map((i) =>
          i.id === idea.id
            ? { ...i, reacted_by_me: res.reacted, reaction_count: res.reaction_count }
            : i,
        ),
      );
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Could not update reaction");
    }
  }

  async function onComment(e: FormEvent) {
    e.preventDefault();
    if (!selectedId || !commentText.trim()) return;
    setError(null);
    try {
      const c = await api.createIdeaComment(tripId, selectedId, {
        content: commentText.trim(),
      });
      setComments((prev) => [...prev, c]);
      setCommentText("");
      setIdeas((prev) =>
        prev.map((i) =>
          i.id === selectedId ? { ...i, comment_count: i.comment_count + 1 } : i,
        ),
      );
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Could not post comment");
    }
  }

  async function onDeleteComment(comment: Comment) {
    if (!selectedId) return;
    setError(null);
    try {
      await api.deleteIdeaComment(tripId, selectedId, comment.id);
      setComments((prev) => prev.filter((c) => c.id !== comment.id));
      setIdeas((prev) =>
        prev.map((i) =>
          i.id === selectedId
            ? { ...i, comment_count: Math.max(0, i.comment_count - 1) }
            : i,
        ),
      );
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Could not delete comment");
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="font-medium text-slate-900">Ideas</h2>
          <p className="text-sm text-slate-500">
            Shared backlog of places and activities for this trip.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as IdeaType | "")}
            className="rounded-md border border-slate-300 px-2 py-1.5 text-sm"
          >
            <option value="">All types</option>
            {IDEA_TYPE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
          {canContribute ? (
            <button
              type="button"
              onClick={() => {
                if (showForm && !editing) resetForm();
                else {
                  setEditing(null);
                  setShowForm(true);
                }
              }}
              className="rounded-md bg-teal-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-teal-800"
            >
              {showForm && !editing ? "Cancel" : "Add idea"}
            </button>
          ) : null}
        </div>
      </div>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      {showForm && canContribute ? (
        <form
          onSubmit={onSubmit}
          className="space-y-3 rounded-lg border border-slate-200 bg-slate-50 p-4"
        >
          <h3 className="text-sm font-medium text-slate-800">
            {editing ? "Edit idea" : "New idea"}
          </h3>
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Name"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-teal-600"
          />
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Description (optional)"
            rows={3}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-teal-600"
          />
          <input
            value={locationText}
            onChange={(e) => setLocationText(e.target.value)}
            placeholder="Location / address"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-teal-600"
          />
          <div className="grid gap-2 sm:grid-cols-2">
            <input
              value={googleMapsUrl}
              onChange={(e) => setGoogleMapsUrl(e.target.value)}
              placeholder="Google Maps URL"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-teal-600"
            />
            <input
              value={appleMapsUrl}
              onChange={(e) => setAppleMapsUrl(e.target.value)}
              placeholder="Apple Maps URL"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-teal-600"
            />
          </div>
          <input
            value={website}
            onChange={(e) => setWebsite(e.target.value)}
            placeholder="Official website"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-teal-600"
          />
          <div>
            <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
              Types
            </p>
            <div className="flex flex-wrap gap-2">
              {IDEA_TYPE_OPTIONS.map((o) => {
                const on = selectedTypes.includes(o.value);
                return (
                  <button
                    key={o.value}
                    type="button"
                    onClick={() => toggleType(o.value)}
                    className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                      on
                        ? "bg-teal-700 text-white"
                        : "bg-white text-slate-600 ring-1 ring-slate-200"
                    }`}
                  >
                    {o.label}
                  </button>
                );
              })}
            </div>
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              className="rounded-md bg-teal-700 px-3 py-2 text-sm font-medium text-white hover:bg-teal-800"
            >
              {editing ? "Save changes" : "Create idea"}
            </button>
            <button
              type="button"
              onClick={resetForm}
              className="rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-600 hover:bg-white"
            >
              Cancel
            </button>
          </div>
        </form>
      ) : null}

      {loading ? (
        <p className="text-sm text-slate-500">Loading ideas…</p>
      ) : ideas.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500">
          No ideas yet{filter ? " for this type" : ""}.
          {canContribute ? " Add the first one above." : ""}
        </div>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          <ul className="grid gap-3 sm:grid-cols-1">
            {ideas.map((idea) => (
              <li key={idea.id}>
                <article
                  className={`rounded-xl border bg-white p-4 shadow-sm transition ${
                    selectedId === idea.id
                      ? "border-teal-400 ring-1 ring-teal-200"
                      : "border-slate-200 hover:border-teal-200"
                  }`}
                >
                  <button
                    type="button"
                    onClick={() => setSelectedId(idea.id === selectedId ? null : idea.id)}
                    className="w-full text-left"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="font-medium text-slate-900">{idea.name}</h3>
                      <span className="shrink-0 text-xs text-slate-400">
                        {idea.reaction_count}♥ · {idea.comment_count}💬
                      </span>
                    </div>
                    {idea.description ? (
                      <p className="mt-1 line-clamp-2 text-sm text-slate-500">{idea.description}</p>
                    ) : null}
                    {idea.location_text ? (
                      <p className="mt-2 text-xs text-slate-400">{idea.location_text}</p>
                    ) : null}
                    {idea.idea_types.length > 0 ? (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {idea.idea_types.map((t) => (
                          <span
                            key={t}
                            className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] text-slate-600"
                          >
                            {typeLabel(t)}
                          </span>
                        ))}
                      </div>
                    ) : null}
                    <p className="mt-2 text-xs text-slate-400">
                      by {idea.created_by_display || "Someone"}
                    </p>
                  </button>
                  <div className="mt-3 flex flex-wrap gap-2 border-t border-slate-100 pt-3">
                    {canComment ? (
                      <button
                        type="button"
                        onClick={() => onToggleLike(idea)}
                        className={`rounded-md px-2.5 py-1 text-xs font-medium ${
                          idea.reacted_by_me
                            ? "bg-rose-50 text-rose-700 ring-1 ring-rose-200"
                            : "bg-slate-50 text-slate-600 ring-1 ring-slate-200"
                        }`}
                      >
                        {idea.reacted_by_me ? "Liked" : "Like"} ({idea.reaction_count})
                      </button>
                    ) : null}
                    <button
                      type="button"
                      onClick={() => setSelectedId(idea.id)}
                      className="rounded-md bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-600 ring-1 ring-slate-200"
                    >
                      Comments
                    </button>
                    {canEditIdea(idea) ? (
                      <>
                        <button
                          type="button"
                          onClick={() => startEdit(idea)}
                          className="rounded-md bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-600 ring-1 ring-slate-200"
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          onClick={() => onDelete(idea)}
                          className="rounded-md bg-red-50 px-2.5 py-1 text-xs font-medium text-red-700 ring-1 ring-red-100"
                        >
                          Delete
                        </button>
                      </>
                    ) : null}
                  </div>
                </article>
              </li>
            ))}
          </ul>

          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            {selected ? (
              <div className="space-y-4">
                <div>
                  <h3 className="font-medium text-slate-900">{selected.name}</h3>
                  {selected.description ? (
                    <p className="mt-1 whitespace-pre-wrap text-sm text-slate-600">
                      {selected.description}
                    </p>
                  ) : null}
                  <div className="mt-3 space-y-1 text-xs text-slate-500">
                    {selected.location_text ? <p>📍 {selected.location_text}</p> : null}
                    {selected.google_maps_url ? (
                      <p>
                        <a
                          href={selected.google_maps_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-teal-700 hover:underline"
                        >
                          Google Maps
                        </a>
                      </p>
                    ) : null}
                    {selected.apple_maps_url ? (
                      <p>
                        <a
                          href={selected.apple_maps_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-teal-700 hover:underline"
                        >
                          Apple Maps
                        </a>
                      </p>
                    ) : null}
                    {selected.official_website ? (
                      <p>
                        <a
                          href={selected.official_website}
                          target="_blank"
                          rel="noreferrer"
                          className="text-teal-700 hover:underline"
                        >
                          Website
                        </a>
                      </p>
                    ) : null}
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-slate-800">Comments</h4>
                  {comments.length === 0 ? (
                    <p className="mt-2 text-sm text-slate-500">No comments yet.</p>
                  ) : (
                    <ul className="mt-2 space-y-2">
                      {comments.map((c) => (
                        <li
                          key={c.id}
                          className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm"
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div>
                              <p className="text-xs font-medium text-slate-500">
                                {c.created_by_display || "Someone"}
                                {c.parent_id ? " · reply" : ""}
                              </p>
                              <p className="mt-0.5 text-slate-800">{c.content}</p>
                            </div>
                            {(myRole === "administrator" || c.created_by_id === myTravelerId) &&
                            canComment ? (
                              <button
                                type="button"
                                onClick={() => onDeleteComment(c)}
                                className="text-xs text-red-600 hover:underline"
                              >
                                Delete
                              </button>
                            ) : null}
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                  {canComment ? (
                    <form onSubmit={onComment} className="mt-3 flex gap-2">
                      <input
                        value={commentText}
                        onChange={(e) => setCommentText(e.target.value)}
                        placeholder="Add a comment…"
                        className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-teal-600"
                      />
                      <button
                        type="submit"
                        className="rounded-md bg-teal-700 px-3 py-2 text-sm font-medium text-white hover:bg-teal-800"
                      >
                        Post
                      </button>
                    </form>
                  ) : (
                    <p className="mt-2 text-xs text-slate-400">
                      Commenters and above can discuss ideas.
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-sm text-slate-500">
                Select an idea to view details and comments.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
