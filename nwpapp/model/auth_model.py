from . import db


groups_users = db.Table(
    "groups_users",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("group_id", db.Integer, db.ForeignKey("ngroup.id")),
)


groups_sectors = db.Table(
    "groups_sectors",
    db.Column("group_id", db.Integer, db.ForeignKey("ngroup.id")),
    db.Column("sector_id", db.Integer, db.ForeignKey("nsector.id")),
)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    mobile = db.Column(db.String(20))
    email = db.Column(db.String(50))
    notification = db.Column(db.String(5))
    admin = db.Column(db.Boolean, default=False)
    superuser = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    groups = db.relationship(
        "Group",
        secondary=groups_users,
        lazy="subquery",
        backref=db.backref("user", lazy=True),
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<User(name='%s', admin='%s', active='%s')>" % (
            self.name,
            self.admin,
            self.active,
        )


class Group(db.Model):
    __tablename__ = "ngroup"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    sectors = db.relationship(
        "NSector",
        secondary=groups_sectors,
        lazy="subquery",
        backref=db.backref("group", lazy=True),
    )

    def __str__(self):
        return self.name


class NSector(db.Model):
    __tablename__ = "nsector"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name
