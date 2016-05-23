create table submitted (
    id          integer primary key autoincrement not null,
    name        text,
    url         text,
    whensub     date,
    username    integer, FOREIGN KEY(username) references submitter(id)
);

create table chosen (
    id          integer primary key autoincrement not null,
    submitted_id integer, FOREIGN KEY(submitted_id) references submitted(id)
);

create table submitter (
  id integer primary key autoincrement not null,
  age text,
  name text
);
