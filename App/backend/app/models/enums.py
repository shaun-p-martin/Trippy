import enum


class TripmateRole(str, enum.Enum):
    viewer = "viewer"
    commenter = "commenter"
    contributor = "contributor"
    administrator = "administrator"


class InviteStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    revoked = "revoked"


ROLE_RANK = {
    TripmateRole.viewer: 1,
    TripmateRole.commenter: 2,
    TripmateRole.contributor: 3,
    TripmateRole.administrator: 4,
}


class IdeaType(str, enum.Enum):
    dining = "dining"
    entertainment_dining = "entertainment_dining"
    tour = "tour"
    guided_activity = "guided_activity"
    unguided_activity = "unguided_activity"
    sightseeing_landmark = "sightseeing_landmark"
    shopping = "shopping"
    supplies_provisions = "supplies_provisions"
    other = "other"


class ReactionType(str, enum.Enum):
    like = "like"
