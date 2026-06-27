from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from schema.database import Base



def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    image: Mapped[str | None] = mapped_column(Text, nullable=True)
    notif_token: Mapped[str | None] = mapped_column(Text, nullable=True)

    scale: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    offset_x: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    offset_y: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    last_conn: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    bot: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    requests: Mapped[list["Request"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
        foreign_keys="Request.user_id",
    )
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
        foreign_keys="Comment.user_id",
    )
    received_messages: Mapped[list["Message"]] = relationship(
        back_populates="target_user",
        cascade="all, delete-orphan",
        foreign_keys="Message.target_user_id",
    )
    sent_messages: Mapped[list["Message"]] = relationship(
        back_populates="sender_user",
        foreign_keys="Message.sender_user_id",
    )


class Request(Base):
    __tablename__ = "requests"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    media: Mapped[str | None] = mapped_column(Text, nullable=True)
    req_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    comment_nb: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    like_nb: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    signal_nb: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    author: Mapped["User"] = relationship(back_populates="requests", foreign_keys=[user_id])
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="request",
        cascade="all, delete-orphan",
        foreign_keys="Comment.request_id",
    )
    likes: Mapped[list["RequestLike"]] = relationship(
        back_populates="request",
        cascade="all, delete-orphan",
    )
    signals: Mapped[list["RequestSignal"]] = relationship(
        back_populates="request",
        cascade="all, delete-orphan",
    )
    interested_by: Mapped[list["UserInterestedRequest"]] = relationship(
        back_populates="request",
        cascade="all, delete-orphan",
    )


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    request_id: Mapped[str] = mapped_column(ForeignKey("requests.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    media: Mapped[str | None] = mapped_column(Text, nullable=True)
    req_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    comment_nb: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    like_nb: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    request: Mapped["Request"] = relationship(back_populates="comments", foreign_keys=[request_id])
    author: Mapped["User"] = relationship(back_populates="comments", foreign_keys=[user_id])
    likes: Mapped[list["CommentLike"]] = relationship(
        back_populates="comment",
        cascade="all, delete-orphan",
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    target_user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    sender_user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    media: Mapped[str | None] = mapped_column(Text, nullable=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    target_user: Mapped["User"] = relationship(back_populates="received_messages", foreign_keys=[target_user_id])
    sender_user: Mapped["User"] = relationship(back_populates="sent_messages", foreign_keys=[sender_user_id])


class RequestLike(Base):
    __tablename__ = "request_likes"
    __table_args__ = (UniqueConstraint("request_id", "user_id", name="uq_request_likes_request_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(ForeignKey("requests.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    request: Mapped["Request"] = relationship(back_populates="likes")
    user: Mapped["User"] = relationship()


class CommentLike(Base):
    __tablename__ = "comment_likes"
    __table_args__ = (UniqueConstraint("comment_id", "user_id", name="uq_comment_likes_comment_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    comment_id: Mapped[str] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    comment: Mapped["Comment"] = relationship(back_populates="likes")
    user: Mapped["User"] = relationship()


class RequestSignal(Base):
    __tablename__ = "request_signals"
    __table_args__ = (UniqueConstraint("request_id", "user_id", name="uq_request_signals_request_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(ForeignKey("requests.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    request: Mapped["Request"] = relationship(back_populates="signals")
    user: Mapped["User"] = relationship()


class UserInterestedRequest(Base):
    __tablename__ = "user_interested_requests"
    __table_args__ = (UniqueConstraint("user_id", "request_id", name="uq_user_interested_request"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    request_id: Mapped[str] = mapped_column(ForeignKey("requests.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    user: Mapped["User"] = relationship()
    request: Mapped["Request"] = relationship(back_populates="interested_by")


class UserBlock(Base):
    __tablename__ = "user_blocks"
    __table_args__ = (UniqueConstraint("user_id", "blocked_user_id", name="uq_user_block"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    blocked_user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    blocked_user: Mapped["User"] = relationship(foreign_keys=[blocked_user_id])

